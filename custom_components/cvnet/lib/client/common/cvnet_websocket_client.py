import asyncio
import json
import logging
import random
import string
import traceback
import uuid
from asyncio import Task
from typing import Any, Callable

import aiohttp
from aiohttp import ClientWebSocketResponse

from .cvnet_base_client import CvnetBaseClient
from ...api.const import DEVICE_ID
from ...api.device.common import DeviceApi
from ...api.device.websocket_common import DeviceWebSocketApi
from ...model.config import CvnetConfig
from ...model.device import DeviceType, DeviceDetailAndConnectInformation, UnitDeviceDetail

_LOGGER = logging.getLogger(__name__)

_MAX_WS_FETCH_ALL_DATA_TIMEOUT = 3  # seconds

class CvnetWebsocketClient(CvnetBaseClient):
    """
    This client has a responsibility for listening to the specific one kind of devices from the CVnet server.
    """
    device_type: DeviceType
    update_partial_data_callback: Callable[[dict[str, Any]], None]

    socket: ClientWebSocketResponse | None = None

    _websocket_address: str | None = None
    _remote_tcp_address: str
    device_information: list[UnitDeviceDetail]

    _ping_task: Task | None = None
    _established_future: asyncio.Future[None] | None = None

    _locked_for_all_request: asyncio.Lock = asyncio.Lock()

    _temp_data_for_all_request: dict | None = None
    _future_for_all_request: asyncio.Future[dict[str, Any]] | None = None

    def __init__(self, session: aiohttp.ClientSession, config: CvnetConfig, device_type: DeviceType, update_partial_data_callback: Callable[[dict[str, Any]], None]):
        super().__init__(session, config)

        self.device_type = device_type
        self.update_partial_data_callback = update_partial_data_callback

    async def _get_ws_connection_information(self) -> DeviceDetailAndConnectInformation:
        return await DeviceApi.get_device_detail(self.session, self.config, self.device_type)

    async def get_ws_connection_information(self) -> DeviceDetailAndConnectInformation:
        return await self._request(self._get_ws_connection_information)

    async def _send_all_device_request(self):
        if self.socket is None:
            raise RuntimeError("Socket is not connected.")

        await DeviceWebSocketApi.send_all_device_information_request(self.socket, self.config, self.device_type,
                                                                     self._remote_tcp_address)

    async def _finish_all_data_collection(self):
        await asyncio.sleep(_MAX_WS_FETCH_ALL_DATA_TIMEOUT)
        async with self._locked_for_all_request:
            if self._future_for_all_request is not None and not self._future_for_all_request.done():
                self._future_for_all_request.set_result(self._temp_data_for_all_request)
                self._temp_data_for_all_request = None
                self._future_for_all_request = None

    async def get_data(self) -> dict[str, Any]:
        if self._established_future is not None and not self._established_future.done():
            await asyncio.wait_for(self._established_future, timeout=_MAX_WS_FETCH_ALL_DATA_TIMEOUT)

        if self.socket is None:
            raise RuntimeError("Socket is not connected.")


        _capture_task: Task | None = None

        async with self._locked_for_all_request:
            if self._future_for_all_request is None:
                self._temp_data_for_all_request = {}

                await self._send_all_device_request()

                loop = asyncio.get_running_loop()
                self._future_for_all_request = loop.create_future()

                _capture_task = asyncio.create_task(self._finish_all_data_collection())
        try:
            return await asyncio.wait_for(self._future_for_all_request, _MAX_WS_FETCH_ALL_DATA_TIMEOUT * 2)  # wait for 10 seconds for the data to be collected
        finally:
            if _capture_task is not None and not _capture_task.cancelled():
                _capture_task.cancel()

    def _generate_connect_url(self) -> str:
        gen_str = lambda n: ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(n))
        gen_num = lambda n: ''.join(random.choice(string.digits) for _ in range(n))

        url = self._websocket_address.replace("https://", "wss://")
        url += f"/{gen_num(3)}/{gen_str(8)}/websocket"

        return url

    async def _initialize_connection_information(self) -> None:
        response = await self.get_ws_connection_information()
        self._websocket_address = response["websock_address"]
        self._remote_tcp_address = response["tcp_remote_addr"]
        self.device_information = response["contents"]

    async def _connect(self):
        """Connect to the CVnet socket server."""
        if self.socket is not None:
            raise RuntimeError("Socket is already connected.")

        if not self._websocket_address:
            await self._initialize_connection_information()

        self.socket = await self.session.ws_connect(self._generate_connect_url())
        self._ping_task = asyncio.create_task(self._ping())

    async def disconnect(self):
        if self.socket is not None:
            await self.socket.close()

            if self._ping_task is not None and not self._ping_task.cancelled():
                self._ping_task.cancel()

            if self._future_for_all_request is not None and not self._future_for_all_request.done():
                self._future_for_all_request.cancel()

            if self._established_future is not None and not self._established_future.done():
                self._established_future.cancel()

        self.socket = None

        self._ping_task = None

        self._temp_data_for_all_request = None
        self._future_for_all_request = None

        self._established_future = None

    async def _ping(self):
        while True:
            if self.socket is None:
                continue
            try:
                await DeviceWebSocketApi.send_ping(self.socket)
            except asyncio.CancelledError as e:
                break
            except aiohttp.ClientError as e:
                _LOGGER.error(f"Ping failed: {e}")
                _LOGGER.error(traceback.format_exc())
                continue
            except Exception as e:
                _LOGGER.error(f"Unexpected error during ping: {e}")
                _LOGGER.error(traceback.format_exc())
                continue
            await asyncio.sleep(5)

    async def parse_contents_from_websocket(self, body: dict[str, Any]) -> dict[str, Any]:
        """
        Parse the contents from the WebSocket message.
        This method should be overridden by subclasses to handle specific device data.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    async def listen(self):
        """Listen for messages from the CVnet socket server."""
        max_retry_delay = 60  # seconds
        retry_delay = 1

        while True:
            try:
                self._established_future = asyncio.get_running_loop().create_future()
                await self._connect()

                reply_address = str(uuid.uuid4())

                async for msg in self.socket:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        header = msg.data[0]
                        raw = msg.data[1:]
                        if header == "h":
                            continue
                        elif header == "c":
                            # we will expect to close the connection by server immediately after this message (closed by server).
                            continue
                        elif header == "o":  # connection established
                            retry_delay = 1  # reset retry delay on successful connection
                            await DeviceWebSocketApi.send_login_request(self.socket, self.config, reply_address)
                            continue
                        elif header == "a":
                            data = json.loads(raw)

                            for datum in data:
                                datum = json.loads(datum)
                                if "address" not in datum:
                                    _LOGGER.warning(f"Unknown message format: {datum}")
                                    continue

                                if datum["address"] == reply_address:
                                    await DeviceWebSocketApi.send_subscribe_request(self.socket, self.device_type)
                                    _LOGGER.info(f"Subscribed to device type: {self.device_type}")
                                    self._established_future.set_result(None)
                                elif datum["address"] == str(int(DEVICE_ID[self.device_type], 16)):  # I'll separate the DEVICE_ID from the device type
                                    if "body" not in datum:
                                        continue

                                    body = json.loads(datum["body"])

                                    parsed_contents = await self.parse_contents_from_websocket(body)

                                    if self._future_for_all_request is not None:
                                        async with self._locked_for_all_request:
                                            self._temp_data_for_all_request.update(parsed_contents)
                                    else:
                                        self.update_partial_data_callback(parsed_contents)
                                else:
                                    _LOGGER.warning(f"Received message for unknown address: {datum['address']}")
                                    _LOGGER.warning(datum)
                        else:
                            # handle other message types
                            _LOGGER.warning(f"Unknown message type: {header}")
                            continue
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        _LOGGER.error(f"WebSocket error: {self.socket.exception()}")
                        break
                    elif msg.type == aiohttp.WSMsgType.CLOSE:
                        _LOGGER.info("WebSocket connection closed.")
                        break

            except asyncio.CancelledError as e:
                break
            except Exception as e:
                _LOGGER.error(f"Error in listen loop: {e}")
                _LOGGER.error(traceback.format_exc())
            finally:
                await self.disconnect()

            current_task = asyncio.current_task()
            if current_task and current_task.cancelled():
                break

            _LOGGER.info(f"Waiting {retry_delay} seconds before WebSocket reconnect attempt.")
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, max_retry_delay)
