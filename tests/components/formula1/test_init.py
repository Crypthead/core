"""Tests for Formula 1 integration initialization."""

from unittest.mock import patch

import pytest

from homeassistant.components.formula1 import (
    DOMAIN,
    async_setup_entry,
    async_unload_entry,
)
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

pytestmark = pytest.mark.usefixtures("config_entry", "f1_coordinator")

PLATFORMS: list[Platform] = [Platform.CALENDAR, Platform.SENSOR]


@pytest.mark.asyncio
async def test_async_setup_entry_multiple_calls(
    hass: HomeAssistant, config_entry, f1_coordinator
):
    """Test formula 1 integration initialization, and that it should fail if already initialized."""

    with patch(
        "homeassistant.components.formula1.F1Coordinator", return_value=f1_coordinator
    ), patch("homeassistant.components.formula1._LOGGER") as mock_logger:
        # First call - normal setup
        result = await async_setup_entry(hass, config_entry)
        assert result is True
        assert hass.data[DOMAIN][config_entry.entry_id] is f1_coordinator

        # Second call - should trigger warning
        second_result = await async_setup_entry(hass, config_entry)
        assert second_result is False

        # Check that warning log is called
        mock_logger.warning.assert_called_with(
            "Only a single Formula1 integration should be initialized"
        )

        # Check that 'initialized' flag is set correctly
        assert hass.data[DOMAIN].get("initialized", False) is True


@pytest.mark.asyncio
async def test_async_unload_entry(hass: HomeAssistant, config_entry, f1_coordinator):
    """Test that unloading works."""

    # Patch async_unload_platforms to return True
    with patch(
        "homeassistant.components.formula1.F1Coordinator", return_value=f1_coordinator
    ):
        await async_setup_entry(hass, config_entry)

    # Test successful unload
    with patch(
        "homeassistant.config_entries.ConfigEntries.async_unload_platforms",
        return_value=True,
    ) as mock_unload_platforms:
        result = await async_unload_entry(hass, config_entry)

        assert result is True
        mock_unload_platforms.assert_awaited_once_with(config_entry, PLATFORMS)
        assert config_entry.entry_id not in hass.data[DOMAIN]

    # Test unsuccessful unload
    with patch(
        "homeassistant.config_entries.ConfigEntries.async_unload_platforms",
        return_value=False,
    ) as mock_unload_platforms:
        result = await async_unload_entry(hass, config_entry)

        assert result is False
        # The entry would still be in hass.data if unload was unsuccessful
