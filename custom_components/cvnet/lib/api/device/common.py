import json

import aiohttp

from ..const import DEVICE_ID
from ...model.config import CvnetConfig
from ...model.device import EnabledDevicesRespond, DeviceType, DeviceDetailAndConnectInformation
from ...model.exception import UnknownException, UnauthorizedException


class DeviceApi:
    @staticmethod
    async def get_enabled_devices(websession: aiohttp.ClientSession, config: CvnetConfig) -> EnabledDevicesRespond:
        response = await websession.post(f"https://{config.host}/cvnet/mobile/mainmenu_info.do", data="[object Object]",
                                         headers={
                                             "Content-Type": "text/plain;charset=UTF-8",
                                         })

        if response.status != 200:
            raise UnknownException(f"Response status is not 200: {response.status}")

        data = json.loads(await response.text())

        if data["result"] == 0:
            raise UnauthorizedException()

        if data["result"] != 1:
            raise UnknownException("API call failed: Unknown error")

        return EnabledDevicesRespond(
            isHeating=data["CV"]["mainmenu_mobile_info"]["isHeating"] == "1",
            isLight=data["CV"]["mainmenu_mobile_info"]["isLight"] == "1",
            isVentilator=data["CV"]["mainmenu_mobile_info"]["isVentilator"] == "1",
            isTelemetering=data["CV"]["mainmenu_mobile_info"]["isTelemetering"] == "1",
            isConcent=data["CV"]["mainmenu_mobile_info"]["isConcent"] == "1",
        )

    @staticmethod
    async def get_device_detail(websession: aiohttp.ClientSession, config: CvnetConfig,
                                device_type: DeviceType) -> DeviceDetailAndConnectInformation:
        type_num = DEVICE_ID[device_type]

        if type_num is None:
            raise UnknownException(
                f"Device type {device_type} is not supported or should not be used through this api.")

        response = await websession.post(f"https://{config.host}/cvnet/mobile/device_info.do",
                                         data=f"type={type_num}",
                                         headers={
                                             "Content-Type": "application/x-www-form-urlencoded",
                                         })

        if response.status != 200:
            raise UnknownException(f"Response status is not 200: {response.status}")

        data = json.loads(await response.text())

        if data["result"] == 0:
            raise UnauthorizedException()

        if data["result"] != 1:
            raise UnknownException("API call failed: Unknown error")

        return data
