"""."""

from dataclasses import dataclass
from enum import StrEnum

from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from .device_spit_ac import TCL_SplitAC_DeviceData


class DeviceTypeEnum(StrEnum):
    SPLIT_AC = "Split AC"
    SPLIT_AC_FRESH_AIR = "Split AC Fresh air"


class DeviceFeature(StrEnum):
    SENSOR_CURRENT_TEMPERATURE = "sensor.current_temperature"
    SWITCH_POWER = "switch.powerSwitch"
    SWITCH_BEEP = "switch.beepSwitch"
    SWITCH_ECO = "switch.eco"
    SWITCH_HEALTHY = "switch.healthy"
    SWITCH_DRYING = "switch.drying"
    SWITCH_SCREEN = "switch.screen"
    SELECT_MODE = "select.mode"
    SELECT_WIND_SPEED = "select.windSpeed"
    SELECT_VERTICAL_DIRECTION = "select.verticalDirection"
    SELECT_HORIZONTAL_DIRECTION = "select.horizontalDirection"
    SELECT_SLEEP_MODE = "select.sleepMode"
    NUMBER_TARGET_TEMPERATURE = "number.targetTemperature"
    NUMBER_TARGET_TEMPERATURE_ALLOW_HALF_DIGITS = "number.targetTemperature.allow_half_digits"
    BUTTON_SELF_CLEAN = "button.selfClean"
    CLIMATE = "climate"


def getSupportedFeatures(device_type: DeviceTypeEnum) -> list[DeviceFeature]:
    match device_type:
        case DeviceTypeEnum.SPLIT_AC:
            return [
                DeviceFeature.SENSOR_CURRENT_TEMPERATURE,
                DeviceFeature.SWITCH_POWER,
                DeviceFeature.SWITCH_BEEP,
                DeviceFeature.SWITCH_ECO,
                DeviceFeature.SWITCH_HEALTHY,
                DeviceFeature.SWITCH_DRYING,
                DeviceFeature.SWITCH_SCREEN,
                DeviceFeature.SELECT_MODE,
                DeviceFeature.SELECT_WIND_SPEED,
                DeviceFeature.SELECT_VERTICAL_DIRECTION,
                DeviceFeature.SELECT_HORIZONTAL_DIRECTION,
                DeviceFeature.SELECT_SLEEP_MODE,
                DeviceFeature.NUMBER_TARGET_TEMPERATURE,
                DeviceFeature.BUTTON_SELF_CLEAN,
                DeviceFeature.CLIMATE,
            ]
        case DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
            return [
                DeviceFeature.SENSOR_CURRENT_TEMPERATURE,
                DeviceFeature.SWITCH_POWER,
                DeviceFeature.SWITCH_BEEP,
                DeviceFeature.SWITCH_ECO,
                DeviceFeature.SWITCH_HEALTHY,
                DeviceFeature.SWITCH_DRYING,
                DeviceFeature.SWITCH_SCREEN,
                DeviceFeature.SELECT_MODE,
                DeviceFeature.SELECT_WIND_SPEED,
                DeviceFeature.SELECT_VERTICAL_DIRECTION,
                DeviceFeature.SELECT_HORIZONTAL_DIRECTION,
                DeviceFeature.SELECT_SLEEP_MODE,
                DeviceFeature.NUMBER_TARGET_TEMPERATURE,
                DeviceFeature.NUMBER_TARGET_TEMPERATURE_ALLOW_HALF_DIGITS,
                DeviceFeature.BUTTON_SELF_CLEAN,
                DeviceFeature.CLIMATE,
            ]
        case _:
            return []



def is_implemented_by_integration(device_type: str) -> bool:
    match device_type:
        case DeviceTypeEnum.SPLIT_AC:
            return True
        case DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
            return True
        case _:
            return False


@dataclass
class Device:
    """Device."""

    def __init__(
        self,
        device_id: str,
        device_type: str,
        name: str,
        firmware_version: str,
        aws_thing: dict | None,
    ) -> None:
        self.device_id = device_id
        self.device_type = device_type
        self.name = name
        self.firmware_version = firmware_version
        self.is_implemented_by_integration = is_implemented_by_integration(
            device_type=device_type
        )
        match device_type:
            case DeviceTypeEnum.SPLIT_AC:
                if aws_thing is not None:
                    self.data = TCL_SplitAC_DeviceData(
                        device_id,
                        aws_thing["state"]["reported"],
                        aws_thing["state"].get("delta", {}),
                    )
                else:
                    self.data = None
            case _:
                self.data = None

    device_id: int
    device_type: str
    name: str
    firmware_version: str
    is_implemented_by_integration: bool
    data: TCL_SplitAC_DeviceData | None = None


def toDeviceInfo(device: Device) -> DeviceInfo:
    """Convert Device to DeviceInfo."""
    return DeviceInfo(
        name=f"{device.name} ({device.device_id}){'' if device.is_implemented_by_integration else ' (Not implemented)'}",
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
