"""."""

from dataclasses import dataclass
from enum import StrEnum

from .device_ac_common import (
    LeftAndRightAirSupplyVectorEnum,
    getLeftAndRightAirSupplyVector,
    UpAndDownAirSupplyVectorEnum,
    getUpAndDownAirSupplyVector,
    ModeEnum,
    getMode,
    SleepModeEnum,
    getSleepMode,
)

"""
{
  temperatureType: 0,
  horizontalWind: 0,
  verticalWind: 0,
  lightSense: 1,
  filterBlockStatus: 0,
  errorCode: [],
  externalUnitVoltage: 0,
  externalUnitElectricCurrent: 0,
  internalUnitFanSpeed: 0,
  PTCStatus: 0,
  externalUnitTemperature: 0,
  externalUnitCoilTemperature: 0,
  externalUnitExhaustTemperature: 0,
  externalUnitFanGear: 0,
  externalUnitFanSpeed: 0,
  compressorFrequency: 0,
  fourWayValveStatus: 0,
  expansionValve: 0,
  FreshAirStatus: 0,
  newWindPercentage: 33,
  windSpeedPercentage: 0,
  selfCleanStatus: 6,
  internalUnitFanCurrentGear: 0,
  lightSenserStatus: 0,
  otaStatus: 1
}
"""


class WindSeed7GearEnum(StrEnum):
    NONE = "Not set"
    TURBO = "Turbo"
    AUTO = "Auto"
    SPEED_1 = "1"
    SPEED_2 = "2"
    SPEED_3 = "3"
    SPEED_4 = "4"
    SPEED_5 = "5"
    SPEED_6 = "6"


