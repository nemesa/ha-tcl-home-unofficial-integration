"""."""

from homeassistant.core import HomeAssistant
from .device_data_storage import get_stored_data, set_stored_data, safe_set_value
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
    WindSeed7GearEnum,
)





class FreshAirEnum(StrEnum):
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
    need_save = False
    stored_data = await get_stored_data(hass, device_id)
    if stored_data is None:
        stored_data = {}
        need_save = True

    stored_data, need_save = safe_set_value(stored_data, "non_user_config.min_celsius_temp", 16)
    stored_data, need_save = safe_set_value(stored_data, "non_user_config.max_celsius_temp", 31)
    stored_data, need_save = safe_set_value(stored_data, "non_user_config.native_temp_step", 0.5)

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


class TCL_SplitAC_Fresh_Air_DeviceData_Helper:
    def __init__(self, data: TCL_SplitAC_Fresh_Air_DeviceData) -> None:
        self.data = data

    def getMode(self) -> ModeEnum:
        return getMode(self.data.work_mode)

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
                return FreshAirEnum.AUTO
            case _:
                return FreshAirEnum.AUTO

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
