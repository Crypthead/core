"""Support for formula1 sensor."""
from __future__ import annotations

import datetime
import logging
from typing import Any, Union

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import homeassistant.util.dt as dt_util

from .const import DOMAIN
from .coordinator import F1Coordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    if entry.data["show_driver_standings"]:
        async_add_entities([F1Sensor(coordinator, entry, True)])

    if entry.data["show_constructor_standings"]:
        async_add_entities([F1Sensor(coordinator, entry, False)])


class F1Sensor(CoordinatorEntity[F1Coordinator], SensorEntity):
    """Implementation of the F1Sensor sensor."""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(
        self,
        coordinator: F1Coordinator,
        entry: ConfigEntry,
        driver_else_constructor: bool,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

        unique_str = "driver" if driver_else_constructor else "constructor"
        name = f"Formula 1 {unique_str} standings"

        self._attr_unique_id = f"{entry.entry_id}_{unique_str}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=name,
        )

        self.driver_else_constructor = driver_else_constructor
        self.last_date_changed = dt_util.now().date()
        self.last_standings: Union[None, dict[str, Any]] = None

    @property
    def native_value(self) -> datetime.date:
        """Returns the last time the standings have changed."""
        return self.last_date_changed

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if self.driver_else_constructor:
            data = self.coordinator.data["driver_standings"]
            name_column = "familyName"
        else:
            data = self.coordinator.data["constructor_standings"]
            name_column = "constructorName"

        attrs = {}
        for position, standing in data.iterrows():
            attrs[f"{position + 1} - {standing[name_column]}"] = standing["points"]

        if self.last_standings != attrs:
            self.last_date_changed = dt_util.now().date()
            self.last_standings = attrs

        return attrs
