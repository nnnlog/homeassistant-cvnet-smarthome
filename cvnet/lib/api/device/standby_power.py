import json

from aiohttp import ClientWebSocketResponse

from ..const import DEVICE_ID
from ...model.config import CvnetConfig
from ...model.device import DeviceType


class StandbyPowerDeviceApi:
    @staticmethod
    async def set_standby_power_state(socket: ClientWebSocketResponse, config: CvnetConfig, device_type: DeviceType, remote_tcp_addr: str, number: int, onoff: bool):
        await socket.send_json([json.dumps({
            "type": "publish",
            "address": str(int(DEVICE_ID[device_type], 16)),
            "body": json.dumps({
                "id": config.username,
                "remote_addr": remote_tcp_addr,
                "request": "control",
                "number": str(number),
                "onoff": "1" if onoff else "0",
            })
        })])
