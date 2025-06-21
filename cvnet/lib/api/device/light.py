import json

from aiohttp import ClientWebSocketResponse

from ..const import DEVICE_ID
from ...model.config import CvnetConfig
from ...model.device import DeviceType


class LightDeviceApi:
    @staticmethod
    async def set_light_state(socket: ClientWebSocketResponse, config: CvnetConfig, device_type: DeviceType, remote_tcp_addr: str, number: int, zone: int, onoff: bool):
        await socket.send_json([json.dumps({
            "type": "publish",
            "address": str(int(DEVICE_ID[device_type], 16)),
            "body": json.dumps({
                "id": config.username,
                "remote_addr": remote_tcp_addr,
                "request": "control",
                "zone": str(zone),
                "number": str(number),
                "onoff": "1" if onoff else "0",
                "brightness": "0",
            })
        })])
