"""Example integration using DataUpdateCoordinator."""
# pylint: disable=broad-except
from datetime import date, timedelta
import logging

import fastf1

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class F1Coordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="Fast-F1 API",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(hours=12),
        )

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            # Get current year's schedule
            data = fastf1.get_event_schedule(
                date.today().year,
                include_testing=False,
                backend="fastf1",
                force_ergast=False,
            )

            data.drop(
                [
                    "Session1Date",
                    "Session2Date",
                    "Session3Date",
                    "Session4Date",
                    "Session5Date",
                ],
                axis=1,
                inplace=True,
            )

            return data

        except Exception:
            pass
