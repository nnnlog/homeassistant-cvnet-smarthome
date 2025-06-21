from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .common.cvnet_websocket_data_update_coordinator import CvnetWebsocketDataUpdateCoordinator
from ...client.ventilator_client import VentilatorClient
from ...model.config import CvnetConfig
from ...model.device import DeviceType


class VentilatorDeviceDataUpdateCoordinator(CvnetWebsocketDataUpdateCoordinator):
    _client: VentilatorClient

    def __init__(self, hass: HomeAssistant, config: CvnetConfig, device_type: DeviceType):
        super().__init__(hass, config, device_type)

        self._client = VentilatorClient(async_get_clientsession(hass), config, device_type, self.update_partial_data)

    @property
    def client(self) -> VentilatorClient:
        return self._client
