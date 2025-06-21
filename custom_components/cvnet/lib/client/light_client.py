import functools
from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo

from ..api.device.light import LightDeviceApi
from .common.cvnet_websocket_client import CvnetWebsocketClient


class LightClient(CvnetWebsocketClient):
    """
    DeviceInformation:
    [
        {
            "number": 1,
            "dimming": 0,
            "zone": 1,
            "title": "거실1"
        },
        {
            "number": 2,
            "dimming": 0,
            "zone": 1,
            "title": "거실2"
        },
        {
            "number": 1,
            "dimming": 0,
            "zone": 2,
            "title": "주방"
        }
    ]
    """

    async def set_state(self, number: int, zone: int, onoff: bool) -> None:
        await LightDeviceApi.set_light_state(self.socket, self.config, self.device_type, self._remote_tcp_address, number, zone, onoff)

    async def parse_contents_from_websocket(self, body: dict[str, Any]) -> dict[str, Any]:
        """
        Response:

        a["{\"address\":\"18\",\"body\":\"{\\\"number\\\":\\\"1\\\",\\\"brightness\\\":\\\"0\\\",\\\"dev\\\":18,\\\"zone\\\":\\\"1\\\",\\\"onoff\\\":\\\"0\\\"}\"}"]
        a["{\"address\":\"18\",\"body\":\"{\\\"number\\\":\\\"2\\\",\\\"brightness\\\":\\\"0\\\",\\\"dev\\\":18,\\\"zone\\\":\\\"1\\\",\\\"onoff\\\":\\\"0\\\"}\"}"]
        a["{\"address\":\"18\",\"body\":\"{\\\"number\\\":\\\"1\\\",\\\"brightness\\\":\\\"0\\\",\\\"dev\\\":18,\\\"zone\\\":\\\"2\\\",\\\"onoff\\\":\\\"0\\\"}\"}"]
        """

        use_default_name = True
        name: str = f"{body['number']}-{body['zone']}"
        for device in self.device_information:
            if device["number"] == int(body["number"]) and device["zone"] == int(body["zone"]):
                use_default_name = False
                name = device["title"]
                break

        return {
            f"light_{body['number']}_{body['zone']}": {
                "name": name,
                "use_default_name": use_default_name,
                "info": DeviceInfo(
                    identifiers={(self.config.unique_id, f"light")},
                    manufacturer="CVnet",
                    translation_key="light",
                ),
                "light": {
                    "set_state_function": functools.partial(lambda _body, state : self.set_state(int(_body["number"]), int(_body["zone"]), state), body),
                    "value": bool(int(body["onoff"])),
                },
            }
        }
