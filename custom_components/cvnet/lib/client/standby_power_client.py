import functools
from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo

from .common.cvnet_websocket_client import CvnetWebsocketClient
from ..api.device.standby_power import StandbyPowerDeviceApi


class StandbyPowerClient(CvnetWebsocketClient):
    """
    DeviceInformation:
    [
        {
            "number": 1,
            "title": "거실1"
        },
        {
            "number": 2,
            "title": "거실2"
        }
    ]
    """

    async def set_state(self, number: int, onoff: bool) -> None:
        await StandbyPowerDeviceApi.set_standby_power_state(self.socket, self.config, self.device_type, self._remote_tcp_address, number, onoff)

    async def parse_contents_from_websocket(self, body: dict[str, Any]) -> dict[str, Any]:
        """
        Response:

        "{\"address\":\"25\",\"body\":\"{\\\"dev\\\":25,\\\"items\\\":[{\\\"deviceid\\\":\\\"1\\\",\\\"on_off\\\":\\\"1\\\"},{\\\"deviceid\\\":\\\"2\\\",\\\"on_off\\\":\\\"0\\\"},{\\\"deviceid\\\":\\\"3\\\",\\\"on_off\\\":\\\"1\\\"},{\\\"deviceid\\\":\\\"4\\\",\\\"on_off\\\":\\\"1\\\"}]}\"}"
        """

        response = {}

        for power in body["items"]:
            name: str = f"{power['deviceid']}"
            use_default_name = True

            for device in self.device_information:
                if device["number"] == int(power["deviceid"]):
                    use_default_name = False
                    name = device["title"]
                    break

            response.update({
                f"outlet_{power['deviceid']}": {
                    "name": name,
                    "use_default_name": use_default_name,
                    "info": DeviceInfo(
                        identifiers={(self.config.unique_id, f"outlet")},
                        manufacturer="CVnet",
                        translation_key="outlet"
                    ),
                    "outlet": {
                        "set_state_function": functools.partial(lambda _power, state : self.set_state(int(_power["deviceid"]), state), power),
                        "value": bool(int(power["on_off"])),
                    },
                }
            })

        return response
