from enum import Enum
from typing import TypedDict


class EnabledDevicesRespond(TypedDict):
    """
    Not supported devices will not be included in this type.
    """
    isHeating: bool  # 난방
    isLight: bool  # 조명
    # isWholeLight: bool
    # isGas: bool
    isVentilator: bool  # 환기 (전열교환기)
    # isAircon: bool
    # isCurtain: bool
    # isElevator: bool
    # isCooktop: bool
    isConcent: bool  # 대기전력 (콘센트)
    # isPhotoAlbum: bool
    # isCallWebRTC: bool
    # isNotice: bool
    # isMaintCost: bool
    isTelemetering: bool  # 원격검침 (전기, 수도, 가스)
    # isEnterCar: bool
    # isParcel: bool
    # isVisitor: bool
    # isEmergency: bool
    # isCctv: bool
    # isEnterRecord: bool
    # isLocation: bool
    # isParkingRemain: bool
    # isBookingCar: bool


class DeviceType(Enum):
    HEATING = 0
    LIGHT = 1
    VENTILATOR = 2
    TELEMETERING = 3
    STANDBY_POWER = 4


def enabled_device_key_to_device_type(key: str) -> DeviceType:
    if key == "isHeating":
        return DeviceType.HEATING
    elif key == "isLight":
        return DeviceType.LIGHT
    elif key == "isVentilator":
        return DeviceType.VENTILATOR
    elif key == "isTelemetering":
        return DeviceType.TELEMETERING
    elif key == "isConcent":
        return DeviceType.STANDBY_POWER

    raise ValueError(f"Unknown device type key: {key}")


class UnitDeviceDetail(TypedDict):
    number: int
    title: str

    zone: int  # Only used in light devices


class DeviceDetailAndConnectInformation(TypedDict):
    dev: str  # Device ID
    tcp_remote_addr: str  # TCP remote address
    websock_address: str  # WebSocket address
    id: str  # User ID when using to connect socket (string)
    contents: list[UnitDeviceDetail]  # List of device units


class TelemeteringRespond(TypedDict):
    electricity: float  # kWh
    water: float  # m^3
    gas: float  # m^3
