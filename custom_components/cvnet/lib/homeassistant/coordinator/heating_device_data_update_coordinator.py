from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .common.cvnet_websocket_data_update_coordinator import CvnetWebsocketDataUpdateCoordinator
from ...client.heating_client import HeatingClient
from ...model.config import CvnetConfig
from ...model.device import DeviceType


class HeatingDeviceDataUpdateCoordinator(CvnetWebsocketDataUpdateCoordinator):
    _client: HeatingClient

    def __init__(self, hass: HomeAssistant, config: CvnetConfig, device_type: DeviceType):
        super().__init__(hass, config, device_type)

        self._client = HeatingClient(async_get_clientsession(hass), config, device_type, self.update_partial_data)

    @property
    def client(self) -> HeatingClient:
        return self._client
