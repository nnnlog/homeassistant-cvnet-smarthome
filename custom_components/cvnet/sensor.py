from homeassistant.components.climate import FAN_HIGH, FAN_MEDIUM, FAN_OFF, FAN_LOW
from homeassistant.components.sensor import SensorEntityDescription, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .lib.homeassistant.entity.cvnet_sensor_entity import CvnetSensorEntity
from .lib.model.config import CvnetConfigEntryRuntimeData

DESCRIPTIONS = [
    SensorEntityDescription(
        key="electricity_sensor",
        translation_key="electricity",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement="kWh",
        has_entity_name=True,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="gas_sensor",
        translation_key="gas",
        device_class=SensorDeviceClass.GAS,
        native_unit_of_measurement="m³",
        has_entity_name=True,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="water_sensor",
        translation_key="water",
        device_class=SensorDeviceClass.WATER,
        native_unit_of_measurement="m³",
        has_entity_name=True,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="ventilator_sensor",
        translation_key="ventilator",
        device_class=SensorDeviceClass.ENUM,
        options=[FAN_OFF, FAN_LOW, FAN_MEDIUM, FAN_HIGH],
        has_entity_name=True,
    ),
]

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[CvnetConfigEntryRuntimeData],
    async_add_entities: AddEntitiesCallback,
) -> None:
    entities: list[Entity] = []

    for coordinator in entry.runtime_data.coordinators:
        for coordinator_key, data in coordinator.data.items():
            for description in DESCRIPTIONS:
                if description.key not in data:
                    continue

                entities.append(CvnetSensorEntity(coordinator, description, coordinator_key))

    async_add_entities(entities)
