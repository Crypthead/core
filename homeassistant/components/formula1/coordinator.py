"""Example integration using DataUpdateCoordinator."""
# pylint: disable=broad-exception-caught
from datetime import date, timedelta
import logging

import fastf1
from fastf1.ergast import Ergast

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
            update_interval=timedelta(hours=1),
        )
        self.ergast = Ergast()

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            # Get current year's schedule
            schedule = await self.hass.async_add_executor_job(
                fastf1.get_event_schedule, date.today().year
            )

            schedule.drop(
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

            driver_standings = await self.hass.async_add_executor_job(
                self.ergast.get_driver_standings, date.today().year
            )

            driver_standings = driver_standings.content[0].drop(
                [
                    "wins",
                    "driverId",
                    "driverNumber",
                    "driverCode",
                    "driverUrl",
                    "dateOfBirth",
                    "driverNationality",
                    "constructorIds",
                    "constructorUrls",
                    "constructorNationalities",
                ],
                axis=1,
            )

            constructor_standings = await self.hass.async_add_executor_job(
                self.ergast.get_constructor_standings, date.today().year
            )

            constructor_standings = constructor_standings.content[0].drop(
                [
                    "positionText",
                    "wins",
                    "constructorId",
                    "constructorUrl",
                    "constructorNationality",
                ],
                axis=1,
            )

            data_dict = {
                "schedule": schedule,
                "driver_standings": driver_standings,
                "constructor_standings": constructor_standings,
            }

            _LOGGER.info("FETCH F1 DATA %s", schedule.to_string())
            _LOGGER.info("FETCH F1 DATA %s", driver_standings.to_string())
            _LOGGER.info("FETCH F1 DATA %s", constructor_standings.to_string())
            _LOGGER.info("FETCH F1 DATA %s", data_dict)
            return data_dict

        except Exception as e:
            _LOGGER.error("Error fetching F1 data: %s", e)
            raise
