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
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([Formula1Calendar(coordinator, entry)])


class Formula1Calendar(CoordinatorEntity[F1Coordinator], CalendarEntity):
    """Defines a F1 calendar."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:delete-empty"
    _attr_name = "Formula 1"

    def __init__(self, coordinator: F1Coordinator, entry: ConfigEntry) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, entry)
        self._event: CalendarEvent | None = None

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        return self._event

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        events: list[CalendarEvent] = []

        schedule = self.coordinator.data
        # GET ALL EVENTS BETWEEN START AND END DATE
        for _, race in schedule.iterrows():
            session_dates = race[
                [
                    "Session1DateUtc",
                    "Session2DateUtc",
                    "Session3DateUtc",
                    "Session4DateUtc",
                    "Session5DateUtc",
                ]
            ]

            for i, session_ts in enumerate(session_dates.values):
                session_date = session_ts.date()
                if (
                    not pd.isnull(session_ts)
                    and session_date >= start_date.date()
                    and session_date + timedelta(hours=2) < end_date.date()
                ):
                    event_summary = (
                        str(race["RoundNumber"])
                        + " "
                        + str(race["Country"])
                        + " "
                        + str(race["EventName"])
                        + " "
                        + str(race["Session" + str(i + 1)])
                    )

                    events.append(
                        CalendarEvent(
                            summary=event_summary,
                            start=session_date,
                            end=session_date + timedelta(hours=2),
                        )
                    )

        return events

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        # FIND NEXT UPCOMING RACE
        schedule = self.coordinator.data

        event_start = None

        for _, race in schedule.iterrows():
            session_dates = race[
                [
                    "Session1DateUtc",
                    "Session2DateUtc",
                    "Session3DateUtc",
                    "Session4DateUtc",
                    "Session5DateUtc",
                ]
            ]

            for i, session_ts in enumerate(session_dates.values):
                session_date = session_ts.date()

                if (
                    not pd.isnull(session_ts)
                    and session_date >= dt_util.now().date()
                    and (event_start is None or session_date < event_start)
                ):
                    event_start = session_date

                    event_summary = (
                        str(race["RoundNumber"])
                        + " "
                        + str(race["Country"])
                        + " "
                        + str(race["EventName"])
                        + " "
                        + str(race["Session" + str(i + 1)])
                    )

                    break

        if event_start is not None and event_summary is not None:
            self._event = CalendarEvent(
                summary=event_summary,
                start=event_start,
                end=event_start + timedelta(hours=2),
            )

        super()._handle_coordinator_update()

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self._handle_coordinator_update()
