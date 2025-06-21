"""Config flow for the CVnet Integration with web version integration."""

from __future__ import annotations

import json
import logging
from hashlib import sha256
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_HOST
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import selector, TextSelector, TextSelectorType, TextSelectorConfig

from .lib.model.config import CvnetConfig
from .lib.api.authentication_api import AuthenticationApi
from .lib.api.information_api import InformationAPI
from .lib.api.inquiry_site_api import InquirySiteApi
from .const import DOMAIN, CONF_SITE_NAME, CONF_REGION
from .lib.model.exception import AuthenticationFailedException

_LOGGER = logging.getLogger(__name__)


class CvnetConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for CVnet Integration with web version."""

    VERSION = 1
    _flow_data: dict[str, Any] = None

    async def async_step_user(
            self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        self._flow_data: dict[str, Any] = {}
        return await self.async_step_select_region(user_input)

    async def async_step_select_region(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle the region selection step."""
        if user_input is not None:
            self._flow_data[CONF_REGION] = user_input[CONF_REGION]

            return await self.async_step_select_site()

        websession = async_get_clientsession(self.hass)
        regions = await InquirySiteApi.get_region_list(websession)

        schema = vol.Schema(
            {
                vol.Required(CONF_REGION): selector({
                    "select": {
                        "options": regions,
                        "sort": True
                    }
                })
            }
        )

        return self.async_show_form(
            step_id="select_region", data_schema=schema
        )

    async def async_step_select_site(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle the site selection step."""
        if user_input is not None:
            data = json.loads(user_input[CONF_SITE_NAME])
            self._flow_data[CONF_HOST] = data["url"]
            self._flow_data[CONF_SITE_NAME] = data["name"]

            return await self.async_step_login()

        region = self._flow_data.get(CONF_REGION)

        websession = async_get_clientsession(self.hass)
        sites = await InquirySiteApi.get_site_list(websession, region)

        schema = vol.Schema(
            {
                vol.Required(CONF_SITE_NAME): selector({
                    "select": {
                        "options": sites,
                        "sort": True,
                    }
                })
            }
        )

        return self.async_show_form(
            step_id="select_site", data_schema=schema,
            description_placeholders={
                CONF_REGION: self._flow_data[CONF_REGION]
            }
        )

    async def async_step_login(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            self._flow_data["username"] = user_input[CONF_USERNAME]
            self._flow_data["password"] = user_input[CONF_PASSWORD]

            websession = async_get_clientsession(self.hass)
            config = CvnetConfig(self._flow_data[CONF_HOST], self._flow_data[CONF_USERNAME],
                                 self._flow_data[CONF_PASSWORD], "")
            try:
                await AuthenticationApi.login(websession, config)
            except AuthenticationFailedException as e:
                return self.async_show_form(
                    step_id="login",
                    data_schema=vol.Schema({
                        vol.Required(CONF_USERNAME): TextSelector(
                            TextSelectorConfig(type=TextSelectorType.TEXT, autocomplete="username")
                        ),
                        vol.Required(CONF_PASSWORD): TextSelector(
                            TextSelectorConfig(type=TextSelectorType.PASSWORD, autocomplete="current-password")
                        ),
                    }),
                    description_placeholders={
                        CONF_REGION: self._flow_data[CONF_REGION],
                        CONF_SITE_NAME: self._flow_data[CONF_SITE_NAME]
                    },
                    errors={"base": "invalid_auth"}
                )

            information = await InformationAPI.get_information(websession, config)

            unique_id_raw = f"{information["COMPLEX_NAME"]}:{information["DONGHO"]}:{information["id"]}"
            unique_id = sha256(unique_id_raw.encode("utf-8")).hexdigest()

            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            # Here you would typically validate the credentials and connect to the API
            # If successful, you would store the connection data in self._flow_data
            return self.async_create_entry(
                title=f"CVnet Devices ({information['COMPLEX_NAME']} {information['DONGHO']})", data={
                    CONF_HOST: self._flow_data[CONF_HOST],
                    CONF_USERNAME: self._flow_data[CONF_USERNAME],
                    CONF_PASSWORD: self._flow_data[CONF_PASSWORD],
                })

        schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.TEXT, autocomplete="username")
                ),
                vol.Required(CONF_PASSWORD): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.PASSWORD, autocomplete="current-password")
                ),
            }
        )

        return self.async_show_form(
            step_id="login", data_schema=schema, description_placeholders={
                CONF_REGION: self._flow_data[CONF_REGION],
                CONF_SITE_NAME: self._flow_data[CONF_SITE_NAME]
            }
        )
