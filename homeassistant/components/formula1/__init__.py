"""The formula1 integration."""
from __future__ import annotations

# pylint: disable=W7421
# pylint: disable=W0718
import logging

from homeassistant.components.formula1.coordinator import F1Coordinator
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN

PLATFORMS: list[Platform] = [Platform.CALENDAR]


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up formula1 from a config entry."""
    coordinator = F1Coordinator(hass)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    if not hass.data[DOMAIN].get("initialized", False):
        hass.data[DOMAIN]["initialized"] = True
    else:
        _LOGGER.warning("Only a single Formula1 integration should be initialized")
        return False

    _LOGGER.debug("hass.data: %s", len(hass.data))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_remove_entry(hass: HomeAssistant, _: ConfigEntry) -> None:
    """Handle removal of an entry."""
    hass.data[DOMAIN]["initialized"] = False
