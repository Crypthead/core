"""Tests for F1 Coordinator."""

import os
import sys
from unittest.mock import AsyncMock, patch

import pytest

from homeassistant.components.formula1.coordinator import F1Coordinator
from homeassistant.core import HomeAssistant

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)


@pytest.mark.asyncio
async def test_async_update_data(hass: HomeAssistant):
    """Test for fetching data."""
    # Mocking the external dependencies
    with patch("homeassistant.components.formula1.coordinator.Ergast") as mock_ergast:
        mock_ergast_instance = mock_ergast.return_value
        mock_ergast_instance._get_schedule = AsyncMock(return_value="mock_schedule")
        mock_ergast_instance._get_driver_standings = AsyncMock(
            return_value="mock_driver_standings"
        )
        mock_ergast_instance._get_constructor_standings = AsyncMock(
            return_value="mock_constructor_standings"
        )
        mock_ergast_instance._get_last_race_results = AsyncMock(
            return_value="mock_last_race_results"
        )
        mock_ergast_instance._get_last_race_info = AsyncMock(
            return_value="mock_last_race_info"
        )

        # Mocking the logger
        with patch(
            "homeassistant.components.formula1.coordinator._LOGGER"
        ) as mock_logger:
            coordinator = F1Coordinator(hass)  # Mock the hass object as needed
            data = await coordinator._async_update_data()

            # Verify the data
            assert data == {
                "schedule": "mock_schedule",
                "driver_standings": "mock_driver_standings",
                "constructor_standings": "mock_constructor_standings",
                "last_race_results": "mock_last_race_results",
                "last_race_info": "mock_last_race_info",
            }

            # Verify if the log message was called
            mock_logger.info.assert_called_once()
