from typing import Any, Coroutine, Callable

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .cvnet_entity import CvnetEntity


class CvnetStandbyPowerEntity(CvnetEntity, SwitchEntity):
    _set_state_function: Callable[[bool], Coroutine]

    def __init__(self, coordinator: DataUpdateCoordinator[dict[str, Any]], entity_description: SwitchEntityDescription,
                 coordinator_data_key: str):
        super().__init__(coordinator, entity_description, coordinator_data_key)

        data = coordinator.data[coordinator_data_key]
        self._set_state_function = data[entity_description.key]["set_state_function"]
        self._attr_is_on = data[entity_description.key]["value"]

    async def async_turn_on(self) -> None:
        self._attr_is_on = True
        self.async_write_ha_state()

        await self._set_state_function(True)

    async def async_turn_off(self) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()

        await self._set_state_function(False)

    @callback
    def _handle_coordinator_update(self):
        """Handle updated data from the coordinator."""
        data = self._data
        self._attr_is_on = data[self.entity_description.key]["value"]

        super()._handle_coordinator_update()
