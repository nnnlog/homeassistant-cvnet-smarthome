import json
from urllib import parse

import aiohttp

from ..model.config import CvnetConfig
from ..model.exception import UnknownException, AuthenticationFailedException


class AuthenticationApi:
    @staticmethod
    async def login(websession: aiohttp.ClientSession, config: CvnetConfig) -> None:
        """Authenticate with the given URL, ID, and password."""
        response = await websession.post(
            f"https://{config.host}/cvnet/mobile/login.do",
            data=parse.urlencode({
                "id": config.username,
                "password": config.password,
                "deviceId": "0",
                "tokenId": "0",
            }),
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )

        if response.status != 200:
            raise UnknownException(f"Response status is not 200: {response.status}")

        data = json.loads(await response.text())

        if data["result"] != 1:
            if "message" in data:
                raise AuthenticationFailedException(f"{data['message']}")
            else:
                raise UnknownException("Login failed: Unknown error")
