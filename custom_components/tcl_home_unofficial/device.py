"""."""

from dataclasses import dataclass
from enum import StrEnum

from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from .device_spit_ac import TCL_SplitAC_DeviceData
from .device_spit_ac_fresh_air import TCL_SplitAC_Fresh_Air_DeviceData


class DeviceTypeEnum(StrEnum):
    SPLIT_AC = "Split AC"
    SPLIT_AC_FRESH_AIR = "Split AC Fresh air"


class DeviceFeature(StrEnum):
    SENSOR_CURRENT_TEMPERATURE = "sensor.current_temperature"
    SENSOR_INTERNAL_UNIT_COIL_TEMPERATURE = "sensor.internal_unit_coil_temperature"
    SENSOR_EXTERNAL_UNIT_COIL_TEMPERATURE = "sensor.external_unit_coil_temperature"
    SENSOR_EXTERNAL_UNIT_TEMPERATURE = "sensor.external_unit_temperature"
    SENSOR_EXTERNAL_UNIT_EXHAUST_TEMPERATURE = (
        "sensor.external_unit_exhaust_temperature"
    )
    SWITCH_POWER = "switch.powerSwitch"
    SWITCH_BEEP = "switch.beepSwitch"
    SWITCH_ECO = "switch.eco"
    SWITCH_HEALTHY = "switch.healthy"
    SWITCH_DRYING = "switch.drying"
    SWITCH_SCREEN = "switch.screen"
    SWITCH_LIGHT_SENSE = "switch.lightSense"
    SELECT_MODE = "select.mode"
    SELECT_WIND_SPEED = "select.windSpeed"
    SELECT_WIND_SPEED_7_Gear = "select.windSpeed7Gear"
    SELECT_WIND_FEELING = "select.windFeeling"
    SELECT_VERTICAL_DIRECTION = "select.verticalDirection"
    SELECT_HORIZONTAL_DIRECTION = "select.horizontalDirection"
    SELECT_SLEEP_MODE = "select.sleepMode"
    SELECT_FRESH_AIR = "select.freshAir"
    SELECT_GENERATOR_MODE = "select.generatorMode"
    NUMBER_TARGET_TEMPERATURE = "number.targetTemperature"
    NUMBER_TARGET_TEMPERATURE_ALLOW_HALF_DIGITS = (
        "number.targetTemperature.allow_half_digits"
    )
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
                DeviceFeature.SENSOR_INTERNAL_UNIT_COIL_TEMPERATURE,
                DeviceFeature.SENSOR_EXTERNAL_UNIT_COIL_TEMPERATURE,
                DeviceFeature.SENSOR_EXTERNAL_UNIT_TEMPERATURE,
                DeviceFeature.SENSOR_EXTERNAL_UNIT_EXHAUST_TEMPERATURE,
                DeviceFeature.SWITCH_POWER,
                DeviceFeature.SWITCH_BEEP,
                DeviceFeature.SWITCH_ECO,
                DeviceFeature.SWITCH_HEALTHY,
                DeviceFeature.SWITCH_DRYING,
                DeviceFeature.SWITCH_SCREEN,
                DeviceFeature.SWITCH_LIGHT_SENSE,
                DeviceFeature.SELECT_MODE,
                DeviceFeature.SELECT_VERTICAL_DIRECTION,
                DeviceFeature.SELECT_HORIZONTAL_DIRECTION,
                DeviceFeature.SELECT_SLEEP_MODE,
                DeviceFeature.SELECT_WIND_SPEED_7_Gear,
                DeviceFeature.SELECT_WIND_FEELING,
                DeviceFeature.SELECT_FRESH_AIR,
                DeviceFeature.SELECT_GENERATOR_MODE,
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
        if aws_thing is not None:
            match device_type:
                case DeviceTypeEnum.SPLIT_AC:
                    self.data = TCL_SplitAC_DeviceData(
                        device_id,
                        aws_thing["state"]["reported"],
                        aws_thing["state"].get("delta", {}),
                    )
                case DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    self.data = TCL_SplitAC_Fresh_Air_DeviceData(
                        device_id,
                        aws_thing["state"]["reported"],
                        aws_thing["state"].get("delta", {}),
                    )
                case _:
                    self.data = None
        else:
            self.data = None

    device_id: int
    device_type: str
    name: str
    firmware_version: str
    is_implemented_by_integration: bool
    data: TCL_SplitAC_DeviceData | TCL_SplitAC_Fresh_Air_DeviceData | None = None


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
