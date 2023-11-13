"""The formula1 integration."""
from __future__ import annotations
from homeassistant.components.formula1.calendar import MyCalendar
from homeassistant.components.formula1.coordinator import F1Coordinator

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN


# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.LIGHT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> bool:
    """Set up formula1 from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    # 1. Instantiate coordinator
    coordinator = F1Coordinator(hass)
    # Fetch initial data so we have data when entities subscribe
    #
    # If the refresh fails, async_config_entry_first_refresh will
    # raise ConfigEntryNotReady and setup will try again later
    #
    # If you do not want to retry setup on failure, use
    # coordinator.async_refresh() instead
    await coordinator.async_config_entry_first_refresh()

    # 2. Instantiate calendar & event entities
    async_add_entities(
        MyCalendar(coordinator, idx) for idx, ent in enumerate(coordinator.data)
    )
    # 3. Save those somewhere so they could be unloaded

    # TODO 1. Create API instance
    # TODO 2. Validate the API connection (and authentication)
    # TODO 3. Store an API object for your platforms to access
    # hass.data[DOMAIN][entry.entry_id] = MyApi(...)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
