"""."""

from homeassistant.core import HomeAssistant
from .device_data_storage import get_stored_data, set_stored_data
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


def get_SplitAC_Type1_capabilities():
    return [3, 7, 8, 9, 11, 12, 13, 21]


@dataclass
class TCL_SplitAC_Type1_DeviceData:
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


async def get_stored_spit_ac_type1_data(
    hass: HomeAssistant, device_id: str
) -> dict[str, any]:
    need_save = False
    stored_data = await get_stored_data(hass, device_id)
    if stored_data is None:
        stored_data = {}
        need_save = True

    if stored_data.get("non_user_config") is None:
        stored_data["non_user_config"] = {}
        need_save = True
    if stored_data["non_user_config"].get("min_celsius_temp") is None:
        stored_data["non_user_config"]["min_celsius_temp"] = 16
        need_save = True
    if stored_data["non_user_config"].get("max_celsius_temp") is None:
        stored_data["non_user_config"]["max_celsius_temp"] = 36
        need_save = True
    if stored_data["non_user_config"].get("native_temp_step") is None:
        stored_data["non_user_config"]["native_temp_step"] = 1
        need_save = True

    if stored_data.get("target_temperature") is None:
        stored_data["target_temperature"] = {}
        need_save = True
    if stored_data["target_temperature"].get("Cool") is None:
        stored_data["target_temperature"]["Cool"] = {}
        need_save = True
        if stored_data["target_temperature"]["Cool"].get("value") is None:
            stored_data["target_temperature"]["Cool"]["value"] = 24
            need_save = True
    if stored_data["target_temperature"].get("Heat") is None:
        stored_data["target_temperature"]["Heat"] = {}
        need_save = True
        if stored_data["target_temperature"]["Heat"].get("value") is None:
            stored_data["target_temperature"]["Heat"]["value"] = 26
            need_save = True
    if stored_data["target_temperature"].get("Dehumidification") is None:
        stored_data["target_temperature"]["Dehumidification"] = {}
        need_save = True
        if stored_data["target_temperature"]["Dehumidification"].get("value") is None:
            stored_data["target_temperature"]["Dehumidification"]["value"] = 26
            need_save = True
    if stored_data["target_temperature"].get("Fan") is None:
        stored_data["target_temperature"]["Fan"] = {}
        need_save = True
        if stored_data["target_temperature"]["Fan"].get("value") is None:
            stored_data["target_temperature"]["Fan"]["value"] = 24
            need_save = True
        need_save = True
    if stored_data["target_temperature"].get("Auto") is None:
        stored_data["target_temperature"]["Auto"] = {}
        need_save = True
        if stored_data["target_temperature"]["Auto"].get("value") is None:
            stored_data["target_temperature"]["Auto"]["value"] = 24
            need_save = True
        need_save = True

    if need_save:
        await set_stored_data(hass, device_id, stored_data)
    return stored_data


class TCL_SplitAC_Type1_DeviceData_Helper:
    def __init__(self, data: TCL_SplitAC_Type1_DeviceData) -> None:
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
