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
    WindSeed7GearEnum
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


def get_SplitAC_Type2_capabilities():
    capabilities = [2,3,7,8,9,11,12,13,21,23,31,33,34,35,36,39,40,41,42,43,48]
    capabilities.sort()
    return capabilities


@dataclass
class TCL_SplitAC_Type2_DeviceData:
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
        # self.turbo = int(delta.get("turbo", aws_thing_state["turbo"]))
        # self.silence_switch = int(
        #     delta.get("silenceSwitch", aws_thing_state["silenceSwitch"])
        # )

        self.wind_speed_auto_switch = int(
            delta.get("windSpeedAutoSwitch", aws_thing_state["windSpeedAutoSwitch"])
        )

        self.wind_speed_7_gear = int(
            delta.get("windSpeed7Gear", aws_thing_state["windSpeed7Gear"])
        )

        self.vertical_direction = int(
            delta.get("verticalDirection", aws_thing_state["verticalDirection"])
        )
        self.horizontal_direction = int(
            delta.get("horizontalDirection", aws_thing_state["horizontalDirection"])
        )

        self.sleep = int(delta.get("sleep", aws_thing_state["sleep"]))
        self.soft_wind = int(delta.get("softWind", aws_thing_state["softWind"]))
        self.ai_eco = int(delta.get("AIECOSwitch", aws_thing_state["AIECOSwitch"]))
        self.healthy = int(delta.get("healthy", aws_thing_state["healthy"]))
        self.anti_moldew = int(delta.get("antiMoldew", aws_thing_state["antiMoldew"]))
        self.self_clean = int(delta.get("selfClean", aws_thing_state["selfClean"]))
        self.screen = int(delta.get("screen", aws_thing_state["screen"]))
        self.eight_add_hot = int(
            delta.get("eightAddHot", aws_thing_state["eightAddHot"])
        )
        self.external_unit_temperature = int(
            delta.get(
                "externalUnitTemperature", aws_thing_state["externalUnitTemperature"]
            )
        )
        self.generator_mode = int(
            delta.get("generatorMode", aws_thing_state["generatorMode"])
        )
        self.device_id = device_id

    device_id: str
    power_switch: int | bool
    beep_switch: int | bool
    target_temperature: int
    current_temperature: int
    high_temperature_wind: int
    wind_speed: int
    vertical_direction: int
    horizontal_direction: int
    sleep: int
    healthy: int
    ai_eco: int
    anti_moldew: int
    self_clean: int
    screen: int
    eight_add_hot: int
    soft_wind: int
    external_unit_temperature: int
    generator_mode: int


async def get_stored_spit_ac_type2_data(
    hass: HomeAssistant, device_id: str
) -> dict[str, any]:
    need_save = False
    stored_data = await get_stored_data(hass, device_id)
    if stored_data is None:
        stored_data = {}
        need_save = True

    stored_data, need_save = safe_set_value(stored_data, "non_user_config.min_celsius_temp", 16)
    stored_data, need_save = safe_set_value(stored_data, "non_user_config.max_celsius_temp", 31)
    stored_data, need_save = safe_set_value(stored_data, "non_user_config.native_temp_step", 1.0)

    stored_data, need_save = safe_set_value(stored_data, "user_config.behavior.memorize_temp_by_mode", True)
    stored_data, need_save = safe_set_value(stored_data, "user_config.behavior.memorize_fan_speed_by_mode", True)
    stored_data, need_save = safe_set_value(stored_data, "user_config.behavior.silent_beep_when_turn_on", False)

    stored_data, need_save = safe_set_value(stored_data, "target_temperature.Cool.value", 24)
    stored_data, need_save = safe_set_value(stored_data, "target_temperature.Heat.value", 36)
    stored_data, need_save = safe_set_value(stored_data, "target_temperature.Dehumidification.value", 24)
    stored_data, need_save = safe_set_value(stored_data, "target_temperature.Fan.value", 24)
    stored_data, need_save = safe_set_value(stored_data, "target_temperature.Auto.value", 24)
    
    stored_data, need_save = safe_set_value(stored_data, "fan_speed.Cool.value", WindSeed7GearEnum.AUTO)
    stored_data, need_save = safe_set_value(stored_data, "fan_speed.Heat.value", WindSeed7GearEnum.AUTO)
    stored_data, need_save = safe_set_value(stored_data, "fan_speed.Dehumidification.value", WindSeed7GearEnum.AUTO)
    stored_data, need_save = safe_set_value(stored_data, "fan_speed.Fan.value", WindSeed7GearEnum.AUTO)
    stored_data, need_save = safe_set_value(stored_data, "fan_speed.Auto.value", WindSeed7GearEnum.AUTO)

    if need_save:
        await set_stored_data(hass, device_id, stored_data)
    return stored_data