@dataclass
class TCL_SplitAC_Fresh_Air_DeviceData:
    def __init__(self, device_id: str, aws_thing_state: dict, delta: dict) -> None:
        self.beep_switch = int(delta.get("beepSwitch", aws_thing_state["beepSwitch"]))
        self.power_switch = int(
            delta.get("powerSwitch", aws_thing_state["powerSwitch"])
        )
        self.target_temperature = float(
            delta.get("targetTemperature", aws_thing_state["targetTemperature"])
        )
        self.current_temperature = float(
            delta.get("currentTemperature", aws_thing_state["currentTemperature"])
        )
        self.internal_unit_coil_temperature = float(
            delta.get(
                "internalUnitCoilTemperature",
                aws_thing_state["internalUnitCoilTemperature"],
            )
        )
        self.work_mode = int(delta.get("workMode", aws_thing_state["workMode"]))

        self.vertical_direction = int(
            delta.get("verticalDirection", aws_thing_state["verticalDirection"])
        )

        self.horizontal_direction = int(
            delta.get("horizontalDirection", aws_thing_state["horizontalDirection"])
        )

        self.wind_speed_auto_switch = int(
            delta.get("windSpeedAutoSwitch", aws_thing_state["windSpeedAutoSwitch"])
        )

        self.wind_speed_7_gear = int(
            delta.get("windSpeed7Gear", aws_thing_state["windSpeed7Gear"])
        )

        self.new_wind_switch = int(
            delta.get("newWindSwitch", aws_thing_state["newWindSwitch"])
        )
        self.new_wind_auto_switch = int(
            delta.get("newWindAutoSwitch", aws_thing_state["newWindAutoSwitch"])
        )
        self.new_wind_strength = int(
            delta.get("newWindStrength", aws_thing_state["newWindStrength"])
        )
        self.soft_wind = int(delta.get("softWind", aws_thing_state["softWind"]))
        self.generator_mode = int(
            delta.get("generatorMode", aws_thing_state["generatorMode"])
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
    target_temperature: float
    current_temperature: float
    internal_unit_coil_temperature: float
    vertical_direction: int
    horizontal_direction: int
    sleep: int
    healthy: int
    eco: int
    anti_moldew: int
    self_clean: int
    screen: int
    wind_speed_auto_switch: int
    wind_speed_7_gear: int
    new_wind_switch: int
    new_wind_auto_switch: int
    new_wind_strength: int
    soft_wind: int
    generator_mode: int


class TCL_SplitAC_Fresh_Air_DeviceData_Helper:
    def __init__(self, data: TCL_SplitAC_Fresh_Air_DeviceData) -> None:
        self.data = data

    def getMode(self) -> ModeEnum:
        return getMode(self.data.work_mode)

    def getFanSpeed(self) -> WindSeed7GearEnum:
        match self.data.wind_speed_7_gear:
            case 1:
                return WindSeed7GearEnum.SPEED_1
            case 2:
                return WindSeed7GearEnum.SPEED_2
            case 3:
                return WindSeed7GearEnum.SPEED_3
            case 4:
                return WindSeed7GearEnum.SPEED_4
            case 5:
                return WindSeed7GearEnum.SPEED_5
            case 6:
                return WindSeed7GearEnum.SPEED_6
            case 7:
                return WindSeed7GearEnum.TURBO
            case 0:
                if self.data.wind_speed_auto_switch == 1:
                    return WindSeed7GearEnum.AUTO
                return WindSeed7GearEnum.NONE
            case _:
                return WindSeed7GearEnum.NONE

    def getUpAndDownAirSupplyVector(self) -> UpAndDownAirSupplyVectorEnum:
        return getUpAndDownAirSupplyVector(self.data.vertical_direction)

    def getLeftAndRightAirSupplyVector(self) -> LeftAndRightAirSupplyVectorEnum:
        return getLeftAndRightAirSupplyVector(self.data.horizontal_direction)

    def getSleepMode(self) -> SleepModeEnum:
        return getSleepMode(self.data.sleep)


"""

FAn to turbo
{"state":{"desired":{"windSpeedAutoSwitch":0,"windSpeed7Gear":7}},"clientToken":"mobile_1752575376456"}
Fan to auto
{"state":{"desired":{"windSpeedAutoSwitch":1,"windSpeed7Gear":0}},"clientToken":"mobile_1752575392037"}
Fa to 1
{"state":{"desired":{"windSpeedAutoSwitch":0,"windSpeed7Gear":1}},"clientToken":"mobile_1752575406578"}
2-6
{"state":{"desired":{"windSpeedAutoSwitch":0,"windSpeed7Gear":2}},"clientToken":"mobile_1752575420675"}
{"state":{"desired":{"windSpeedAutoSwitch":0,"windSpeed7Gear":3}},"clientToken":"mobile_1752575431138"}
{"state":{"desired":{"windSpeedAutoSwitch":0,"windSpeed7Gear":4}},"clientToken":"mobile_1752575439008"}
{"state":{"desired":{"windSpeedAutoSwitch":0,"windSpeed7Gear":5}},"clientToken":"mobile_1752575450022"}
{"state":{"desired":{"windSpeedAutoSwitch":0,"windSpeed7Gear":6}},"clientToken":"mobile_1752575459038"}
Freash air toogle
{"state":{"desired":{"newWindSwitch":1,"selfClean":0}},"clientToken":"mobile_1752575483171"}
fresh air auto
{"state":{"desired":{"newWindAutoSwitch":1,"newWindStrength":0}},"clientToken":"mobile_1752575502900"}
fresh air 1
{"state":{"desired":{"newWindAutoSwitch":0,"newWindStrength":1}},"clientToken":"mobile_1752575527454"}
2-3
{"state":{"desired":{"newWindAutoSwitch":0,"newWindStrength":2}},"clientToken":"mobile_1752575541330"}
{"state":{"desired":{"newWindAutoSwitch":0,"newWindStrength":3}},"clientToken":"mobile_1752575545013"}
Wind feeling
{"state":{"desired":{"horizontalDirection":8,"softWind":1}},"clientToken":"mobile_1752575563957"} (soft)
WF - shower
{"state":{"desired":{"horizontalDirection":8,"softWind":2,"verticalDirection":9}},"clientToken":"mobile_1752575659254"}
András
 —
12:35
WF - Carpet
{"state":{"desired":{"horizontalDirection":8,"softWind":3,"verticalDirection":13}},"clientToken":"mobile_1752575685738"}
WF - Surround
{"state":{"desired":{"softWind":4,"verticalDirection":8}},"clientToken":"mobile_1752575725894"}
Air flow
top fix
{"state":{"desired":{"verticalDirection":9}},"clientToken":"mobile_1752575881474"}
upper fix
{"state":{"desired":{"verticalDirection":10}},"clientToken":"mobile_1752575903284"}
midle fix
{"state":{"desired":{"verticalDirection":11}},"clientToken":"mobile_1752575916018"}
lower fix
{"state":{"desired":{"verticalDirection":12}},"clientToken":"mobile_1752575932386"}
bottom fix
{"state":{"desired":{"verticalDirection":13}},"clientToken":"mobile_1752575944060"}
upwards swing
{"state":{"desired":{"verticalDirection":2}},"clientToken":"mobile_1752575968057"}
downward swing
{"state":{"desired":{"verticalDirection":3}},"clientToken":"mobile_1752575994933"}
up and down swing
{"state":{"desired":{"verticalDirection":1}},"clientToken":"mobile_1752576032832"}
András
 —
12:42
Horizontal air flows
Left swing
{"state":{"desired":{"horizontalDirection":2}},"clientToken":"mobile_1752576115298"}
LEft and right swing
{"state":{"desired":{"horizontalDirection":1}},"clientToken":"mobile_1752576136149"}
Right swing
{"state":{"desired":{"horizontalDirection":4}},"clientToken":"mobile_1752576148366"}
LEft fix
{"state":{"desired":{"horizontalDirection":9}},"clientToken":"mobile_1752576168165"}
center left fix
{"state":{"desired":{"horizontalDirection":10}},"clientToken":"mobile_1752576182199"}
midle fix
{"state":{"desired":{"horizontalDirection":11}},"clientToken":"mobile_1752576195352"}
center right-fix
{"state":{"desired":{"horizontalDirection":12}},"clientToken":"mobile_1752576203784"}
right fix
{"state":{"desired":{"horizontalDirection":13}},"clientToken":"mobile_1752576218467"}
eco
{"state":{"desired":{"ECO":1}},"clientToken":"mobile_1752576233454"}
sleep standard
{"state":{"desired":{"sleep":1}},"clientToken":"mobile_1752576248420"}
elder:
{"state":{"desired":{"sleep":2}},"clientToken":"mobile_1752576291181"}
child:
{"state":{"desired":{"sleep":3}},"clientToken":"mobile_1752576291181"}
Health
{"state":{"desired":{"healthy":1}},"clientToken":"mobile_1752576347550"}
Midewproof
{"state":{"desired":{"antiMoldew":1}},"clientToken":"mobile_1752576368148"}
Self clean:
{"state":{"desired":{"powerSwitch":0,"selfClean":1}},"clientToken":"mobile_1752576436154"}
GEN mode
L1  30%
{"state":{"desired":{"generatorMode":1}},"clientToken":"mobile_1752576474816"}
L2 50%
{"state":{"desired":{"generatorMode":2}},"clientToken":"mobile_1752576496998"}
L3 70%
{"state":{"desired":{"generatorMode":3}},"clientToken":"mobile_1752576508926"}
Gen mode close
{"state":{"desired":{"generatorMode":0}},"clientToken":"mobile_1752576527102"}

"""
