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


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up F1 based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Only add calendar if user has enabled it
    if entry.data["show_calendar"]:
        async_add_entities([Formula1Calendar(coordinator, entry)])


class Formula1Calendar(CoordinatorEntity[F1Coordinator], CalendarEntity):
    """Defines a F1 calendar entity."""

    _attr_has_entity_name = True
    _attr_name = "Formula 1 calendar"
    _attr_unique_id = "formula_1_calendar"

    def __init__(self, coordinator: F1Coordinator, entry: ConfigEntry) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, entry)
        self._event: CalendarEvent | None = None

        # Only show race events or show all events
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

        # Get the schedule from the coordinator
        schedule = self.coordinator.data["schedule"]

        # Iterate through schedule to get all events within the time range
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

            # Iterate through the sessions
            for i, session_ts in enumerate(session_dates.values):
                session_date = session_ts.to_pydatetime()

                # Check if the session is within the time range
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
                            start_date=dt_util.now(),
                            location="Nowhere",
                        )
                    )

                # Race events is Session5
                if self.only_show_race_event:
                    break

        events = [
            self._create_calendar_event(
                event_name="Demo Grand Prix",
                session="Race",
                round_num="1",
                start_date=dt_util.now() + timedelta(minutes=30),
                location="Nowhere",
            )
        ]

        return events

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator. Find the next upcoming event."""

        # Get the schedule from the coordinator
        schedule = self.coordinator.data["schedule"]

        event_start = None
        upcoming_event = None

        # Iterate through schedule to get next upcoming event
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

            # Iterate through the sessions
            for i, session_ts in enumerate(session_dates.values):
                session_date = session_ts.to_pydatetime()

                # Check if the session is closer than the current upcoming event
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

                # Race events is Session5
                if self.only_show_race_event:
                    break

        # Set the upcoming event
        if upcoming_event is not None:
            self._event = upcoming_event

        self._event = self._create_calendar_event(
            event_name="Demo Grand Prix",
            session="Race",
            round_num="1",
            start_date=dt_util.now() + timedelta(minutes=30),
            location="Nowhere",
        )

        super()._handle_coordinator_update()

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self._handle_coordinator_update()

    @property
    def icon(self) -> str | None:
        """Icon of the entity."""
        return "mdi:go-kart-track"
