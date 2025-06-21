from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .common.cvnet_websocket_data_update_coordinator import CvnetWebsocketDataUpdateCoordinator
from ...client.standby_power_client import StandbyPowerClient
from ...model.config import CvnetConfig
from ...model.device import DeviceType


class StandbyPowerDeviceDataUpdateCoordinator(CvnetWebsocketDataUpdateCoordinator):
    _client: StandbyPowerClient

    def __init__(self, hass: HomeAssistant, config: CvnetConfig, device_type: DeviceType):
        super().__init__(hass, config, device_type)

        self._client = StandbyPowerClient(async_get_clientsession(hass), config, device_type, self.update_partial_data)

    @property
    def client(self) -> StandbyPowerClient:
        return self._client
