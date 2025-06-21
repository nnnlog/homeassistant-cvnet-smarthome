import json
import aiohttp

from ...model.config import CvnetConfig
from ...model.device import TelemeteringRespond
from ...model.exception import UnknownException, UnauthorizedException


class TelemeteringDeviceApi:
    @staticmethod
    async def get_telemetering_device_detail(websession: aiohttp.ClientSession, config: CvnetConfig) -> TelemeteringRespond:
        response = await websession.post(f"https://{config.host}/cvnet/mobile/telemeter_info.do",
                                         data="[object Object]",
                                         headers={
                                             "Content-Type": "text/plain;charset=UTF-8",
                                         })

        if response.status != 200:
            raise UnknownException(f"Response status is not 200: {response.status}")

        try:
            data = json.loads(await response.text())
        except json.JSONDecodeError as e:
            raise UnauthorizedException()  # server returns html when unauthorized

        if data["result"] != 1:
            raise UnknownException("API call failed: Unknown error")

        return TelemeteringRespond(
            electricity=float(data["electric"]),
            gas=float(data["gas"]),
            water=float(data["water"]),
        )
