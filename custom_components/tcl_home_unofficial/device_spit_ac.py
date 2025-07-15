"""."""

from dataclasses import dataclass
from enum import StrEnum

from .device_ac_common import (
    LeftAndRightAirSupplyVectorEnum,
    ModeEnum,
    SleepModeEnum,
    UpAndDownAirSupplyVectorEnum,
    getLeftAndRightAirSupplyVector,
    getMode,
    getSleepMode,
    getUpAndDownAirSupplyVector,
)


class WindSeedEnum(StrEnum):
    STRONG = "Strong"
    HEIGH = "Heigh"
    MID_HEIGH = "Mid-heigh"
    MID_LOW = "Mid-low"
    MEDIUM = "Medium"
    LOW = "Low"
    MUTE = "Mute"
    AUTO = "Auto"


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
        return getMode(self.data.work_mode)

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
        return getUpAndDownAirSupplyVector(self.data.vertical_direction)

    def getLeftAndRightAirSupplyVector(self) -> LeftAndRightAirSupplyVectorEnum:
        return getLeftAndRightAirSupplyVector(self.data.horizontal_direction)

    def getSleepMode(self) -> SleepModeEnum:
        return getSleepMode(self.data.sleep)
