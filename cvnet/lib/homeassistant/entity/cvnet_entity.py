from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator


class CvnetEntity(CoordinatorEntity[dict[str, Any]]):
    """Base class for Cvnet entities."""
    coordinator_data_key: str

    def __init__(self, coordinator: DataUpdateCoordinator[dict[str, Any]], entity_description: EntityDescription,
                 coordinator_data_key: str):
        """
        Initialize the Cvnet entity.

        :param coordinator: The coordinator for this entity.
        :param entity_id: The unique identifier for this entity.
        """
        super().__init__(coordinator)

        self.unique_id = f"{coordinator.config_entry.unique_id}_{coordinator_data_key}_{entity_description.key}"
        self.entity_description = entity_description
        self.coordinator_data_key = coordinator_data_key

        data = coordinator.data[coordinator_data_key]
        self._attr_device_info = data["info"]
        if "name" in data:
            if "use_default_name" in data and not data["use_default_name"]:
                self._attr_name = data["name"]
            else:
                self._attr_translation_placeholders = {
                    "name": data["name"],
                }

    @property
    def available(self) -> bool:
        """Return True if the entity is available."""
        return self.coordinator.last_update_success and self._data is not None

    @property
    def _data(self):
        """Return the data for this entity."""
        return self.coordinator.data.get(self.coordinator_data_key, None)

    def _handle_coordinator_update(self) -> None:
        # self._attr_device_info = self._data["info"]

        super()._handle_coordinator_update()
