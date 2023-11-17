"""Support for F1 Calendar."""

from datetime import datetime, timedelta
import logging

import pandas as pd

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import homeassistant.util.dt as dt_util

from .const import DOMAIN
from .coordinator import F1Coordinator

_LOGGER = logging.getLogger(__name__)

# Need to
# 1. Get data from coordinator
# 2. Parse data to calendar events
# 3. Check that we don't add duplicate events, check if any disappeared


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up F1 based on a config entry."""

    if not entry.data["show_calendar"]:
        return

    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([Formula1Calendar(coordinator, entry)])


class Formula1Calendar(CoordinatorEntity[F1Coordinator], CalendarEntity):
    """Defines a F1 calendar."""

    _attr_has_entity_name = True
    _attr_name = "Formula 1"
    _attr_unique_id = "formula_1"

    def __init__(self, coordinator: F1Coordinator, entry: ConfigEntry) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, entry)
        self._event: CalendarEvent | None = None
        self.only_show_race_event = entry.data["only_show_race_event"]

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        return self._event

    def _create_calendar_event(
        self,
        event_name: str,
        session: str,
        round_num: str,
        start_date: datetime,
        location: str,
    ) -> CalendarEvent:
        """Create a calendar event from a session."""
        event = CalendarEvent(
            summary=event_name + ", " + session + ", " + round_num + " rounds",
            location=location,
            start=start_date,
            end=start_date + timedelta(hours=2),
        )

        return event

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        events: list[CalendarEvent] = []

        schedule = self.coordinator.data["schedule"]
        # Get all events within the time range
        for _, race in schedule.iterrows():
            session_dates = race[
                [
                    "Session5Date",
                    "Session4Date",
                    "Session3Date",
                    "Session2Date",
                    "Session1Date",
                ]
            ]

            for i, session_ts in enumerate(session_dates.values):
                session_date = session_ts.to_pydatetime()

                if (
                    not pd.isnull(session_ts)
                    and session_date >= start_date
                    and session_date + timedelta(hours=2) < end_date
                ):
                    events.append(
                        self._create_calendar_event(
                            event_name=str(race["EventName"]),
                            session=str(race["Session" + str(5 - i)]),
                            round_num=str(race["RoundNumber"]),
                            start_date=session_date,
                            location=str(race["Country"]),
                        )
                    )

                if self.only_show_race_event:
                    break

        return events

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        # Find the next upcoming event
        schedule = self.coordinator.data["schedule"]

        event_start = None
        upcoming_event = None

        for _, race in schedule.iterrows():
            session_dates = race[
                [
                    "Session5Date",
                    "Session4Date",
                    "Session3Date",
                    "Session2Date",
                    "Session1Date",
                ]
            ]

            for i, session_ts in enumerate(session_dates.values):
                session_date = session_ts.to_pydatetime()

                if (
                    not pd.isnull(session_ts)
                    and session_date >= dt_util.now()
                    and (event_start is None or session_date < event_start)
                ):
                    event_start = session_date
                    upcoming_event = self._create_calendar_event(
                        event_name=str(race["EventName"]),
                        session=str(race["Session" + str(5 - i)]),
                        round_num=str(race["RoundNumber"]),
                        start_date=session_date,
                        location=str(race["Country"]),
                    )

                if self.only_show_race_event:
                    break

        if upcoming_event is not None:
            self._event = upcoming_event

        super()._handle_coordinator_update()

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self._handle_coordinator_update()
