"""Tests for F1 Coordinator."""

import os
import sys
from unittest.mock import patch

import pandas as pd
import pytest

from homeassistant.components.formula1.coordinator import F1Coordinator
from homeassistant.core import HomeAssistant

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)


class MockErgastMultiResponse:
    """Mocks ErgastMultiResponse wrapping a given DataFrame."""

    def __init__(self, data):
        """Wrap data in list."""
        # Assuming 'data' is the DataFrame you want to wrap
        self.content = [data]


async def async_mock_return(df):
    """Asynchronously returns a given DataFrame."""

    async def return_function():
        return df

    return return_function


def create_mock_schedule():
    """Create mock schedule DataFrame with predefined columns."""
    return pd.DataFrame(
        {
            "Location": [""],
            "OfficialEventName": [""],
            "EventDate": [""],
            "EventFormat": [""],
            "Session1DateUtc": [""],
            "Session2DateUtc": [""],
            "Session3DateUtc": [""],
            "Session4DateUtc": [""],
            "Session5DateUtc": [""],
            "F1ApiSupport": [""],
            "Session5": [""],
        }
    )


def create_mock_constructor_standings():
    """Create mock constructor standings with full column set."""
    return MockErgastMultiResponse(
        pd.DataFrame(
            {
                "position": [1, 2],
                "points": [100, 80],
                "constructorName": ["Team A", "Team B"],
                # Include other columns that your code will drop, if necessary
                "positionText": ["1", "2"],
                "wins": [5, 3],
                "constructorId": ["team_a", "team_b"],
                "constructorUrl": ["http://team-a.com", "http://team-b.com"],
                "constructorNationality": ["Country A", "Country B"],
            }
        )
    )


def create_mock_constructor_standings_after():
    """Create mock constructor standings with reduced columns."""
    return MockErgastMultiResponse(
        pd.DataFrame(
            {
                "position": [1, 2],
                "points": [100, 80],
                "constructorName": ["Team A", "Team B"],
            }
        )
    )


def create_mock_ergast_response(columns):
    """Create mock Ergast response with specified columns."""
    return MockErgastMultiResponse(pd.DataFrame(columns=columns))


@pytest.mark.asyncio
async def test_async_update_data(hass: HomeAssistant):
    """Test for fetching data."""

    # Mocking the Ergast object
    with patch("homeassistant.components.formula1.coordinator.Ergast") as mock_ergast:
        mock_ergast_instance = mock_ergast.return_value

        # Mocking fastf1 method "get_event_schedule"
        with patch(
            "homeassistant.components.formula1.coordinator.fastf1.get_event_schedule"
        ) as mock_get_event_schedule:
            mock_schedule_df = create_mock_schedule()
            mock_get_event_schedule.return_value = mock_schedule_df

            # Create mock DataFrames
            pd.DataFrame(
                data={
                    "mock_data": [
                        [
                            "position",
                            "points",
                            "givenName",
                            "familyName",
                            "constructorNames",
                        ]
                    ]
                }
            )
            # mock_constructor_standings_df = [pd.DataFrame(columns=["position", "points", "constructorName"])]
            mock_constructor_standings_df = create_mock_ergast_response(
                [
                    "position",
                    "points",
                    "constructorName",
                    "positionText",
                    "wins",
                    "constructorId",
                    "constructorUrl",
                    "constructorNationality",
                ]
            )
            pd.DataFrame(
                data={
                    "mock_data": [
                        ["position", "constructorName", "givenName", "familyName"]
                    ]
                }
            )
            pd.DataFrame(
                data={"mock_data": [["round", "raceName", "country", "raceDate"]]}
            )

            # Set up the mock return values
            # mock_ergast_instance.get_driver_standings.return_value = mock_driver_standings_df
            mock_ergast_instance.get_constructor_standings.return_value = (
                mock_constructor_standings_df
            )
            # mock_ergast_instance.get_last_race_results = AsyncMock(side_effect=await async_mock_return(mock_last_race_results_df))
            # mock_ergast_instance.get_last_race_info = AsyncMock(side_effect=await async_mock_return(mock_last_race_info_df))

            # ... similar setup for other methods

            # Mocking the logger

            coordinator = F1Coordinator(hass)
            data = await coordinator._async_update_data()

            # Verify the data
            # assert data["schedule"].equals(mock_schedule_df)
            assert data["schedule"].equals(mock_schedule_df)
            assert data["driver_standings"].equals(
                pd.DataFrame(columns=["position", "points", "constructorName"])
            )
            # print(type(data["constructor_standings"]))
            # assert data["constructor_standings"].equals(create_mock_ergast_response(["position", "points", "constructorName"]))
            # assert data["last_race_results"].equals(mock_last_race_results_df)
            # assert data["last_race_info"].equals(mock_last_race_info_df)


# print(create_mock_ergast_response(["HEllo", "hello"]).content)
