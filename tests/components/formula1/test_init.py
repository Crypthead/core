"""Tests for Formula 1 integration initialization."""

from unittest.mock import patch

import pytest

from homeassistant.components.formula1 import DOMAIN, async_setup_entry
from homeassistant.core import HomeAssistant

pytestmark = pytest.mark.usefixtures("config_entry", "f1_coordinator")


@pytest.mark.asyncio
async def test_async_setup_entry(hass: HomeAssistant, config_entry, f1_coordinator):
    """Test for successful setup of formula1 integration."""
    # Patch the F1Coordinator to return the mock coordinator from the fixture
    with patch(
        "homeassistant.components.formula1.F1Coordinator", return_value=f1_coordinator
    ):
        # Call the async_setup_entry function
        result = await async_setup_entry(hass, config_entry)

        # Assert that the function returns True
        assert result is True

        # Verify if hass.data is updated
        assert config_entry.entry_id in hass.data[DOMAIN]
        assert hass.data[DOMAIN][config_entry.entry_id] is f1_coordinator


"""
@pytest.mark.asyncio
async def test_async_unload_entry(hass: HomeAssistant):
    mock_entry = MagicMock()
    mock_entry.entry_id = "test_entry"
    hass.data[DOMAIN] = {mock_entry.entry_id: MagicMock()}

    # Patch the async_unload_platforms method
    with patch('homeassistant.config_entries.ConfigEntries.async_unload_platforms', return_value=True):
        result = await async_unload_entry(hass, mock_entry)

        # Assert that the function returns True
        assert result == True

        # Ensure the entry is removed from hass.data
        assert mock_entry.entry_id not in hass.data[DOMAIN]



@pytest.mark.asyncio
async def test_async_remove_entry(hass: HomeAssistant):
    mock_entry = MagicMock()
    hass.data[DOMAIN] = {"initialized": True}

    # Call the async_remove_entry function
    await async_remove_entry(hass, mock_entry)

    # Assert that 'initialized' flag is set to False
    assert hass.data[DOMAIN]["initialized"] == False """
