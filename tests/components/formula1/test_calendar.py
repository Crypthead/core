"""Test the formula1 calendar platform."""
from datetime import timedelta

import pytest

from homeassistant.components.formula1.calendar import Formula1Calendar
from homeassistant.core import HomeAssistant

from .conftest import MOCK_DATETIME

pytestmark = pytest.mark.usefixtures("config_entry", "f1_coordinator")


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


@pytest.mark.asyncio
async def test_calendar_setup(hass: HomeAssistant, config_entry):
    """Test async_get_events with all event types."""
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    attributes = dict(hass.states.get("calendar.formula_1_calendar").attributes)

    assert attributes["message"] == "Test Event, Session5, 1 rounds"
    assert attributes["all_day"] is False
    assert attributes["location"] == "Test Country"
