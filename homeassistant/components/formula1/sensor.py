"""Support for formula1 sensor."""
from __future__ import annotations

from enum import Enum
import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import F1Coordinator

_LOGGER = logging.getLogger(__name__)


class SensorType(Enum):
    """Specifies what information the F1Sensor displays."""

    DRIVER_STANDINGS = 1
    CONSTRUCTOR_STANDINGS = 2
    LAST_RACE_WINNER = 3
    LAST_RACE_FINAL_POSITIONS = 4


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities_to_add = []

    if entry.data.get("show_driver_standings", False):
        entities_to_add.append(
            F1Sensor(coordinator, entry, SensorType.DRIVER_STANDINGS)
        )

    if entry.data.get("show_constructor_standings", False):
        entities_to_add.append(
            F1Sensor(coordinator, entry, SensorType.CONSTRUCTOR_STANDINGS)
        )

    if entry.data.get("show_last_winner", False):
        entities_to_add.append(
            F1Sensor(coordinator, entry, SensorType.LAST_RACE_WINNER)
        )

    if entry.data.get("show_last_results", False):
        entities_to_add.append(
            F1Sensor(coordinator, entry, SensorType.LAST_RACE_FINAL_POSITIONS)
        )

    if entities_to_add:
        async_add_entities(entities_to_add)


class F1Sensor(CoordinatorEntity[F1Coordinator], SensorEntity):
    """Implementation of the F1Sensor sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: F1Coordinator,
        _: ConfigEntry,
        sensor_type: SensorType,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.sensor_type = sensor_type
        self._attr_unique_id = sensor_type.name

        self.last_date_changed = None
        self.last_winner = ""

    @property
    def native_value(self) -> str:
        """Returns the last time the standings have changed or the last winner."""
        if self.sensor_type == SensorType.LAST_RACE_WINNER:
            return self.last_winner
        if self.last_date_changed:
            return self.last_date_changed.strftime("%Y-%m-%d")
        return ""

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        self.last_date_changed = self.coordinator.data["last_race_info"]["raceDate"]

        match self.sensor_type:
            case SensorType.DRIVER_STANDINGS:
                data = self.coordinator.data["driver_standings"]
                name_column = "familyName"
                result_column = "points"
            case SensorType.CONSTRUCTOR_STANDINGS:
                data = self.coordinator.data["constructor_standings"]
                name_column = "constructorName"
                result_column = "points"
            case SensorType.LAST_RACE_FINAL_POSITIONS:
                data = self.coordinator.data["last_race_results"]
                name_column = "familyName"
            case SensorType.LAST_RACE_WINNER:
                self.last_winner = self.coordinator.data["last_race_results"][
                    "familyName"
                ].iloc[0]
                return self.coordinator.data["last_race_info"]

        attrs = {}
        if self.sensor_type in [
            SensorType.DRIVER_STANDINGS,
            SensorType.CONSTRUCTOR_STANDINGS,
        ]:
            for position, standing in data.iterrows():
                attrs[f"{position + 1} - {standing[name_column]}"] = standing[
                    result_column
                ]

        else:
            for position, standing in data.iterrows():
                attrs[position] = standing[name_column]

        return attrs

    @property
    def name(self) -> str:
        """Name of the entity."""
        match self.sensor_type:
            case SensorType.DRIVER_STANDINGS:
                return "Formula 1 drivers standings"
            case SensorType.CONSTRUCTOR_STANDINGS:
                return "Formula 1 constructors standings"
            case SensorType.LAST_RACE_WINNER:
                return "Formula 1 last race winner"
            case SensorType.LAST_RACE_FINAL_POSITIONS:
                return "Formula 1 last race results"
            case _:
                return ""

    @property
    def icon(self) -> str | None:
        """Icon of the entity."""
        return "mdi:go-kart"
