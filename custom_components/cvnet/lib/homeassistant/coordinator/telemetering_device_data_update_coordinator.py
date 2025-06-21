from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .common.cvnet_data_update_coordinator import CvnetDataUpdateCoordinator
from ...client.telemetering_client import TelemeteringClient
from ...model.config import CvnetConfig


class TelemeteringDeviceDataUpdateCoordinator(CvnetDataUpdateCoordinator):
    _client: TelemeteringClient

    def __init__(self, hass: HomeAssistant, config: CvnetConfig):
        super().__init__(hass, config)

        self._client = TelemeteringClient(async_get_clientsession(hass), config)

    @property
    def client(self) -> TelemeteringClient:
        return self._client
