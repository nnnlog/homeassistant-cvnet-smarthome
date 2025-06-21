import json

from aiohttp import ClientWebSocketResponse

from ..const import DEVICE_ID
from ...model.config import CvnetConfig
from ...model.device import DeviceType


class DeviceWebSocketApi:
    @staticmethod
    async def send_ping(socket: ClientWebSocketResponse):
        await socket.send_json([
            json.dumps({"type": "ping"}),
        ])

    @staticmethod
    async def send_login_request(socket: ClientWebSocketResponse, config: CvnetConfig, reply_address: str):
        await socket.send_json([json.dumps({
            "type": "send",
            "address": "vertx.basicauthmanager.login",
            "body": {
                "username": config.username,
                "password": "cvnet" # It should be config.password, but CVnet's client is using a hardcoded password
            },
            "replyAddress": reply_address
        })])

    @staticmethod
    async def send_subscribe_request(socket: ClientWebSocketResponse, device_type: DeviceType):
        await socket.send_json([
            json.dumps({
                "type": "register",
                "address": str(int(DEVICE_ID[device_type], 16)),
            })
        ])

    @staticmethod
    async def send_all_device_information_request(socket: ClientWebSocketResponse, config: CvnetConfig, device_type: DeviceType, remote_tcp_addr: str):
        await socket.send_json([
            json.dumps({
                "type": "publish",
                "address": str(int(DEVICE_ID[device_type], 16)),
                "body": json.dumps({
                    "id": config.username,
                    "remote_addr": remote_tcp_addr,
                    "request": "status"
                })
            })
        ])
