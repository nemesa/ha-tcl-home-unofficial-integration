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
    stored_data = await get_stored_data(hass, device_id)
    if stored_data is None:
        stored_data = {
            "target_temperature": {
                "Cool": 24,
                "Heat": 26,
                "Dehumidification": 24,
                "Fan": 24,
                "Auto": 24,
            }
        }
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

FAN seepd:
1: {"state":{"desired":{"windSpeedAutoSwitch":0,"windSpeed7Gear":1}},"clientToken":"mobile_1753013593742"}
6: {"state":{"desired":{"windSpeedAutoSwitch":0,"windSpeed7Gear":6}},"clientToken":"mobile_1753013639226"}
7: {"state":{"desired":{"windSpeedAutoSwitch":0,"softWind":0,"windSpeed7Gear":7}},"clientToken":"mobile_1753013650563"}


Airflow direction:
left and right swing:
{"state":{"desired":{"horizontalDirection":2}},"clientToken":"mobile_1753013672235"}

upper fix:
{"state":{"desired":{"verticalDirection":10}},"clientToken":"mobile_1753013715203"}

beep switch:
{"state":{"desired":{"beepSwitch":0}},"clientToken":"mobile_1753013332621"}


soft wind:
on:{"state":{"desired":{"softWind":1}},"clientToken":"mobile_1753013757741"}
off:{"state":{"desired":{"softWind":0}},"clientToken":"mobile_1753013888307"}

AI ECO:
on: {"state":{"desired":{"eightAddHot":0,"targetTemperature":26,"AIECOSwitch":1}},"clientToken":"mobile_1753013783602"}
on: {"state":{"desired":{"eightAddHot":0,"AIECOSwitch":1}},"clientToken":"mobile_1753013939736"}
off:{"state":{"desired":{"eightAddHot":0,"AIECOSwitch":0}},"clientToken":"mobile_1753014006572"}

Sleep elder:
{"state":{"desired":{"sleep":2}},"clientToken":"mobile_1753013811820"}


GEN mode:
L1: {"state":{"desired":{"generatorMode":1}},"clientToken":"mobile_1753014090761"}
L2: {"state":{"desired":{"generatorMode":2}},"clientToken":"mobile_1753014090761"}
L3: {"state":{"desired":{"generatorMode":3}},"clientToken":"mobile_1753014090761"}

Healthy:
{"state":{"desired":{"healthy":1}},"clientToken":"mobile_1753014177202"}
{"state":{"desired":{"healthy":0}},"clientToken":"mobile_1753014200934"}

drying:
{"state":{"desired":{"antiMoldew":1}},"clientToken":"mobile_1753014211729"}
{"state":{"desired":{"antiMoldew":0}},"clientToken":"mobile_1753014213517"}

8C heating:
{"state":{"desired":{"eightAddHot":0}},"clientToken":"mobile_1753014310543"}
{"state":{"desired":{"eightAddHot":1}},"clientToken":"mobile_1753014312826"}


8C heating:
teamperature disabled
soft wind disabled
mildewproof disabled



Mode Heat/ Fan / Auto:
Mildewproof disabled

"""
