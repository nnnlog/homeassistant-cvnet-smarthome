import functools
from typing import Any

from homeassistant.components.climate import FAN_OFF, FAN_LOW, FAN_MEDIUM, FAN_HIGH, HVACAction, HVACMode
from homeassistant.helpers.device_registry import DeviceInfo

from ..api.device.heating import HeatingDeviceApi
from .common.cvnet_websocket_client import CvnetWebsocketClient


class HeatingClient(CvnetWebsocketClient):
    """
    DeviceInformation:
    [
        {
            "number": 2,
            "title": "거실"
        }
    ]
    """

    async def set_state(self, number: int, onoff: bool, target_temperature: int) -> None:
        for _ in range(2):
            await HeatingDeviceApi.set_heating_state(self.socket, self.config, self.device_type,
                                                     self._remote_tcp_address, number, onoff, target_temperature)

    async def parse_contents_from_websocket(self, body: dict[str, Any]) -> dict[str, Any]:
        """
        Response:

        a["{\"address\":\"22\",\"body\":\"{\\\"dev\\\":22,\\\"contents\\\":[{\\\"number\\\":1,\\\"current_temp\\\":0,\\\"setting_temp\\\":0,\\\"status\\\":-1,\\\"onoff\\\":0},{\\\"number\\\":2,\\\"current_temp\\\":27,\\\"setting_temp\\\":26,\\\"status\\\":1,\\\"onoff\\\":0},{\\\"number\\\":3,\\\"current_temp\\\":0,\\\"setting_temp\\\":0,\\\"status\\\":-1,\\\"onoff\\\":0},{\\\"number\\\":4,\\\"current_temp\\\":0,\\\"setting_temp\\\":0,\\\"status\\\":-1,\\\"onoff\\\":0},{\\\"number\\\":5,\\\"current_temp\\\":0,\\\"setting_temp\\\":0,\\\"status\\\":-1,\\\"onoff\\\":0},{\\\"number\\\":6,\\\"current_temp\\\":0,\\\"setting_temp\\\":0,\\\"status\\\":-1,\\\"onoff\\\":0},{\\\"number\\\":7,\\\"current_temp\\\":0,\\\"setting_temp\\\":0,\\\"status\\\":-1,\\\"onoff\\\":0},{\\\"number\\\":8,\\\"current_temp\\\":0,\\\"setting_temp\\\":0,\\\"status\\\":-1,\\\"onoff\\\":0}]}\"}"]
        """

        response = {}

        for heating in body["contents"]:
            if heating["status"] == -1:
                continue

            use_default_name = True
            name: str = f"{heating['number'] if len(body["contents"]) > 1 else ""}".strip()
            for device in self.device_information:
                if device["number"] == int(heating["number"]):
                    use_default_name = False
                    name = device["title"]
                    break


            response.update({
                f"heating_{heating['number']}": {
                    "name": name,
                    "use_default_name": use_default_name,
                    "info": DeviceInfo(
                        identifiers={(self.config.unique_id, f"heating")},
                        manufacturer="CVnet",
                        translation_key="heating",
                    ),
                    "heating": {
                        "set_state_function": functools.partial(lambda _heating, onoff, target_temp: self.set_state(int(_heating["number"]), onoff, target_temp if target_temp is not None else heating["setting_temp"]), heating),
                        "target_temperature": heating["setting_temp"] if heating["onoff"] else None,
                        "current_temperature": heating["current_temp"],
                        "state_mode": HVACMode.HEAT if heating["onoff"] else HVACMode.OFF,
                        "state_action": HVACAction.OFF if not heating["onoff"] else
                        (HVACAction.HEATING if heating["setting_temp"] > heating["current_temp"] else HVACAction.IDLE),
                    },
                }
            })

        return response
