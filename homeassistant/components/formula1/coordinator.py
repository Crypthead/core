"""Formula 1 coordinator."""
# pylint: disable=broad-exception-caught
from datetime import timedelta
import logging

import fastf1
from fastf1.ergast import Ergast
import python_weather

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
        Dictionary containing the information:
        - schedule:                 dataframe
        - driver_standings:         dataframe
        - constructor_standings:    dataframe
        - last_race_results:        dataframe
        - last_race_info:           dict
        - next_weekend_weather:     [(str, str)]
        """

        _LOGGER.info("Fetching Formula 1 data")

        try:
            schedule = await self._get_schedule()

            driver_standings = await self._get_driver_standings()

            constructor_standings = await self._get_constructor_standings()

            last_race_results = await self._get_last_race_results()

            last_race_info = await self._get_last_race_info()

            next_weekend_weather = await self._get_weather_next_race_weekend()

            data_dict = {
                "schedule": schedule,
                "driver_standings": driver_standings,
                "constructor_standings": constructor_standings,
                "last_race_results": last_race_results,
                "last_race_info": last_race_info,
                "next_weekend_weather": next_weekend_weather,
            }

            _LOGGER.info("Successfully fetched Formula 1 data")
            _LOGGER.info("\n %s", data_dict)

            return data_dict

        except Exception as e:
            _LOGGER.error("Error fetching Formula 1 data: %s", e)
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

    async def _get_weather_next_race_weekend(self):
        """Get weather information for each session of the coming race weekend.

        Returns
        -------
        list with a tuple per session in the coming race weekend:

        [("(date) location and session", "weather information")]: [(String, String)]
        """

        # SETTING THIS TO TRUE WILL SET FAKE DATES IN THE NEXT RACE WEEKEND WEATHER SO WE ACTUALLY GET AN EVENT TO SHOW OFF
        # Should only be used (Set to True) for the presentation/demo on friday 15/12
        # Should be removed after friday
        fake_dates = True

        # Fetch the remaining events (race weekend)
        rem_events = await self.hass.async_add_executor_job(
            fastf1.get_events_remaining,
            dt_util.now().today()
            if not fake_dates
            else dt_util.parse_datetime("2023-6-1 1:00"),
        )

        # If we get no events, the season is over and we cannot check weather
        if len(rem_events) <= 0:
            return [("Season is over, no more race weekends", "-")]

        # We're only interested in the next event
        next_event = rem_events.iloc[0]

        # Get weather at location of event
        async with python_weather.Client(unit=python_weather.METRIC) as client:
            weather = await client.get(next_event[["Location"]].item())

        # List to be filled with session descriptions and corresponding session weather information
        sessions_weather = [None] * 5

        # Go through all sessions for the next event and find the closest forecast
        for i in range(1, 6):
            # Pick out each session's title and date
            session_title = (
                next_event[["EventName"]].item()
                + ": "
                + next_event[["Session" + str(i)]].item()
            )
            session_date = (
                next_event[["Session" + str(i) + "Date"]].item()
                if not fake_dates
                else (dt_util.now().today() + timedelta(days=(i - 1) // 2))
            )

            for forecast in weather.forecasts:
                if forecast.date == session_date.date():
                    self.find_closest_hourly_forecast(
                        sessions_weather, i, session_title, session_date, forecast
                    )

        return sessions_weather

    def find_closest_hourly_forecast(
        self, sessions_weather, i, session_title, session_date, forecast
    ):
        """Find the closest hourly forecast to a session.

        Pure side-effect function, changes values in the sessions_weather object
        """
        best_diff = 1000

        for h_forecast in forecast.hourly:
            h_min = h_forecast.time.hour * 60 + h_forecast.time.minute
            s_min = session_date.time().hour * 60 + session_date.time().minute

            new_diff = abs(h_min - s_min)

            # Find the forecast closest to the session start time
            if new_diff < best_diff:
                best_diff = new_diff

                sessions_weather[i - 1] = (
                    "(" + str(session_date.date()) + ") " + session_title,
                    str(h_forecast.description)
                    + ", "
                    + str(h_forecast.temperature)
                    + "°C",
                )
