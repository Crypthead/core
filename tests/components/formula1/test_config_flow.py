"""Test the formula1 config flow."""
from unittest.mock import AsyncMock

import pytest

from homeassistant import data_entry_flow
from homeassistant.components.formula1.const import DOMAIN
from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from .conftest import MockConfigEntry

pytestmark = pytest.mark.usefixtures("mock_setup_entry")


async def test_form_no_calendar(
    hass: HomeAssistant, mock_setup_entry: AsyncMock
) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert not result["errors"]

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "show_calendar": False,
            "show_last_results": False,
            "show_last_winner": False,
            "show_driver_standings": False,
            "show_constructor_standings": True,
            "show_upcoming_race_weather": False,
        },
    )
    await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "formula1_config"
    assert result2["data"] == {
        "title": "formula1_config",
        "show_calendar": False,
        "show_last_results": False,
        "show_last_winner": False,
        "show_driver_standings": False,
        "show_constructor_standings": True,
        "show_upcoming_race_weather": False,
    }
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_with_calendar(
    hass: HomeAssistant, mock_setup_entry: AsyncMock
) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert not result["errors"]

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "show_calendar": True,
            "show_last_results": True,
            "show_last_winner": True,
            "show_driver_standings": True,
            "show_constructor_standings": True,
            "show_upcoming_race_weather": True,
        },
    )
    await hass.async_block_till_done()
    assert result2["type"] == FlowResultType.FORM
    assert not result2["errors"]

    result3 = await hass.config_entries.flow.async_configure(
        result2["flow_id"],
        {
            "only_show_race_event": False,
        },
    )

    assert result3["title"] == "formula1_config"
    assert result3["data"] == {
        "title": "formula1_config",
        "show_calendar": True,
        "show_last_results": True,
        "show_last_winner": True,
        "show_driver_standings": True,
        "show_constructor_standings": True,
        "show_upcoming_race_weather": True,
        "only_show_race_event": False,
    }
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_invalid_input(hass: HomeAssistant) -> None:
    """Test we handle invalid input."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "show_calendar": False,
            "show_last_results": False,
            "show_last_winner": False,
            "show_driver_standings": False,
            "show_constructor_standings": False,
            "show_upcoming_race_weather": False,
        },
    )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {
        "base": "Unexpected exception:Must select at least one type of information to show"
    }


async def test_integration_already_exists(hass: HomeAssistant) -> None:
    """Test we only allow a single config flow."""

    MockConfigEntry(
        domain=DOMAIN,
        data={},
    ).add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}, data={}
    )

    assert result.get("type") == data_entry_flow.FlowResultType.ABORT
    assert result.get("reason") == "single_instance_allowed"
