"""."""

from enum import StrEnum
import logging

from .device_capabilities import DeviceCapabilityEnum
from .device_types import DeviceTypeEnum

_LOGGER = logging.getLogger(__name__)


class ASDF(StrEnum):
    CAPABILITY_SOFT_WIND = "5"
    CAPABILITY_8C_HEATING = "21"
    CAPABILITY_GENERATOR_MODE = "23"


class DeviceFeatureEnum(StrEnum):
    MODE_HEAT = "mode.heat"
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
    SWITCH_AI_ECO = "switch.AIeco"
    SWITCH_HEALTHY = "switch.healthy"
    SWITCH_DRYING = "switch.drying"
    SWITCH_SCREEN = "switch.screen"
    SWITCH_LIGHT_SENSE = "switch.lightSense"
    SWITCH_SWING_WIND = "switch.swingWind"
    SWITCH_SLEEP = "switch.sleep"
    SWITCH_8_C_HEATING = "switch.8CHeating"
    SWITCH_SOFT_WIND = "switch.softWind"
    SWITCH_FRESH_AIR = "switch.freshAir"
    SELECT_MODE = "select.mode"
    SELECT_WIND_SPEED = "select.windSpeed"
    SELECT_WIND_SPEED_7_GEAR = "select.windSpeed7Gear"
    SELECT_WIND_FEELING = "select.windFeeling"
    SELECT_VERTICAL_DIRECTION = "select.verticalDirection"
    SELECT_HORIZONTAL_DIRECTION = "select.horizontalDirection"
    SELECT_SLEEP_MODE = "select.sleepMode"
    SELECT_FRESH_AIR = "select.freshAir"
    SELECT_GENERATOR_MODE = "select.generatorMode"
    SELECT_TEMPERATURE_TYPE = "select.temperatureType"
    SELECT_PORTABLE_WIND_SEED = "select.portableWindSeed"
    NUMBER_TARGET_DEGREE = "number.targetDegree"
    NUMBER_TARGET_TEMPERATURE = "number.targetTemperature"
    NUMBER_TARGET_TEMPERATURE_ALLOW_HALF_DIGITS = (
        "number.targetTemperature.allow_half_digits"
    )
    BUTTON_SELF_CLEAN = "button.selfClean"
    CLIMATE = "climate"
    INTERNAL_HAS_SWING_SWITCH = "internal.hasSwingSwitch"
    INTERNAL_SET_TFT_WITH_TT = (
        "internal.set_targetFahrenheitTemp_with_targetTemperature"
    )
    USER_CONFIG_BEHAVIOR_MEMORIZE_TEMP_BY_MODE = (
        "user_config.behavior.memorize_temp_by_mode"
    )
    USER_CONFIG_BEHAVIOR_MEMORIZE_FAN_SPEED_BY_MODE = (
        "user_config.behavior.memorize_fan_speed_by_mode"
    )
    USER_CONFIG_BEHAVIOR_SILENT_BEEP_WHEN_TURN_ON = (
        "user_config.behavior.silent_beep_when_turn_on"
    )


