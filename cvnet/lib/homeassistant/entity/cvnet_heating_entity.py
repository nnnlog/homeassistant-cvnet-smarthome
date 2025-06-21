from typing import Any, Coroutine, Callable

from homeassistant.components.climate import ClimateEntity, ClimateEntityDescription, ClimateEntityFeature, HVACMode, \
    HVACAction
from homeassistant.const import UnitOfTemperature
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .cvnet_entity import CvnetEntity


class CvnetHeatingEntity(CvnetEntity, ClimateEntity):
    _set_state_function: Callable[[bool, float], Coroutine]

    def __init__(self, coordinator: DataUpdateCoordinator[dict[str, Any]], entity_description: ClimateEntityDescription,
                 coordinator_data_key: str):
        super().__init__(coordinator, entity_description, coordinator_data_key)

        data = coordinator.data[coordinator_data_key]
        self._set_state_function = data[entity_description.key]["set_state_function"]

        self._attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
        self._attr_hvac_mode = data[entity_description.key]["state_mode"]

        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE

        self._attr_target_temperature_step = 1
        self._attr_target_temperature_low = 5
        self._attr_target_temperature_high = 40

        self._attr_target_temperature = data[entity_description.key]["target_temperature"]
        self._attr_current_temperature = data[entity_description.key]["current_temperature"]

        self._attr_hvac_action = data[entity_description.key]["state_action"]

        self._attr_temperature_unit = UnitOfTemperature.CELSIUS

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        self._attr_hvac_mode = hvac_mode
        self.async_write_ha_state()

        await self._set_state_function(True if hvac_mode == HVACMode.HEAT else False, self._attr_target_temperature)

    async def async_set_temperature(self, temperature: float, **kwargs: Any) -> None:
        # Changing the target temperature will not be worked if the HVAC mode is OFF. (server-side logic)
        self._attr_target_temperature = temperature
        self.async_write_ha_state()

        await self._set_state_function(True if self._attr_hvac_mode == HVACMode.HEAT else False, temperature)

    @callback
    def _handle_coordinator_update(self):
        """Handle updated data from the coordinator."""
        data = self._data
        self._attr_target_temperature = data[self.entity_description.key]["target_temperature"]
        self._attr_current_temperature = data[self.entity_description.key]["current_temperature"]
        self._attr_hvac_mode = data[self.entity_description.key]["state_mode"]
        self._attr_hvac_action = data[self.entity_description.key]["state_action"]

        super()._handle_coordinator_update()
