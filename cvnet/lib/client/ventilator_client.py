import functools
from typing import Any

from homeassistant.components.climate import FAN_OFF, FAN_LOW, FAN_MEDIUM, FAN_HIGH
from homeassistant.helpers.device_registry import DeviceInfo

from ..api.device.light import LightDeviceApi
from .common.cvnet_websocket_client import CvnetWebsocketClient
from ..api.device.ventilator import VentilatorDeviceApi


class VentilatorClient(CvnetWebsocketClient):
    """
    DeviceInformation:
    [
        {
            "number": 1,
            "title": "환기"
        }
    ]
    """

    async def set_state(self, number: int, running: bool, wind_level_mode: int = 0) -> None:
        for _ in range(2):
            await VentilatorDeviceApi.set_ventilator_state(self.socket, self.config, self.device_type, self._remote_tcp_address, number, running, wind_level_mode)

    async def parse_contents_from_websocket(self, body: dict[str, Any]) -> dict[str, Any]:
        """
        Response:

        a["{\"address\":\"24\",\"body\":\"{\\\"dev\\\":24,\\\"contents\\\":[{\\\"running\\\":0,\\\"number\\\":1,\\\"operation_mode\\\":1,\\\"wind_level_mode\\\":0}]}\"}"]
        """

        response = {}

        for ventilator in body["contents"]:
            use_default_name = True
            name: str = f"{ventilator['number'] if len(body["contents"]) > 1 else ""}".strip()

            for device in self.device_information:
                if device["number"] == int(ventilator["number"]):
                    use_default_name = False
                    name = device["title"]
                    break

            fan_mode = [FAN_OFF, FAN_LOW, FAN_MEDIUM, FAN_HIGH][max(0, min(3, int(ventilator["wind_level_mode"])))] if bool(ventilator["running"]) else FAN_OFF
            # fan_mode = [FAN_OFF, FAN_LOW, FAN_MEDIUM, FAN_HIGH][max(0, min(3, int(ventilator["wind_level_mode"])))]
            response.update({
                f"ventilator_{ventilator['number']}": {
                    "name": name,
                    "use_default_name": use_default_name,
                    "info": DeviceInfo(
                        identifiers={(self.config.unique_id, f"ventilator")},
                        manufacturer="CVnet",
                        translation_key="ventilator",
                    ),
                    "ventilator_climate": {
                        "set_state_function": functools.partial(lambda _ventilator, state, wind_level : self.set_state(int(_ventilator["number"]), state, wind_level), ventilator),
                        "state": fan_mode
                    },
                    "ventilator_fan": {
                        "set_state_function": functools.partial(lambda _ventilator, state, wind_level : self.set_state(int(_ventilator["number"]), state, wind_level), ventilator),
                        "state": fan_mode if fan_mode != FAN_OFF else None,
                        "is_on": fan_mode != FAN_OFF,
                    },
                    "ventilator_sensor": {
                        "value": fan_mode
                    }
                }
            })

        return response