class TCL_SplitAC_Type2_DeviceData_Helper:
    def __init__(self, data: TCL_SplitAC_Type2_DeviceData) -> None:
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


"""
Type 2

{
  powerSwitch: 1,
  targetTemperature: 20,
  currentTemperature: 25.1,
  windSpeed7Gear: 1,
  verticalWind: 0,
  horizontalWind: 1,
  horizontalDirection: 1,
  verticalDirection: 8,
  workMode: 1,
  AIECOSwitch: 0,
  regularReporting: 2,
  selfClean: 0,
  screen: 1,
  targetFahrenheitTemp: 68,
  temperatureType: 0,
  sleep: 0,
  beepSwitch: 1,
  softWind: 0,
  antiMoldew: 0,
  generatorMode: 0,
  filterBlockSwitch: 1,
  filterBlockStatus: 0,
  errorCode: [],
  internalUnitCoilTemperature: 8,
  capabilities: [
     2,  3,  7,  8,  9, 11, 12,
    13, 21, 23, 31, 33, 34, 35,
    36, 39, 40, 41, 42, 43, 48
  ],
  PTCStatus: 0,
  externalUnitTemperature: 32,
  externalUnitFanSpeed: 700,
  compressorFrequency: 0,
  windSpeedPercentage: 1,
  windSpeedAutoSwitch: 0,
  selfCleanStatus: 6,
  selfCleanPercentage: 0,
  healthy: 0,
  AIECOStatus: 0,
  OutDoorCompTarFreqSet: 0,
  OutDoorFanTarSpeed: 0,
  OutDoorEEVTarOpenDegree: 0,
  OutDoorCompTarFreqRun: 40,
  weekTimer1: ';;;;;;;',
  weekTimer2: ';;;;;;;',
  eightAddHot: 0,
  accessCardInsert: 1,
  lowerTemperatureLimit: 16,
  upperTemperatureLimit: 31,
  specialTimer: ';',
  highTemperatureWind: 0,
  coolFeelWind: 0,
  authFlag: { google: true }
}


min/max temp: 16 / 31

Teamp step 1.0

{"state":{"desired":{"eightAddHot":0,"targetTemperature":20,"targetFahrenheitTemp":68}},"clientToken":"mobile_1753013249008"}

Mode to heat:
{"state":{"desired":{"eightAddHot":0,"windSpeedAutoSwitch":1,"workMode":4,"targetTemperature":26,"targetFahrenheitTemp":79,"windSpeed7Gear":0}},"clientToken":"mobile_1753013293857"}
Mode to dry:
{"state":{"desired":{"eightAddHot":0,"windSpeedAutoSwitch":0,"workMode":2,"targetTemperature":26,"targetFahrenheitTemp":79,"windSpeed7Gear":2}},"clientToken":"mobile_1753013314535"}
Mode to fan:
{"state":{"desired":{"eightAddHot":0,"windSpeedAutoSwitch":1,"workMode":3,"targetTemperature":26,"targetFahrenheitTemp":79,"windSpeed7Gear":0}},"clientToken":"mobile_1753013352848"}
Mode to auto:
{"state":{"desired":{"eightAddHot":0,"windSpeedAutoSwitch":1,"workMode":0,"targetTemperature":26,"targetFahrenheitTemp":79,"windSpeed7Gear":0}},"clientToken":"mobile_1753013379306"}
Mode to cool:
{"state":{"desired":{"eightAddHot":0,"windSpeedAutoSwitch":1,"workMode":1,"targetTemperature":20,"targetFahrenheitTemp":68,"windSpeed7Gear":0}},"clientToken":"mobile_1753013445257"}

Set temperature by mode when change mode
Set Fan speed by mode when change mode




"""
