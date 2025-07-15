"""."""

from dataclasses import dataclass
from enum import StrEnum

from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN


class DeviceTypeEnum(StrEnum):
    SPLIT_AC = "Split AC"


class ModeEnum(StrEnum):
    COOL = "Cool"
    HEAT = "Heat"
    DEHUMIDIFICATION = "Dehumidification"
    FAN = "Fan"
    AUTO = "Auto"


class WindSeedEnum(StrEnum):
    STRONG = "Strong"
    HEIGH = "Heigh"
    MID_HEIGH = "Mid-heigh"
    MID_LOW = "Mid-low"
    MEDIUM = "Medium"
    LOW = "Low"
    MUTE = "Mute"
    AUTO = "Auto"


class UpAndDownAirSupplyVectorEnum(StrEnum):
    UP_AND_DOWN_SWING = "Up and down swing"
    UPWARDS_SWING = "Upwards swing"
    DOWNWARDS_SWING = "Downwards swing"
    TOP_FIX = "Top fix"
    UPPER_FIX = "Upper fix"
    MIDDLE_FIX = "Middle fix"
    LOWER_FIX = "Lower fix"
    BOTTOM_FIX = "Bottom fix"
    NOT_SET = "Not set"


class LeftAndRightAirSupplyVectorEnum(StrEnum):
    LEFT_AND_RIGHT_SWING = "Left and right swing"
    LEFT_SWING = "Left swing"
    MIDDLE_SWING = "Middle swing"
    RIGHT_SWING = "Right swing"
    LEFT_FIX = "Left fix"
    CENTER_LEFT_FIX = "Center-left fix"
    MIDDLE_FIX = "Middle fix"
    CENTER_RIGHT_FIX = "Center-right fix"
    RIGHT_FIX = "Right fix"
    NOT_SET = "Not set"


class SleepModeEnum(StrEnum):
    STANDARD = "Standard"
    ELDERLY = "Elderly"
    CHILD = "Child"
    OFF = "off"


@dataclass
class TCL_SplitAC_DeviceData:
    def __init__(self, device_id: str, aws_thing_state: dict, delta: dict) -> None:
        self.beep_switch = int(delta.get("beepSwitch", aws_thing_state["beepSwitch"]))
        self.power_switch = int(
            delta.get("powerSwitch", aws_thing_state["powerSwitch"])
        )
        self.target_temperature = int(
            delta.get("targetTemperature", aws_thing_state["targetTemperature"])
        )
        self.current_temperature = int(
            delta.get("currentTemperature", aws_thing_state["currentTemperature"])
        )
        self.work_mode = int(delta.get("workMode", aws_thing_state["workMode"]))
        self.high_temperature_wind = int(
            delta.get("highTemperatureWind", aws_thing_state["highTemperatureWind"])
        )
        self.turbo = int(delta.get("turbo", aws_thing_state["turbo"]))
        self.silence_switch = int(
            delta.get("silenceSwitch", aws_thing_state["silenceSwitch"])
        )
        self.wind_speed = int(delta.get("windSpeed", aws_thing_state["windSpeed"]))

        self.vertical_switch = int(
            delta.get("verticalSwitch", aws_thing_state["verticalSwitch"])
        )
        self.vertical_direction = int(
            delta.get("verticalDirection", aws_thing_state["verticalDirection"])
        )

        self.horizontal_switch = int(
            delta.get("horizontalSwitch", aws_thing_state["horizontalSwitch"])
        )
        self.horizontal_direction = int(
            delta.get("horizontalDirection", aws_thing_state["horizontalDirection"])
        )

        self.sleep = int(delta.get("sleep", aws_thing_state["sleep"]))
        self.eco = int(delta.get("ECO", aws_thing_state["ECO"]))
        self.healthy = int(delta.get("healthy", aws_thing_state["healthy"]))
        self.anti_moldew = int(delta.get("antiMoldew", aws_thing_state["antiMoldew"]))
        self.self_clean = int(delta.get("selfClean", aws_thing_state["selfClean"]))
        self.screen = int(delta.get("screen", aws_thing_state["screen"]))
        self.device_id = device_id

    device_id: str
    power_switch: int | bool
    beep_switch: int | bool
    target_temperature: int
    current_temperature: int
    high_temperature_wind: int
    turbo: int
    silence_switch: int
    wind_speed: int
    vertical_switch: int
    vertical_direction: int
    horizontal_switch: int
    horizontal_direction: int
    sleep: int
    healthy: int
    eco: int
    anti_moldew: int
    self_clean: int
    screen: int


