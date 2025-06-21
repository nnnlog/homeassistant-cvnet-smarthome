from homeassistant.components.switch import SwitchEntityDescription, SwitchDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .lib.homeassistant.entity.cvnet_standby_power_entity import CvnetStandbyPowerEntity
from .lib.model.config import CvnetConfigEntryRuntimeData

DESCRIPTIONS = [
    SwitchEntityDescription(
        key="outlet",
        translation_key="outlet",
        device_class=SwitchDeviceClass.OUTLET,
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

                entities.append(CvnetStandbyPowerEntity(coordinator, description, coordinator_key))

    async_add_entities(entities)
