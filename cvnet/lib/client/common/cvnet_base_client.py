import logging
import traceback
from typing import Any

import aiohttp

from ...api.authentication_api import AuthenticationApi
from ...model.config import CvnetConfig
from ...model.exception import UnauthorizedException

_LOGGER = logging.getLogger(__name__)

class CvnetBaseClient:
    session: aiohttp.ClientSession
    config: CvnetConfig

    def __init__(self, session: aiohttp.ClientSession, config: CvnetConfig):
        self.session = session
        self.config = config

    async def _request(self, callback, retry: bool = True) -> Any:
        """
        All requests except login should be wrapped in this method.
        """
        try:
            return await callback()
        except UnauthorizedException:
            await self.login()
            return await self._request(callback, retry=False)
        except Exception as e:
            if retry:
                _LOGGER.error(f"Error occurred: {e}. Retrying...")
                _LOGGER.error(traceback.format_exc())
                return self._request(callback, retry=False)
            else:
                raise e

    async def login(self) -> None:
        try:
            await AuthenticationApi.login(self.session, self.config)
        except Exception as e:
            _LOGGER.error(f"Login failed: {e}")
            raise e

    async def get_data(self) -> dict[str, Any]:
        raise NotImplementedError("This method should be implemented in subclasses.")
