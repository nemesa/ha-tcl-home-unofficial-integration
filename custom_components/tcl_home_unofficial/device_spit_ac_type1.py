"""."""

from homeassistant.core import HomeAssistant
from .device_data_storage import get_stored_data, set_stored_data, safe_set_value
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
    HIGH = "High"
    MID_HIGH = "Mid-high"
    MID_LOW = "Mid-low"
    MEDIUM = "Medium"
    LOW = "Low"
    MUTE = "Mute"
    AUTO = "Auto"


def get_SplitAC_Type1_capabilities() -> list[list[int]]:
    capabilities1 = [3, 7, 8, 9, 11, 12, 13, 21]
    capabilities1.sort()

    capabilities2 = [3, 7, 8, 9, 11, 12, 13, 21, 23]
    capabilities2.sort()
    
    capabilities3 = [3, 5, 7, 8, 9, 11, 12, 13, 21, 23]
    capabilities3.sort()    
    
    capabilities4 = [5, 7, 8, 9, 11, 12, 13, 23, 28]
    capabilities4.sort()      
    
    capabilities5 = [3, 8, 9, 11, 12, 13, 22, 23]
    capabilities5.sort()

    capabilities6 = [3, 5, 7, 8, 9, 11, 12, 13, 21]
    capabilities6.sort()

    capabilities7 = [3, 7, 8, 9, 11, 12, 13, 23]
    capabilities7.sort()    
    
    capabilities8 = [3, 7, 8, 9, 11, 12, 13, 21, 22, 23]
    capabilities8.sort()
    
    
    return [capabilities1, capabilities2, capabilities3, capabilities4, capabilities5 ,capabilities6, capabilities7, capabilities8]


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

        self.eight_add_hot = int(
            delta.get("eightAddHot", aws_thing_state["eightAddHot"])
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
    eight_add_hot: int
    screen: int


async def get_stored_spit_ac_type1_data(
    hass: HomeAssistant, device_id: str
) -> dict[str, any]:
    need_save = False
    stored_data = await get_stored_data(hass, device_id)
    if stored_data is None:
        stored_data = {}
        need_save = True

    stored_data, need_save = safe_set_value(
        stored_data, "non_user_config.min_celsius_temp", 16
    )
    stored_data, need_save = safe_set_value(
        stored_data, "non_user_config.max_celsius_temp", 36
    )
    stored_data, need_save = safe_set_value(
        stored_data, "non_user_config.native_temp_step", 1.0
    )

    stored_data, need_save = safe_set_value(
        stored_data, "user_config.behavior.memorize_temp_by_mode", False
    )
    stored_data, need_save = safe_set_value(
        stored_data, "user_config.behavior.memorize_fan_speed_by_mode", False
    )
    stored_data, need_save = safe_set_value(
        stored_data, "user_config.behavior.silent_beep_when_turn_on", False
    )

    stored_data, need_save = safe_set_value(
        stored_data, "target_temperature.Cool.value", 24
    )
    stored_data, need_save = safe_set_value(
        stored_data, "target_temperature.Heat.value", 36
    )
    stored_data, need_save = safe_set_value(
        stored_data, "target_temperature.Dehumidification.value", 24
    )
    stored_data, need_save = safe_set_value(
        stored_data, "target_temperature.Fan.value", 24
    )
    stored_data, need_save = safe_set_value(
        stored_data, "target_temperature.Auto.value", 24
    )

    stored_data, need_save = safe_set_value(
        stored_data, "fan_speed.Cool.value", WindSeedEnum.AUTO
    )
    stored_data, need_save = safe_set_value(
        stored_data, "fan_speed.Heat.value", WindSeedEnum.AUTO
    )
    stored_data, need_save = safe_set_value(
        stored_data, "fan_speed.Dehumidification.value", WindSeedEnum.AUTO
    )
    stored_data, need_save = safe_set_value(
        stored_data, "fan_speed.Fan.value", WindSeedEnum.AUTO
    )
    stored_data, need_save = safe_set_value(
        stored_data, "fan_speed.Auto.value", WindSeedEnum.AUTO
    )

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
                    WindSeedEnum.STRONG if self.data.turbo == 1 else WindSeedEnum.HIGH
                )
            case 5:
                return WindSeedEnum.MID_HIGH
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
