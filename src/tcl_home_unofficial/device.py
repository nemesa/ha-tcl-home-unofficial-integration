"""."""

from dataclasses import dataclass

from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN


@dataclass
class DeviceData:
    def __init__(self, device_id: str, aws_thing: dict) -> None:
        self.beep_switch_state = int(aws_thing["state"]["reported"]["beepSwitch"])
        self.power_state = int(aws_thing["state"]["reported"]["powerSwitch"])
        self.target_temperature = int(
            aws_thing["state"]["reported"]["targetTemperature"]
        )
        self.device_id = device_id

    device_id: str
    power_state: int | bool
    beep_switch_state: int | bool
    target_temperature: int


@dataclass
class Device:
    """Device."""

    def __init__(
        self,
        device_id: str,
        device_type: str,
        name: str,
        firmware_version: str,
        aws_thing: dict,
    ) -> None:
        self.device_id = device_id
        self.device_type = device_type
        self.name = name
        self.firmware_version = firmware_version
        self.data = DeviceData(device_id, aws_thing)

    device_id: int
    device_type: str
    name: str
    firmware_version: str
    data: DeviceData | None = None


def toDeviceInfo(device: Device) -> DeviceInfo:
    """Convert Device to DeviceInfo."""
    return DeviceInfo(
        name=f"{device.name} ({device.device_id})",
        manufacturer="TCL",
        model=device.device_type,
        sw_version=device.firmware_version,
        identifiers={
            (
                DOMAIN,
                f"TCL-{device.device_id}",
            )
        },
    )
