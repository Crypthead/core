from unittest.mock import patch, AsyncMock
import pytest
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from homeassistant.components.formula1.coordinator import F1Coordinator

import asyncio



async def test_async_update_data_success():
    mock_hass = AsyncMock()
    coordinator = F1Coordinator(mock_hass)
    await coordinator.async_config_entry_first_refresh()

    data = await coordinator.async_request_refresh()

    print(data)

async def main():
    await test_async_update_data_success()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())