from logging import Logger
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .cvnet_data_update_coordinator import CvnetDataUpdateCoordinator
from ....client.common.cvnet_websocket_client import CvnetWebsocketClient
from ....model.config import CvnetConfig
from ....model.device import DeviceType


class CvnetWebsocketDataUpdateCoordinator(CvnetDataUpdateCoordinator):
    logger: Logger = Logger("cvnet_websocket_data_update_coordinator")
    config_entry: ConfigEntry
    device_type: DeviceType

    def __init__(self, hass: HomeAssistant, config: CvnetConfig, device_type: DeviceType) -> None:
        super().__init__(hass, config)

        # self._client = CvnetWebsocketClient(async_get_clientsession(hass), config, device_type,
        #                                     self.update_partial_data)

    @property
    def client(self) -> CvnetWebsocketClient:
        raise NotImplementedError

    def update_partial_data(self, data: dict[str, Any]) -> None:
        new_data: dict[str, Any]

        if not self.data:
            new_data = data
        else:
            new_data = self.data.copy()
            for key, value in data.items():
                if key not in new_data or new_data[key] != value:
                    new_data[key] = value

        self.async_set_updated_data(new_data)

    def listen(self):
        return self.client.listen()

    def disconnect(self):
        return self.client.disconnect()