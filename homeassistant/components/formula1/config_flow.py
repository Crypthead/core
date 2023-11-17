"""Config flow for formula1 integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("show_calendar", default=True): bool,
        vol.Required("only_show_race_event", default=True): bool,
        vol.Required("show_driver_standings", default=True): bool,
        vol.Required("show_team_standings"): bool,
    }
)


async def validate_input(_: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    data["title"] = "formula1_config"
    return data


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for formula1."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except Exception as e:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception %s", e)
                errors["base"] = "Unexpected exception:" + str(e)
            else:
                _LOGGER.info("Received config: %s", str(info))
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
