from typing import Any, Coroutine, Callable

from homeassistant.components.climate import ClimateEntity, ClimateEntityDescription, ClimateEntityFeature, FAN_ON, \
    FAN_LOW, FAN_MEDIUM, FAN_HIGH, FAN_OFF, HVACMode, HVACAction
from homeassistant.components.fan import FanEntity, FanEntityFeature, FanEntityDescription
from homeassistant.const import UnitOfTemperature
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util.percentage import ordered_list_item_to_percentage, percentage_to_ordered_list_item

from .cvnet_entity import CvnetEntity

_FAN_TYPES = [FAN_LOW, FAN_MEDIUM, FAN_HIGH]

class CvnetVentilatorEntity(CvnetEntity, FanEntity):
    _wind_level = {
        FAN_LOW: 1,
        FAN_MEDIUM: 2,
        FAN_HIGH: 3,
    }

    _set_state_function: Callable[[bool, int], Coroutine]
    _attr_custom_speed: str | None = None

    def __init__(self, coordinator: DataUpdateCoordinator[dict[str, Any]], entity_description: FanEntityDescription,
                 coordinator_data_key: str):
        super().__init__(coordinator, entity_description, coordinator_data_key)

        data = coordinator.data[coordinator_data_key]
        self._set_state_function = data[entity_description.key]["set_state_function"]

        self._attr_supported_features = FanEntityFeature.SET_SPEED | FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF
        self._attr_custom_speed = data[entity_description.key]["state"]

        self._attr_is_on = data[entity_description.key]["is_on"]

    async def async_turn_on(self, percentage: int | None = None, preset_mode: str | None = None, **kwargs: Any) -> None:
        self._attr_is_on = True
        self._attr_custom_speed = percentage_to_ordered_list_item(_FAN_TYPES, percentage) if percentage != 0 and percentage is not None else FAN_LOW
        self.async_write_ha_state()

        await self._set_state_function(self._attr_is_on, self._wind_level[self._attr_custom_speed])

    async def async_turn_off(self, percentage: int | None = None, preset_mode: str | None = None,
                             **kwargs: Any) -> None:
        self._attr_is_on = False
        self._attr_custom_speed = None
        self.async_write_ha_state()

        await self._set_state_function(self._attr_is_on, 0)

    async def async_set_percentage(self, percentage: int) -> None:
        if percentage > 0:
            wind_level = percentage_to_ordered_list_item(_FAN_TYPES, percentage)
            self._attr_custom_speed = wind_level
            self._attr_is_on = True
        else:
            wind_level = None
            self._attr_custom_speed = None
            self._attr_is_on = False
        self.async_write_ha_state()

        await self._set_state_function(self._attr_is_on, self._wind_level.get(wind_level, 0))

    @property
    def percentage(self) -> int | None:
        if self._attr_custom_speed is None:
            return None
        return ordered_list_item_to_percentage(_FAN_TYPES, self._attr_custom_speed)

    @property
    def speed_count(self) -> int:
        return len(_FAN_TYPES)

    @callback
    def _handle_coordinator_update(self):
        """Handle updated data from the coordinator."""
        data = self._data

        self._attr_custom_speed = data[self.entity_description.key]["state"]
        self._attr_is_on = data[self.entity_description.key]["is_on"]

        super()._handle_coordinator_update()

# class CvnetVentilatorClimateEntity(CvnetEntity, ClimateEntity):
#     _wind_level = {
#         FAN_OFF: 0,
#         FAN_LOW: 1,
#         FAN_MEDIUM: 2,
#         FAN_HIGH: 3,
#     }
#
#     _set_state_function: Callable[[bool, int], Coroutine]
#
#     def __init__(self, coordinator: DataUpdateCoordinator[dict[str, Any]], entity_description: ClimateEntityDescription,
#                  coordinator_data_key: str):
#         super().__init__(coordinator, entity_description, coordinator_data_key)
#
#         data = coordinator.data[coordinator_data_key]
#         self._set_state_function = data[entity_description.key]["set_state_function"]
#
#         self._attr_supported_features = ClimateEntityFeature.FAN_MODE
#
#         self._attr_fan_modes = [FAN_OFF, FAN_LOW, FAN_MEDIUM, FAN_HIGH]
#         self._attr_fan_mode = data[entity_description.key]["state"]
#
#         self._attr_hvac_modes = [HVACMode.FAN_ONLY, HVACMode.OFF]
#         self._attr_hvac_mode = HVACMode.FAN_ONLY if self._attr_fan_mode != FAN_OFF else HVACMode.OFF
#
#         self._attr_hvac_action = HVACAction.OFF if self._attr_fan_mode == FAN_OFF else HVACAction.FAN
#
#         self._attr_temperature_unit = UnitOfTemperature.CELSIUS
#
#     async def async_set_fan_mode(self, fan_mode: str) -> None:
#         running: bool = fan_mode != FAN_OFF
#
#         self._attr_fan_mode = fan_mode
#         self._attr_hvac_mode = HVACMode.FAN_ONLY if fan_mode != FAN_OFF else HVACMode.OFF
#         self._attr_hvac_action = HVACAction.OFF if fan_mode == FAN_OFF else HVACAction.FAN
#         self.async_write_ha_state()
#
#         await self._set_state_function(running, self._wind_level[fan_mode])
#
#     async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
#         self._attr_fan_mode = FAN_OFF if hvac_mode == HVACMode.OFF else FAN_LOW
#         self._attr_hvac_mode = hvac_mode
#         self._attr_hvac_action = HVACAction.OFF if hvac_mode == HVACMode.OFF else HVACAction.FAN
#         self.async_write_ha_state()
#
#         await self._set_state_function(True if hvac_mode == HVACMode.FAN_ONLY else False,
#                                        self._wind_level[self._attr_fan_mode])
#
#
#     @callback
#     def _handle_coordinator_update(self):
#         """Handle updated data from the coordinator."""
#         data = self._data
#         self._attr_fan_mode = data[self.entity_description.key]["state"]
#         self._attr_hvac_mode = HVACMode.FAN_ONLY if self._attr_fan_mode != FAN_OFF else HVACMode.OFF
#         self._attr_hvac_action = HVACAction.OFF if self._attr_fan_mode == FAN_OFF else HVACAction.FAN
#
#         super()._handle_coordinator_update()
