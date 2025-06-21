import json

from aiohttp import ClientWebSocketResponse

from ..const import DEVICE_ID
from ...model.config import CvnetConfig
from ...model.device import DeviceType


class VentilatorDeviceApi:
    @staticmethod
    async def set_ventilator_state(socket: ClientWebSocketResponse, config: CvnetConfig, device_type: DeviceType, remote_tcp_addr: str, number: int, running: bool, wind_level_mode: int = 0):
        await socket.send_json([json.dumps({
            "type": "publish",
            "address": str(int(DEVICE_ID[device_type], 16)),
            "body": json.dumps({
                "id": config.username,
                "remote_addr": remote_tcp_addr,
                "request": "control",
                "number": str(number),
                "running": "1" if running else "0",
                "wind_level_mode": str(wind_level_mode),
                "operation_mode": "1", # 0: auto, 1: manual
                "timer": "0",
            })
        })])