class TCL_SplitAC_DeviceData_Helper:
    def __init__(self, data: TCL_SplitAC_DeviceData) -> None:
        self.data = data

    def getMode(self) -> ModeEnum:
        match self.data.work_mode:
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

    def getWindSpeed(self) -> WindSeedEnum:
        match self.data.wind_speed:
            case 6:
                return (
                    WindSeedEnum.STRONG if self.data.turbo == 1 else WindSeedEnum.HEIGH
                )
            case 5:
                return WindSeedEnum.MID_HEIGH
            case 4:
                return WindSeedEnum.MEDIUM
            case 3:
                return WindSeedEnum.MID_LOW
            case 2:
                return (
                    WindSeedEnum.MUTE
                    if self.data.silence_switch == 1
                    else WindSeedEnum.LOW
                )
            case 0:
                return WindSeedEnum.AUTO
            case _:
                return WindSeedEnum.AUTO

    def getUpAndDownAirSupplyVector(self) -> UpAndDownAirSupplyVectorEnum:
        match self.data.vertical_direction:
            case 1:
                return UpAndDownAirSupplyVectorEnum.UP_AND_DOWN_SWING
            case 2:
                return UpAndDownAirSupplyVectorEnum.UPWARDS_SWING
            case 3:
                return UpAndDownAirSupplyVectorEnum.DOWNWARDS_SWING
            case 8:
                return UpAndDownAirSupplyVectorEnum.NOT_SET
            case 9:
                return UpAndDownAirSupplyVectorEnum.TOP_FIX
            case 10:
                return UpAndDownAirSupplyVectorEnum.UPPER_FIX
            case 11:
                return UpAndDownAirSupplyVectorEnum.MIDDLE_FIX
            case 12:
                return UpAndDownAirSupplyVectorEnum.LOWER_FIX
            case 13:
                return UpAndDownAirSupplyVectorEnum.BOTTOM_FIX

    def getLeftAndRightAirSupplyVector(self) -> LeftAndRightAirSupplyVectorEnum:
        match self.data.horizontal_direction:
            case 1:
                return LeftAndRightAirSupplyVectorEnum.LEFT_AND_RIGHT_SWING
            case 2:
                return LeftAndRightAirSupplyVectorEnum.LEFT_SWING
            case 3:
                return LeftAndRightAirSupplyVectorEnum.MIDDLE_SWING
            case 4:
                return LeftAndRightAirSupplyVectorEnum.RIGHT_SWING
            case 8:
                return LeftAndRightAirSupplyVectorEnum.NOT_SET
            case 9:
                return LeftAndRightAirSupplyVectorEnum.LEFT_FIX
            case 10:
                return LeftAndRightAirSupplyVectorEnum.CENTER_LEFT_FIX
            case 11:
                return LeftAndRightAirSupplyVectorEnum.MIDDLE_FIX
            case 12:
                return LeftAndRightAirSupplyVectorEnum.CENTER_RIGHT_FIX
            case 13:
                return LeftAndRightAirSupplyVectorEnum.RIGHT_FIX

    def getSleepMode(self) -> SleepModeEnum:
        match self.data.sleep:
            case 1:
                return SleepModeEnum.STANDARD
            case 2:
                return SleepModeEnum.ELDERLY
            case 3:
                return SleepModeEnum.CHILD
            case 0:
                return SleepModeEnum.OFF


def is_implemented_by_integration(device_type: str) -> bool:
    match device_type:
        case DeviceTypeEnum.SPLIT_AC:
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
