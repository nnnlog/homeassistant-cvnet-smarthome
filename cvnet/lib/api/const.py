from ..model.device import DeviceType

"""
gas: "0x11",
light: "0x12",
curtain: "0x13",
cooktop: "0x15",
heat: "0x16",
aircon: "0x17",
vent: "0x18",
standbypower: "0x19",
lightall: "0x1A",
multicurtain: "0x31",
multigas: "0x32",
guard: "0x41"
"""
DEVICE_ID = {
    DeviceType.HEATING: "0x16",
    DeviceType.LIGHT: "0x12",
    DeviceType.VENTILATOR: "0x18",
    DeviceType.STANDBY_POWER: "0x19",
    # Telemetering is not a device type, but a service.
}
