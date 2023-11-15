# TODO import everything

# Need to
# 1. Get data from coordinator
# 2. Parse data to calendar events
# 3. Check that we don't add duplicate events, check if any dissapeared
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from homeassistant.components.calendar import CalendarEntity
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity


class MyCalendar(CoordinatorEntity, CalendarEntity):

    def __init__(self, coordinator):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, context=idx)
        self.idx = idx

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        #self._attr_is_on = self.coordinator.data['schedule']['2023']
        schedule = self.coordinator.test()

        # Notify UI about change of state
        self.async_write_ha_state()

    async def async_create_event(self, **kwargs) -> None:
        """Add a new event to calendar."""
        event = CalendarEvent()