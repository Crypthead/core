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
        vol.Required("show_last_results", default=True): bool,
        vol.Required("show_last_winner", default=True): bool,
        vol.Required("show_driver_standings", default=True): bool,
        vol.Required("show_constructor_standings", default=True): bool,
        vol.Required("show_upcoming_race_weather", default=True): bool,
    }
)

STEP_CALENDAR_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("only_show_race_event", default=False): bool,
    }
)


async def validate_input(_: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Input validation to guarantee that at least one type of information is included.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    if not (
        data["show_calendar"]
        or data["show_driver_standings"]
        or data["show_constructor_standings"]
        or data["show_last_winner"]
        or data["show_last_results"]
        or data["show_upcoming_race_weather"]
    ):
        raise ValueError("Must select at least one type of information to show")

    data["title"] = "formula1_config"
    return data


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for formula1."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        super().__init__()
        self.data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle what information to be displayed in the integration."""
        # Check if already configured
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        errors: dict[str, str] = {}
        if user_input is not None:  # Check if the user already provided input
            try:
                info = await validate_input(self.hass, user_input)
            except Exception as e:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception %s", e)
                errors["base"] = "Unexpected exception:" + str(e)
            else:
                if info["show_calendar"]:
                    self.data = info
                    return await self.async_step_calendar()
                _LOGGER.info("Received config: %s", str(info))
                return self.async_create_entry(title=info["title"], data=user_input)

        # Ask frontend for input
        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_calendar(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Configure the calendar."""
        errors: dict[str, str] = {}
        if user_input is not None:
            self.data["only_show_race_event"] = user_input["only_show_race_event"]
            _LOGGER.info("Received config: %s", str(self.data))
            return self.async_create_entry(title=self.data["title"], data=self.data)

        # Ask frontend for input
        return self.async_show_form(
            step_id="calendar", data_schema=STEP_CALENDAR_DATA_SCHEMA, errors=errors
        )