def getSupportedFeatures(
    device_type: DeviceTypeEnum, aws_thing_state_reported: dict[str, any]
) -> list[DeviceFeatureEnum]:
    capabilities = aws_thing_state_reported.get("capabilities", [])
    aws_data_windSpeed7Gear = aws_thing_state_reported.get("windSpeed7Gear", -1)
    has_windSpeed7Gear = True if aws_data_windSpeed7Gear != -1 else False
    


    match device_type:
        case DeviceTypeEnum.SPLIT_AC_TYPE_1:
            features = [
                DeviceFeatureEnum.MODE_HEAT,
                DeviceFeatureEnum.SENSOR_CURRENT_TEMPERATURE,
                DeviceFeatureEnum.SWITCH_POWER,
                DeviceFeatureEnum.SWITCH_BEEP,
                DeviceFeatureEnum.SWITCH_ECO,
                DeviceFeatureEnum.SWITCH_HEALTHY,
                DeviceFeatureEnum.SWITCH_DRYING,
                DeviceFeatureEnum.SWITCH_SCREEN,
                DeviceFeatureEnum.SELECT_MODE,
                DeviceFeatureEnum.SELECT_WIND_SPEED,
                DeviceFeatureEnum.SELECT_VERTICAL_DIRECTION,
                DeviceFeatureEnum.SELECT_HORIZONTAL_DIRECTION,
                DeviceFeatureEnum.SELECT_SLEEP_MODE,
                DeviceFeatureEnum.NUMBER_TARGET_TEMPERATURE,
                DeviceFeatureEnum.BUTTON_SELF_CLEAN,
                DeviceFeatureEnum.CLIMATE,
                DeviceFeatureEnum.INTERNAL_HAS_SWING_SWITCH,
                DeviceFeatureEnum.USER_CONFIG_BEHAVIOR_MEMORIZE_TEMP_BY_MODE,
                DeviceFeatureEnum.USER_CONFIG_BEHAVIOR_MEMORIZE_FAN_SPEED_BY_MODE,
                DeviceFeatureEnum.USER_CONFIG_BEHAVIOR_SILENT_BEEP_WHEN_TURN_ON,
            ]
            if len(capabilities) > 0:
                if DeviceCapabilityEnum.CAPABILITY_SOFT_WIND in capabilities:
                    features.append(DeviceFeatureEnum.SWITCH_SOFT_WIND)
                if DeviceCapabilityEnum.CAPABILITY_8C_HEATING in capabilities:
                    features.append(DeviceFeatureEnum.SWITCH_8_C_HEATING)
                if DeviceCapabilityEnum.CAPABILITY_GENERATOR_MODE in capabilities:
                    features.append(DeviceFeatureEnum.SELECT_GENERATOR_MODE)
            return features
        case DeviceTypeEnum.SPLIT_AC_TYPE_2:
            return [
                DeviceFeatureEnum.MODE_HEAT,
                DeviceFeatureEnum.SENSOR_CURRENT_TEMPERATURE,
                DeviceFeatureEnum.SENSOR_EXTERNAL_UNIT_TEMPERATURE,
                DeviceFeatureEnum.SWITCH_POWER,
                DeviceFeatureEnum.SWITCH_BEEP,
                DeviceFeatureEnum.SWITCH_AI_ECO,
                DeviceFeatureEnum.SWITCH_HEALTHY,
                DeviceFeatureEnum.SWITCH_DRYING,
                DeviceFeatureEnum.SWITCH_SCREEN,
                DeviceFeatureEnum.SWITCH_8_C_HEATING,
                DeviceFeatureEnum.SWITCH_SOFT_WIND,
                DeviceFeatureEnum.SELECT_MODE,
                DeviceFeatureEnum.SELECT_WIND_SPEED_7_GEAR,
                DeviceFeatureEnum.SELECT_VERTICAL_DIRECTION,
                DeviceFeatureEnum.SELECT_HORIZONTAL_DIRECTION,
                DeviceFeatureEnum.SELECT_SLEEP_MODE,
                DeviceFeatureEnum.NUMBER_TARGET_TEMPERATURE,
                DeviceFeatureEnum.SELECT_GENERATOR_MODE,
                DeviceFeatureEnum.BUTTON_SELF_CLEAN,
                DeviceFeatureEnum.CLIMATE,
                DeviceFeatureEnum.INTERNAL_SET_TFT_WITH_TT,
                DeviceFeatureEnum.USER_CONFIG_BEHAVIOR_MEMORIZE_TEMP_BY_MODE,
                DeviceFeatureEnum.USER_CONFIG_BEHAVIOR_MEMORIZE_FAN_SPEED_BY_MODE,
                DeviceFeatureEnum.USER_CONFIG_BEHAVIOR_SILENT_BEEP_WHEN_TURN_ON,
            ]
        case DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
            return [
                DeviceFeatureEnum.MODE_HEAT,
                DeviceFeatureEnum.SENSOR_CURRENT_TEMPERATURE,
                DeviceFeatureEnum.SENSOR_INTERNAL_UNIT_COIL_TEMPERATURE,
                DeviceFeatureEnum.SENSOR_EXTERNAL_UNIT_COIL_TEMPERATURE,
                DeviceFeatureEnum.SENSOR_EXTERNAL_UNIT_TEMPERATURE,
                DeviceFeatureEnum.SENSOR_EXTERNAL_UNIT_EXHAUST_TEMPERATURE,
                DeviceFeatureEnum.SWITCH_POWER,
                DeviceFeatureEnum.SWITCH_BEEP,
                DeviceFeatureEnum.SWITCH_ECO,
                DeviceFeatureEnum.SWITCH_HEALTHY,
                DeviceFeatureEnum.SWITCH_DRYING,
                DeviceFeatureEnum.SWITCH_SCREEN,
                DeviceFeatureEnum.SWITCH_LIGHT_SENSE,
                DeviceFeatureEnum.SWITCH_FRESH_AIR,
                DeviceFeatureEnum.SELECT_MODE,
                DeviceFeatureEnum.SELECT_VERTICAL_DIRECTION,
                DeviceFeatureEnum.SELECT_HORIZONTAL_DIRECTION,
                DeviceFeatureEnum.SELECT_SLEEP_MODE,
                DeviceFeatureEnum.SELECT_WIND_SPEED_7_GEAR,
                DeviceFeatureEnum.SELECT_WIND_FEELING,
                DeviceFeatureEnum.SELECT_FRESH_AIR,
                DeviceFeatureEnum.SELECT_GENERATOR_MODE,
                DeviceFeatureEnum.NUMBER_TARGET_TEMPERATURE,
                DeviceFeatureEnum.NUMBER_TARGET_TEMPERATURE_ALLOW_HALF_DIGITS,
                DeviceFeatureEnum.BUTTON_SELF_CLEAN,
                DeviceFeatureEnum.CLIMATE,
                DeviceFeatureEnum.USER_CONFIG_BEHAVIOR_MEMORIZE_TEMP_BY_MODE,
                DeviceFeatureEnum.USER_CONFIG_BEHAVIOR_MEMORIZE_FAN_SPEED_BY_MODE,
                DeviceFeatureEnum.USER_CONFIG_BEHAVIOR_SILENT_BEEP_WHEN_TURN_ON,
            ]
        case DeviceTypeEnum.PORTABLE_AC:
            return [
                DeviceFeatureEnum.SWITCH_POWER,
                DeviceFeatureEnum.SWITCH_SWING_WIND,
                DeviceFeatureEnum.SWITCH_SLEEP,
                DeviceFeatureEnum.SELECT_MODE,
                DeviceFeatureEnum.SELECT_PORTABLE_WIND_SEED,
                DeviceFeatureEnum.NUMBER_TARGET_DEGREE,
            ]
        case _:
            return []
