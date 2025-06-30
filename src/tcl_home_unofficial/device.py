"""."""

from dataclasses import dataclass
from enum import StrEnum

from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN


class ModeEnum(StrEnum):
    """Mode states."""

    COOL = "Cool"
    HEAT = "Heat"
    DEHUMIDIFICATION = "Dehumidification"
    FAN = "Fan"
    AUTO = "Auto"


@dataclass
class DeviceData:
    def __init__(self, device_id: str, aws_thing_state: dict, delta: dict) -> None:
        self.beep_switch = int(delta.get("beepSwitch", aws_thing_state["beepSwitch"]))
        self.power_switch = int(
            delta.get("powerSwitch", aws_thing_state["powerSwitch"])
        )
        self.target_temperature = int(
            delta.get("targetTemperature", aws_thing_state["targetTemperature"])
        )
        self.work_mode = int(delta.get("workMode", aws_thing_state["workMode"]))
        self.device_id = device_id

    device_id: str
    power_switch: int | bool
    beep_switch: int | bool
    target_temperature: int
    work_mode: int


def getModeFromDeviceData(data: DeviceData) -> ModeEnum:
    """Get the mode as a ModeEnum."""
    match data.work_mode:
        case 0:
            return ModeEnum.AUTO
        case 1:
            return ModeEnum.COOL
        case 2:
            return ModeEnum.DEHUMIDIFICATION
        case 3:
            return ModeEnum.FAN
        case 4:
            return ModeEnum.HEAT
        case _:
            return ModeEnum.AUTO


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
        self.data = DeviceData(
            device_id,
            aws_thing["state"]["reported"],
            aws_thing["state"].get("delta", {}),
        )
        self.data_desired = DeviceData(device_id, aws_thing["state"]["desired"], {})

    device_id: int
    device_type: str
    name: str
    firmware_version: str
    data: DeviceData | None = None
    data_desired: DeviceData | None = None


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
