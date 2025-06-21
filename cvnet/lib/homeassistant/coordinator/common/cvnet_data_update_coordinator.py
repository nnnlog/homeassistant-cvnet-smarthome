from logging import Logger
from typing import Any
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from ....client.common.cvnet_base_client import CvnetBaseClient
from ....model.config import CvnetConfig


class CvnetDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    logger: Logger = Logger("cvnet_data_update_coordinator")
    config_entry: ConfigEntry

    _client: CvnetBaseClient

    def __init__(self, hass: HomeAssistant, config: CvnetConfig) -> None:
        super().__init__(
            hass,
            logger=self.logger,
            name="cvnet_data_update_coordinator",
            update_interval=timedelta(seconds=10),
            update_method=self._async_update_data,
        )

        # self._client = CvnetBaseClient(async_get_clientsession(hass), config)

    @property
    def client(self) -> CvnetBaseClient:
        raise NotImplementedError

    async def _async_update_data(self) -> dict[str, Any]:
        return await self.client.get_data()
