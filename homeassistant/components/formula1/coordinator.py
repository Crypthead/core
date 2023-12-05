"""Formula 1 coordinator."""
# pylint: disable=broad-exception-caught
from datetime import timedelta
import logging

import fastf1
from fastf1.ergast import Ergast

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
import homeassistant.util.dt as dt_util

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

        Returns
        -------
        Dictionary containing 5 DataFrames:
        - schedule
        - driver_standings
        - constructor_standings
        - last_race_results
        - last_race_info

        """
        try:
            schedule = await self._get_schedule()

            driver_standings = await self._get_driver_standings()

            constructor_standings = await self._get_constructor_standings()

            last_race_results = await self._get_last_race_results()

            last_race_info = await self._get_last_race_info()

            data_dict = {
                "schedule": schedule,
                "driver_standings": driver_standings,
                "constructor_standings": constructor_standings,
                "last_race_results": last_race_results,
                "last_race_info": last_race_info,
            }

            _LOGGER.info("FETCH F1 DATA %s", data_dict)
            return data_dict

        except Exception as e:
            _LOGGER.error("Error fetching F1 data: %s", e)
            raise

    async def _get_schedule(self):
        """Get current year's schedule.

        Returns
        -------
        DataFrame with columns:

        EventName, RoundNumber, Country, Location, Session1, Session1Date,
        Session2, Session2Date,  Session3, Session3Date,  Session4, Session4Date,  Session5, Session5Date
        """

        schedule = await self.hass.async_add_executor_job(
            fastf1.get_event_schedule, dt_util.now().today().year
        )
        schedule = schedule[
            [
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
        ]

        # Remove Pre-season testing, by create a boolean mask.
        mask = schedule["Session5"] != "None"

        # Use the mask to select rows where Session5 is not 'None'
        return schedule[mask]

    async def _get_constructor_standings(self):
        """Get current constructor standings.

        Returns
        -------
        DataFrame with columns:

        position, points, constructorName
        """

        constructor_standings = await self.hass.async_add_executor_job(
            self.ergast.get_constructor_standings, "current"
        )

        constructor_standings = constructor_standings.content[0][
            ["position", "points", "constructorName"]
        ]

        return constructor_standings

    async def _get_driver_standings(self):
        """Get current driver standings.

        Returns
        -------
        DataFrame with columns:

        position, points, givenName, familyName, constructorNames
        """

        driver_standings = await self.hass.async_add_executor_job(
            self.ergast.get_driver_standings, "current"
        )

        driver_standings = driver_standings.content[0][
            ["position", "points", "givenName", "familyName", "constructorNames"]
        ]

        return driver_standings

    async def _get_last_race_results(self):
        """Get race results for the latest race.

        Returns
        -------
        DataFrame with columns:

        position (index), constructorName, givenName, familyName
        """

        _LOGGER.info("Retrieving results from last race")

        last_results = await self.hass.async_add_executor_job(
            self.ergast.get_race_results, "current", "last"
        )

        last_results = last_results.content[0][
            ["position", "constructorName", "givenName", "familyName"]
        ]

        # Convert position from double to int for a nicer viewing experience
        last_results = last_results.astype({"position": "int"})

        last_results.set_index("position", drop=True, inplace=True)

        return last_results

    async def _get_last_race_info(self):
        """Get information about the last race.

        Returns
        -------
        dictionary with keys:

        round (round number), raceName, country, raceDate
        """

        _LOGGER.info("Retrieving information about last race")

        last_race = await self.hass.async_add_executor_job(
            self.ergast.get_race_schedule, "current", "last"
        )

        last_race = last_race[["round", "raceName", "country", "raceDate"]]

        return last_race.to_dict(orient="records")[0]
