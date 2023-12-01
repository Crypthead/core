"""Common fixtures for the formula1 tests."""
from collections.abc import Generator
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pandas as pd
from pandas import Timestamp
import pytest

from homeassistant.components.formula1.const import DOMAIN
from homeassistant.components.formula1.coordinator import F1Coordinator
from homeassistant.config_entries import SOURCE_USER
import homeassistant.util.dt as dt_util

from tests.common import MockConfigEntry


@pytest.fixture(name="config_entry")
def config_entry_fixture():
    """Create hass config_entry fixture."""
    data = {
        "show_calendar": True,
        "show_last_results": True,
        "show_last_winner": True,
        "show_driver_standings": True,
        "show_constructor_standings": True,
        "only_show_race_event": True,
        "title": "formula1_config",
    }
    return MockConfigEntry(
        version=1,
        domain=DOMAIN,
        title="",
        data=data,
        source=SOURCE_USER,
        entry_id=1,
    )


MOCK_DATETIME = dt_util.as_utc(datetime(2017, 11, 27, 0, 0, 0))


@pytest.fixture(name="f1_coordinator")
async def f1_coordinator(hass):
    """Mock F1 Coordinator."""
    # Mock the API methods
    with patch.object(
        F1Coordinator, "_get_schedule", new_callable=AsyncMock
    ) as mock_schedule:
        # Set return values for the mock methods
        mock_schedule.return_value = pd.DataFrame(
            {
                "EventName": ["Test Event"],
                "Session1Date": [Timestamp(MOCK_DATETIME + timedelta(days=1))],
                "Session2Date": [Timestamp(MOCK_DATETIME + timedelta(days=2))],
                "Session3Date": [Timestamp(MOCK_DATETIME + timedelta(days=3))],
                "Session4Date": [Timestamp(MOCK_DATETIME + timedelta(days=3, hours=5))],
                "Session5Date": [Timestamp(MOCK_DATETIME + timedelta(days=5))],
                "Session1": ["Session1"],
                "Session2": ["Session2"],
                "Session3": ["Session3"],
                "Session4": ["Session4"],
                "Session5": ["Session5"],
                "RoundNumber": ["1"],
                "Country": ["Test Country"],
            }
        )
        # mock_driver_standings.return_value = ...
        # mock_constructor_standings.return_value = ...
        # mock_last_race_results.return_value = ...
        # mock_last_race_info.return_value = ...

        # Initialize the coordinator
        coordinator = F1Coordinator(hass)

        # Use async_config_entry_first_refresh for initial data retrieval
        await coordinator.async_config_entry_first_refresh()

        yield coordinator


@pytest.fixture(name="coordinator")
def coordinator_fixtore():
    """Create an F1 coordinator fixture."""

    class MockF1Coordinator:
        data = {
            "schedule": pd.DataFrame(
                [
                    {
                        "EventName": "Test Event",
                        "Session1Date": Timestamp(MOCK_DATETIME + timedelta(days=1)),
                        "Session2Date": Timestamp(MOCK_DATETIME + timedelta(days=2)),
                        "Session3Date": Timestamp(MOCK_DATETIME + timedelta(days=3)),
                        "Session4Date": Timestamp(
                            MOCK_DATETIME + timedelta(days=3, hours=5)
                        ),
                        "Session5Date": Timestamp(MOCK_DATETIME + timedelta(days=5)),
                        "Session5": "Session5",
                        "Session4": "Session4",
                        "Session3": "Session3",
                        "Session2": "Session2",
                        "Session1": "Session1",
                        "RoundNumber": "1",
                        "Country": "Test Country",
                    }
                ]
            )
        }

    return MockF1Coordinator()


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock, None, None]:
    """Override async_setup_entry."""
    with patch(
        "homeassistant.components.formula1.async_setup_entry", return_value=True
    ) as mock_setup_entry:
        yield mock_setup_entry
