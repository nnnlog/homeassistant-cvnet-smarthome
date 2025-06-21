import asyncio

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator


class CvnetConfig:
    host: str
    username: str
    password: str

    unique_id: str

    def __init__(self, host: str, username: str, password: str, unique_id: str):
        self.host = host
        self.username = username
        self.password = password

        self.unique_id = unique_id


class CvnetConfigEntryRuntimeData:
    config: CvnetConfig
    coordinators: list[DataUpdateCoordinator] = []
    listener_tasks: list[asyncio.Task] = []
