import json
from typing import Any, TypedDict

import aiohttp

from ..model.config import CvnetConfig
from ..model.exception import UnauthorizedException, UnknownException


class InformationRespondType(TypedDict):
    ACCOUNT_NAME: str
    COMPLEX_NAME: str
    DONGHO: str
    dong: str
    ho: str
    id: str
    result: int


class InformationAPI:
    @staticmethod
    async def get_information(websession: aiohttp.ClientSession, config: CvnetConfig) -> InformationRespondType:
        response = await websession.post(f"https://{config.host}/cvnet/mobile/setting_list.do", data="key=GR_ACCOUNT&type=1",
                                     headers={
                                         "Content-Type": "application/x-www-form-urlencoded",
                                     })

        if response.status != 200:
            raise UnauthorizedException(f"Response status is not 200: {response.status}")

        data = json.loads(await response.text())

        if data["result"] != 1:
            if "message" in data:
                raise UnknownException(f"{data['message']}")
            else:
                raise UnknownException("API call failed: Unknown error")

        return data


