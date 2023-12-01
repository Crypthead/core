"""Common fixtures for the formula1 tests."""
from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest

from homeassistant.components.formula1.const import DOMAIN
from homeassistant.config_entries import SOURCE_USER

from tests.common import MockConfigEntry


@pytest.fixture(name="config_entry")
def config_entry_fixture():
    """Create hass config_entry fixture."""
    data = {
        "show_calendar": True,
        "show_last_results": True,
        "show_last_winner": True,
        "show_driver_standings": True,
        "show_constructor_standings": True,
        "only_show_race_event": True,
        "title": "formula1_config",
    }
    return MockConfigEntry(
        version=1,
        domain=DOMAIN,
        title="",
        data=data,
        source=SOURCE_USER,
        entry_id=1,
    )


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock, None, None]:
    """Override async_setup_entry."""
    with patch(
        "homeassistant.components.formula1.async_setup_entry", return_value=True
    ) as mock_setup_entry:
        yield mock_setup_entry
