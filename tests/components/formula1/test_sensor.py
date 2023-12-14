"""Test the formula1 calendar platform."""
from datetime import datetime

import pytest

from homeassistant.components.formula1 import DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
import homeassistant.util.dt as dt_util

from tests.common import MockConfigEntry

pytestmark = pytest.mark.usefixtures("f1_coordinator")


MOCK_DATETIME = dt_util.as_utc(datetime(2017, 11, 27, 0, 0, 0))


async def test_correct_sensors_setup(hass: HomeAssistant):
    """Test that the sensor correctly parses the configuration."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Idk lol",
        unique_id="0123456",
        data={
            "show_driver_standings": True,
            "show_constructor_standings": False,
            "show_last_winner": False,
            "show_last_results": False,
            "show_upcoming_race_weather": True,
            "name": "Home",
        },
    )

    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state == ConfigEntryState.LOADED
    sensors = hass.states.async_all("sensor")
    assert len(sensors) == 2

    assert hass.states.get("sensor.formula_1_drivers_standings") is not None
    assert hass.states.get("sensor.formula_1_constructors_standings") is None
    assert hass.states.get("sensor.formula_1_last_race_winner") is None
    assert hass.states.get("sensor.formula_1_last_race_results") is None
    assert hass.states.get("sensor.formula_1_upcoming_weather") is not None


async def test_drivers_standings_sensor(hass: HomeAssistant):
    """Test that the driver standings sensor correctly loads driver standings from the mocked coordinator."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Idk lol",
        unique_id="0123456",
        data={
            "show_driver_standings": True,
            "show_constructor_standings": False,
            "show_last_winner": False,
            "show_last_results": False,
            "show_upcoming_race_weather": False,
            "name": "Home",
        },
    )

    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.formula_1_drivers_standings")
    assert state is not None
    assert ("1 - Hamilton", 25) in state.as_dict()["attributes"].items()


async def test_constructors_standings_sensor(hass: HomeAssistant):
    """Test that the constructor standings sensor correctly loads driver standings from the mocked coordinator."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Idk lol",
        unique_id="0123456",
        data={
            "show_driver_standings": False,
            "show_constructor_standings": True,
            "show_last_winner": False,
            "show_last_results": False,
            "show_upcoming_race_weather": False,
            "name": "Home",
        },
    )

    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.formula_1_constructors_standings")
    assert state is not None
    assert ("1 - Ferrari", 25) in state.as_dict()["attributes"].items()
    assert ("2 - Williams", 18) in state.as_dict()["attributes"].items()


async def test_last_winner_sensor(hass: HomeAssistant):
    """Test that the last winner sensor correctly loads driver standings from the mocked coordinator."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Idk lol",
        unique_id="0123456",
        data={
            "show_driver_standings": False,
            "show_constructor_standings": False,
            "show_last_winner": True,
            "show_last_results": False,
            "show_upcoming_race_weather": False,
            "name": "Home",
        },
    )

    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.formula_1_last_race_winner")

    assert ("round", 1) in state.as_dict()["attributes"].items()
    assert ("raceName", "Australian Grand Prix") in state.as_dict()[
        "attributes"
    ].items()
    assert ("country", "Australia") in state.as_dict()["attributes"].items()


async def test_last_results_sensor(hass: HomeAssistant):
    """Test that the last results sensor correctly loads driver standings from the mocked coordinator."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Idk lol",
        unique_id="0123456",
        data={
            "show_driver_standings": False,
            "show_constructor_standings": False,
            "show_last_winner": False,
            "show_last_results": True,
            "show_upcoming_race_weather": False,
            "name": "Home",
        },
    )

    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.formula_1_last_race_results")
    assert state is not None
    assert (0, "Vettel") in state.as_dict()["attributes"].items()


async def test_race_weather_sensor(hass: HomeAssistant):
    """Test that the race weather sensor correctly loads the weather from ."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test weather sensor",
        unique_id="0123456",
        data={
            "show_driver_standings": False,
            "show_constructor_standings": False,
            "show_last_winner": False,
            "show_last_results": False,
            "show_upcoming_race_weather": True,
            "name": "Home",
        },
    )

    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.formula_1_upcoming_weather")
    assert state is not None
    assert (
        "(2023-12-8) Swedish Grand Prix: Practice 1",
        "Snowy, -5°C",
    ) in state.as_dict()["attributes"].items()
