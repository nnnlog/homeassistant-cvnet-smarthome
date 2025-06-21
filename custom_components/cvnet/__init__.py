"""The CVnet Integration with web version integration."""

from __future__ import annotations

import asyncio
from typing import Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD, EVENT_HOMEASSISTANT_START, EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import HomeAssistant, CoreState
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .lib.homeassistant.coordinator.standby_power_device_data_update_coordinator import StandbyPowerDeviceDataUpdateCoordinator
from .lib.homeassistant.coordinator.heating_device_data_update_coordinator import HeatingDeviceDataUpdateCoordinator
from .lib.homeassistant.coordinator.ventilator_device_data_update_coordinator import VentilatorDeviceDataUpdateCoordinator
from .lib.homeassistant.coordinator.light_device_data_update_coordinator import LightDeviceDataUpdateCoordinator
from .lib.model.device import enabled_device_key_to_device_type
from .lib.homeassistant.coordinator.common.cvnet_websocket_data_update_coordinator import \
    CvnetWebsocketDataUpdateCoordinator
from .lib.homeassistant.coordinator.telemetering_device_data_update_coordinator import \
    TelemeteringDeviceDataUpdateCoordinator
from .const import PLATFORMS
from .lib.api.authentication_api import AuthenticationApi
from .lib.api.device.common import DeviceApi
from .lib.homeassistant.coordinator.common.cvnet_data_update_coordinator import CvnetDataUpdateCoordinator
from .lib.model.config import CvnetConfigEntryRuntimeData, CvnetConfig

type CvnetConfigEntry = ConfigEntry[CvnetConfigEntryRuntimeData]


async def get_coordinators(hass: HomeAssistant, entry: CvnetConfigEntry) -> list[CvnetDataUpdateCoordinator]:
    session = async_get_clientsession(hass)
    config = entry.runtime_data.config

    await AuthenticationApi.login(session, config)

    enabled_devices = await DeviceApi.get_enabled_devices(session, config)

    mapping: dict[str, Callable[[str], CvnetDataUpdateCoordinator]] = {
        "isTelemetering": lambda k: TelemeteringDeviceDataUpdateCoordinator(hass, config),
        "isLight": lambda k: LightDeviceDataUpdateCoordinator(hass, config, enabled_device_key_to_device_type(k)),
        "isVentilator": lambda k: VentilatorDeviceDataUpdateCoordinator(hass, config, enabled_device_key_to_device_type(k)),
        "isHeating": lambda k: HeatingDeviceDataUpdateCoordinator(hass, config, enabled_device_key_to_device_type(k)),
        "isConcent": lambda k: StandbyPowerDeviceDataUpdateCoordinator(hass, config, enabled_device_key_to_device_type(k)),
    }

    coordinators = []
    for key, generator in mapping.items():
        if key in enabled_devices and enabled_devices[key]:
            coordinators.append(generator(key))

    return coordinators


async def async_setup_entry(hass: HomeAssistant, entry: CvnetConfigEntry) -> bool:
    config = CvnetConfig(
        host=entry.data[CONF_HOST],
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
        unique_id=entry.unique_id,
    )

    entry.runtime_data = CvnetConfigEntryRuntimeData()
    entry.runtime_data.config = config

    coordinators = await get_coordinators(hass, entry)
    entry.runtime_data.coordinators = coordinators

    listener_tasks: list[asyncio.Task] = []
    for coordinator in coordinators:
        if isinstance(coordinator, CvnetWebsocketDataUpdateCoordinator):
            listener_tasks.append(entry.async_create_task(hass, coordinator.listen()))

    await asyncio.wait(list(map(lambda x: asyncio.create_task(x.async_config_entry_first_refresh()), coordinators)))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def _async_start_listener(_):
        for coordinator in coordinators:
            if isinstance(coordinator, CvnetWebsocketDataUpdateCoordinator):
                entry.runtime_data.listener_tasks.append(
                    entry.async_create_task(hass, coordinator.listen())
                )

    if hass.state == CoreState.starting:
        for task in listener_tasks:
            task.cancel()

        entry.async_on_unload(
            hass.bus.async_listen_once(
                EVENT_HOMEASSISTANT_STARTED, _async_start_listener
            )
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: CvnetConfigEntry) -> bool:
    for task in entry.runtime_data.listener_tasks:
        task.cancel()

    for coordinator in entry.runtime_data.coordinators:
        await coordinator.async_shutdown()

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
