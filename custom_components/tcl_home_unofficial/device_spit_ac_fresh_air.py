"""."""

from homeassistant.core import HomeAssistant
from .device_data_storage import get_stored_data, set_stored_data
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


class WindSeed7GearEnum(StrEnum):
    TURBO = "Turbo"
    AUTO = "Auto"
    SPEED_1 = "1"
    SPEED_2 = "2"
    SPEED_3 = "3"
    SPEED_4 = "4"
    SPEED_5 = "5"
    SPEED_6 = "6"


class FreshAirEnum(StrEnum):
    OFF = "Off"
    ON = "On"
    AUTO = "Auto"
    STRENGTH_1 = "1"
    STRENGTH_2 = "2"
    STRENGTH_3 = "3"


class WindFeelingEnum(StrEnum):
    NONE = "Not set"
    SOFT = "Soft"
    SHOWER = "Shower"
    CARPET = "Carpet"
    SURROUND = "Surround"


class GeneratorModeEnum(StrEnum):
    NONE = "Not set"
    L1 = "L1 30%"
    L2 = "L1 50%"
    L3 = "L1 70%"


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
        self.light_sense = int(delta.get("lightSense", aws_thing_state["lightSense"]))
        self.external_unit_coil_temperature = int(
            delta.get(
                "externalUnitCoilTemperature",
                aws_thing_state["externalUnitCoilTemperature"],
            )
        )
        self.external_unit_temperature = int(
            delta.get(
                "externalUnitTemperature", aws_thing_state["externalUnitTemperature"]
            )
        )
        self.external_unit_exhaust_temperature = int(
            delta.get(
                "externalUnitExhaustTemperature",
                aws_thing_state["externalUnitExhaustTemperature"],
            )
        )
        self.device_id = device_id

    device_id: str
    power_switch: int | bool
    beep_switch: int | bool
    target_temperature: float
    current_temperature: float
    internal_unit_coil_temperature: float
    external_unit_coil_temperature: float
    external_unit_exhaust_temperature: float
    external_unit_temperature: float
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
    light_sense: int


async def get_stored_spit_ac_fresh_data(
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


class TCL_SplitAC_Fresh_Air_DeviceData_Helper:
    def __init__(self, data: TCL_SplitAC_Fresh_Air_DeviceData) -> None:
        self.data = data

    def getMode(self) -> ModeEnum:
        return getMode(self.data.work_mode)

    def getWindSeed7Gear(self) -> WindSeed7GearEnum:
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
                return WindSeed7GearEnum.AUTO
            case _:
                return WindSeed7GearEnum.AUTO

    def getUpAndDownAirSupplyVector(self) -> UpAndDownAirSupplyVectorEnum:
        return getUpAndDownAirSupplyVector(self.data.vertical_direction)

    def getLeftAndRightAirSupplyVector(self) -> LeftAndRightAirSupplyVectorEnum:
        return getLeftAndRightAirSupplyVector(self.data.horizontal_direction)

    def getSleepMode(self) -> SleepModeEnum:
        return getSleepMode(self.data.sleep)

    def getFreshAir(self) -> FreshAirEnum:
        match self.data.new_wind_strength:
            case 1:
                return FreshAirEnum.STRENGTH_1
            case 2:
                return FreshAirEnum.STRENGTH_2
            case 3:
                return FreshAirEnum.STRENGTH_3
            case 0:
                if self.data.new_wind_switch == 0:
                    return FreshAirEnum.OFF
                else:
                    if self.data.new_wind_auto_switch == 1:
                        return FreshAirEnum.AUTO
                    else:
                        return FreshAirEnum.ON
            case _:
                return FreshAirEnum.OFF

    def getWindFeeling(self) -> WindFeelingEnum:
        match self.data.soft_wind:
            case 1:
                return WindFeelingEnum.SOFT
            case 2:
                return WindFeelingEnum.SHOWER
            case 3:
                return WindFeelingEnum.CARPET
            case 3:
                return WindFeelingEnum.SURROUND
            case 0:
                return WindFeelingEnum.NONE
            case _:
                return WindFeelingEnum.NONE

    def getGeneratorMode(self) -> GeneratorModeEnum:
        match self.data.generator_mode:
            case 1:
                return GeneratorModeEnum.L1
            case 2:
                return GeneratorModeEnum.L2
            case 3:
                return GeneratorModeEnum.L3
            case 0:
                return GeneratorModeEnum.NONE
