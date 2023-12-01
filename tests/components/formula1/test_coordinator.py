"""Tests for F1 Coordinator."""

import os
import sys
from unittest.mock import AsyncMock, patch

import pandas as pd
import pytest

from homeassistant.components.formula1.coordinator import F1Coordinator
from homeassistant.core import HomeAssistant

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)


class MockErgastMultiResponse:
    """Mocks ErgastMultiResponse by wrapping a given DataFrame."""

    def __init__(self, data):
        """Wrap data in list."""
        # Assuming 'data' is the DataFrame you want to wrap
        self.content = [data]


def create_mock_ergast_response(columns):
    """Create mock Ergast response with specified columns."""
    return MockErgastMultiResponse(pd.DataFrame(columns=columns))


def create_mock_schedule():
    """Create mock schedule DataFrame with predefined columns."""
    columns = [
        "RoundNumber",
        "EventName",
        "Country",
        "Location",
        "Session1",
        "Session1Date",
        "Session2",
        "Session2Date",
        "Session3",
        "Session3Date",
        "Session4",
        "Session4Date",
        "Session5",
        "Session5Date",
    ]

    # Create an empty DataFrame with these columns
    return pd.DataFrame(columns=columns)


def create_mock_constructor_standings():
    """Create mock constructor standings with partial column set."""
    return create_mock_ergast_response(
        [
            "position",
            "points",
            "constructorName",
            "wins",  # Ensure "wins" get filtered
        ]
    )


def create_mock_driver_standings():
    """Create mock driver standings with partial column set."""
    return create_mock_ergast_response(
        ["position", "points", "givenName", "familyName", "constructorNames", "wins"]
    )


def create_mock_last_race_results():
    """Create mock last race results with partial column set."""
    return create_mock_ergast_response(
        ["position", "constructorName", "givenName", "familyName", "wins"]
    )


def create_mock_last_race_info():
    """Create mock last race info with partial column set and fake data."""
    data = {
        "round": [1, 2],  # Example round numbers
        "raceName": ["Grand Prix A", "Grand Prix B"],  # Example race names
        "country": ["Country A", "Country B"],  # Example countries
        "raceDate": ["2023-01-01", "2023-02-01"],  # Example dates
        "wins": [3, 1],  # Example win counts
    }
    return pd.DataFrame(data)


@pytest.mark.asyncio
async def test_async_update_data(hass: HomeAssistant):
    """Test for fetching data."""

    # Mocking the Ergast object
    with patch("homeassistant.components.formula1.coordinator.Ergast") as mock_ergast:
        mock_ergast_instance = mock_ergast.return_value

        # Mocking fastf1 method "get_event_schedule()"
        with patch(
            "homeassistant.components.formula1.coordinator.fastf1.get_event_schedule"
        ) as mock_get_event_schedule:
            mock_get_event_schedule.return_value = create_mock_schedule()

            # Set up the mock return values for each API function call
            mock_ergast_instance.get_constructor_standings.return_value = (
                create_mock_constructor_standings()
            )
            mock_ergast_instance.get_driver_standings.return_value = (
                create_mock_driver_standings()
            )
            mock_ergast_instance.get_race_results.return_value = (
                create_mock_last_race_results()
            )
            mock_ergast_instance.get_race_schedule.return_value = (
                create_mock_last_race_info()
            )

            # Fetch data from coordinator
            coordinator = F1Coordinator(hass)
            data = await coordinator._async_update_data()

            # Verify the data has been fetched and filtered

            assert data["schedule"].equals(create_mock_schedule())

            assert data["constructor_standings"].equals(
                pd.DataFrame(columns=["position", "points", "constructorName"])
            )

            assert data["driver_standings"].equals(
                pd.DataFrame(
                    columns=[
                        "position",
                        "points",
                        "givenName",
                        "familyName",
                        "constructorNames",
                    ]
                )
            )

            assert data["last_race_results"].equals(
                pd.DataFrame(columns=["constructorName", "givenName", "familyName"])
            )

            expected_keys = {"round", "raceName", "country", "raceDate"}
            actual_keys = set(data["last_race_info"].keys())
            assert (
                actual_keys == expected_keys
            ), "The keys in last_race_info do not match the expected keys."


@pytest.mark.asyncio
async def test_async_update_data_exception(hass: HomeAssistant):
    """Test for coordinator data fethcing exceptions."""

    with patch.object(
        F1Coordinator,
        "_get_schedule",
        new=AsyncMock(side_effect=Exception("Test Exception")),
    ):
        f1_coordinator = F1Coordinator(hass)
        with pytest.raises(Exception) as excinfo:
            await f1_coordinator.async_config_entry_first_refresh()
        assert "Test Exception" in str(excinfo.value)
