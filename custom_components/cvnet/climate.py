from typing import Type, Tuple

from homeassistant.components.climate import ClimateEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .lib.homeassistant.entity.cvnet_heating_entity import CvnetHeatingEntity
# from .lib.homeassistant.entity.cvnet_ventilator_entity import CvnetVentilatorClimateEntity
from .lib.model.config import CvnetConfigEntryRuntimeData

DESCRIPTIONS: list[Tuple[ClimateEntityDescription, Type]] = [
    # (
    #     ClimateEntityDescription(
    #         key="ventilator_climate",
    #         translation_key="ventilator",
    #         device_class="ventilator",
    #         has_entity_name=True,
    #     ), CvnetVentilatorClimateEntity
    # ),
    (
        ClimateEntityDescription(
            key="heating",
            translation_key="heating",
            device_class="heating",
            has_entity_name=True,
        ), CvnetHeatingEntity
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
            for description, constructor in DESCRIPTIONS:
                if description.key not in data:
                    continue

                entities.append(constructor(coordinator, description, coordinator_key))

    async_add_entities(entities)
