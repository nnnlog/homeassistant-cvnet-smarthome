from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.core import callback

from .cvnet_entity import CvnetEntity


class CvnetSensorEntity(CvnetEntity, SensorEntity):
    """Representation of a CVnet electricity sensor entity."""

    @callback
    def _handle_coordinator_update(self):
        """Handle updated data from the coordinator."""
        data = self._data
        self._attr_native_value = data[self.entity_description.key]["value"]

        super()._handle_coordinator_update()
