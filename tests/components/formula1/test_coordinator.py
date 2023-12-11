"""Tests for F1 Coordinator."""

import os
import sys
from unittest.mock import AsyncMock, patch

import pandas as pd
import pytest

from homeassistant.components.formula1.coordinator import F1Coordinator
from homeassistant.core import HomeAssistant
import homeassistant.util.dt as dt_util

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


def create_get_events_no_remaining():
    """Create mock for remaining events (no events)."""
    columns = [
        "EventName",
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

    # Create an DataFrame with the data
    return pd.DataFrame(columns=columns)


def create_get_events_remaining():
    """Create mock for remaining events (only one event)."""
    data = {
        "EventName": ["Swedish Grand Prix"],
        "Location": ["Gotland"],
        "Session1": ["Practice 1"],
        "Session1Date": [pd.Timestamp(2023, 4, 11, 14, 0)],
        "Session2": ["Practice 2"],
        "Session2Date": [pd.Timestamp(2023, 4, 11, 15, 0)],
        "Session3": ["Practice 3"],
        "Session3Date": [pd.Timestamp(2023, 4, 11, 16, 0)],
        "Session4": ["Qualifying"],
        "Session4Date": [pd.Timestamp(2023, 4, 11, 17, 0)],
        "Session5": ["Race"],
        "Session5Date": [pd.Timestamp(2023, 4, 11, 18, 0)],
    }

    # Create an DataFrame with the data
    return pd.DataFrame(data)


class Client:
    """Mock weather client."""

    async def __aenter__(self, *args):
        """Mock."""
        return self

    async def __aexit__(self, *args):
        """Mock."""
        pass

    async def get(self, *args):
        """Mock."""
        return Weather()


class Weather:
    """Mock Weather object."""

    forecasts = []

    def __init__(self):
        """Mock."""
        self.forecasts = [DailyForecast(), DailyForecast(), DailyForecast()]


class DailyForecast:
    """Mock Daily Forecast."""

    date = None
    hourly = None

    def __init__(self):
        """Mock."""
        self.date = dt_util.parse_date("2023-04-11")
        self.hourly = [
            HourlyForecast(14),
            HourlyForecast(15),
            HourlyForecast(16),
            HourlyForecast(17),
            HourlyForecast(18),
        ]


class HourlyForecast:
    """Mock Hourly Forecast."""

    time = None
    description = None
    temperature = None

    def __init__(self, hour):
        """Mock."""
        self.time = dt_util.parse_datetime("2023-04-11 " + str(hour) + ":00")
        self.description = "Snowy"
        # set the temperature to a negative value, that depends on the hour
        self.temperature = 10 - hour


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
        ) as mock_get_event_schedule, patch(
            "homeassistant.components.formula1.coordinator.fastf1.get_events_remaining"
        ) as mock_get_events_remaining, patch(
            "homeassistant.components.formula1.coordinator.python_weather.Client"
        ) as mock_get_weather:
            mock_get_event_schedule.return_value = create_mock_schedule()
            mock_get_events_remaining.return_value = create_get_events_remaining()
            mock_get_weather.return_value = Client()

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

            assert data["next_weekend_weather"] == [
                ("(2023-04-11) Swedish Grand Prix: Practice 1", "Snowy, -4C°"),
                ("(2023-04-11) Swedish Grand Prix: Practice 2", "Snowy, -5C°"),
                ("(2023-04-11) Swedish Grand Prix: Practice 3", "Snowy, -6C°"),
                ("(2023-04-11) Swedish Grand Prix: Qualifying", "Snowy, -7C°"),
                ("(2023-04-11) Swedish Grand Prix: Race", "Snowy, -8C°"),
            ]


@pytest.mark.asyncio
async def test_coordinator_next_event_season_over(hass: HomeAssistant):
    """Test for coordinator getting weather for the next race weekend, when there are no more race weekends in the season."""

    # Mocking fastf1 method "get_event_schedule()"
    with patch(
        "homeassistant.components.formula1.coordinator.fastf1.get_events_remaining"
    ) as mock_get_events_remaining, patch(
        "homeassistant.components.formula1.coordinator.python_weather.Client"
    ) as mock_get_weather:
        mock_get_events_remaining.return_value = create_get_events_no_remaining()
        mock_get_weather.return_value = Client()

        # Fetch data from coordinator
        coordinator = F1Coordinator(hass)
        data = await coordinator._async_update_data()

        assert data["next_weekend_weather"] == [
            ("Season is over, no more race weekends", "-")
        ]


@pytest.mark.asyncio
async def test_async_update_data_exception(hass: HomeAssistant):
    """Test for coordinator data fethcing exceptions."""

    with patch.object(
        F1Coordinator,
        "_get_schedule",
        new=AsyncMock(side_effect=Exception("Error fetching Schedule")),
    ):
        f1_coordinator = F1Coordinator(hass)

        # Call coordinator and wait for exception
        with pytest.raises(Exception) as excinfo:
            await f1_coordinator.async_config_entry_first_refresh()

        assert "Error fetching Schedule" in str(excinfo.value)
