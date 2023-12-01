"""Test the formula1 calendar platform."""
from datetime import datetime, timedelta

import pytest

from homeassistant.components.formula1.calendar import Formula1Calendar
from homeassistant.core import HomeAssistant
import homeassistant.util.dt as dt_util

pytestmark = pytest.mark.usefixtures("config_entry", "coordinator", "f1_coordinator")


MOCK_DATETIME = dt_util.as_utc(datetime(2017, 11, 27, 0, 0, 0))


def test_create_calendar_event(hass: HomeAssistant, config_entry, f1_coordinator):
    """Test creating a calendar event."""
    calendar = Formula1Calendar(f1_coordinator, config_entry)

    event = calendar._create_calendar_event(
        "Test Event", "Session1", "1", MOCK_DATETIME, "Test Country"
    )

    assert event.summary == "Test Event, Session1, 1 rounds"
    assert event.location == "Test Country"
    assert event.start == MOCK_DATETIME
    assert event.end == MOCK_DATETIME + timedelta(hours=2)


@pytest.mark.asyncio
async def test_async_get_events_race(hass: HomeAssistant, config_entry, f1_coordinator):
    """Test async_get_events with only race events."""
    calendar = Formula1Calendar(f1_coordinator, config_entry)

    events = await calendar.async_get_events(
        hass, MOCK_DATETIME, MOCK_DATETIME + timedelta(days=10)
    )
    assert len(events) == 1


@pytest.mark.asyncio
async def test_async_get_events_no_events(
    hass: HomeAssistant, config_entry, f1_coordinator
):
    """Test async_get_events with no events."""
    calendar = Formula1Calendar(f1_coordinator, config_entry)

    events = await calendar.async_get_events(
        hass, MOCK_DATETIME + timedelta(days=1), MOCK_DATETIME + timedelta(days=2)
    )
    assert len(events) == 0


@pytest.mark.asyncio
async def test_async_get_events_all_events(
    hass: HomeAssistant, config_entry, f1_coordinator
):
    """Test async_get_events with all event types."""
    calendar = Formula1Calendar(f1_coordinator, config_entry)
    calendar.only_show_race_event = False

    events = await calendar.async_get_events(
        hass, MOCK_DATETIME, MOCK_DATETIME + timedelta(days=10)
    )
    assert len(events) == 5
