"""."""

from enum import StrEnum
import logging

from .device_capabilities import DeviceCapabilityEnum
from .device_types import DeviceTypeEnum

_LOGGER = logging.getLogger(__name__)


class DeviceFeatureEnum(StrEnum):
    MODE_AUTO = "mode.auto"
    MODE_COOL = "mode.cool"
    MODE_DEHUMIDIFICATION = "mode.dehumidification"
    MODE_FAN = "mode.fan"
    MODE_HEAT = "mode.heat"
    SENSOR_IS_ONLINE = "sensor.is_online"
    SENSOR_CURRENT_TEMPERATURE = "sensor.current_temperature"
    SENSOR_INTERNAL_UNIT_COIL_TEMPERATURE = "sensor.internal_unit_coil_temperature"
    SENSOR_EXTERNAL_UNIT_COIL_TEMPERATURE = "sensor.external_unit_coil_temperature"
    SENSOR_EXTERNAL_UNIT_TEMPERATURE = "sensor.external_unit_temperature"
    SENSOR_EXTERNAL_UNIT_EXHAUST_TEMPERATURE = "sensor.external_unit_exhaust_temperature"
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
    SELECT_PORTABLE_WIND_SPEED = "select.portableWindSpeed"
    SELECT_WINDOW_AS_WIND_SPEED = "select.WindowAcWindSpeed"
    NUMBER_TARGET_DEGREE = "number.targetDegree"
    NUMBER_TARGET_TEMPERATURE = "number.targetTemperature"
    NUMBER_TARGET_TEMPERATURE_ALLOW_HALF_DIGITS = "number.targetTemperature.allow_half_digits"
    BUTTON_SELF_CLEAN = "button.selfClean"
    CLIMATE = "climate"
    INTERNAL_HAS_SWING_SWITCH = "internal.hasSwingSwitch"
    INTERNAL_HAS_TURBO_PROPERTY = "internal.has_turbo_property"
    INTERNAL_HAS_HIGHTEMPERATUREWIND_PROPERTY = "internal.has_highTemperatureWind_property"
    INTERNAL_HAS_SILENCESWITCH_PROPERTY = "internal.has_silenceSwitch_property"
    INTERNAL_SET_TFT_WITH_TT = "internal.set_targetFahrenheitTemp_with_targetTemperature"
    USER_CONFIG_BEHAVIOR_MEMORIZE_TEMP_BY_MODE = "user_config.behavior.memorize_temp_by_mode"
    USER_CONFIG_BEHAVIOR_MEMORIZE_FAN_SPEED_BY_MODE = "user_config.behavior.memorize_fan_speed_by_mode"
    USER_CONFIG_BEHAVIOR_SILENT_BEEP_WHEN_TURN_ON = "user_config.behavior.silent_beep_when_turn_on"


def has_property(aws_thing_state_reported: dict[str, any], propertyName: str) -> bool:
    return propertyName in aws_thing_state_reported


def getSupportedFeatures(
    device_type: DeviceTypeEnum, aws_thing_state_reported: dict[str, any]
) -> list[DeviceFeatureEnum]:
    capabilities = aws_thing_state_reported.get("capabilities", [])

    match device_type:
        case DeviceTypeEnum.SPLIT_AC:
            features = [
                DeviceFeatureEnum.MODE_AUTO,
                DeviceFeatureEnum.MODE_COOL,
                DeviceFeatureEnum.MODE_DEHUMIDIFICATION,
                DeviceFeatureEnum.MODE_FAN,
                DeviceFeatureEnum.MODE_HEAT,
                DeviceFeatureEnum.SENSOR_CURRENT_TEMPERATURE,
                DeviceFeatureEnum.SENSOR_IS_ONLINE,
                DeviceFeatureEnum.SWITCH_POWER,
                DeviceFeatureEnum.SWITCH_BEEP,
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

            if has_property(aws_thing_state_reported, "ECO"):
                features.append(DeviceFeatureEnum.SWITCH_ECO)

            if has_property(aws_thing_state_reported, "windSpeed"):
                features.append(DeviceFeatureEnum.SELECT_WIND_SPEED)

            if has_property(aws_thing_state_reported, "verticalSwitch") and has_property(aws_thing_state_reported, "horizontalSwitch"):
                features.append(DeviceFeatureEnum.INTERNAL_HAS_SWING_SWITCH)
                        
            if has_property(aws_thing_state_reported, "turbo"):
                features.append(DeviceFeatureEnum.INTERNAL_HAS_TURBO_PROPERTY)
                
            if has_property(aws_thing_state_reported, "silenceSwitch"):
                features.append(DeviceFeatureEnum.INTERNAL_HAS_SILENCESWITCH_PROPERTY)
                
            if has_property(aws_thing_state_reported, "highTemperatureWind"):
                features.append(DeviceFeatureEnum.INTERNAL_HAS_HIGHTEMPERATUREWIND_PROPERTY)

            if has_property(aws_thing_state_reported, "windSpeed7Gear"):
                features.append(DeviceFeatureEnum.SELECT_WIND_SPEED_7_GEAR)

            if has_property(aws_thing_state_reported, "externalUnitTemperature"):
                features.append(DeviceFeatureEnum.SENSOR_EXTERNAL_UNIT_TEMPERATURE)

            if has_property(aws_thing_state_reported, "AIECOSwitch"):
                features.append(DeviceFeatureEnum.SWITCH_AI_ECO)

            if has_property(aws_thing_state_reported, "targetFahrenheitTemp"):
                features.append(DeviceFeatureEnum.INTERNAL_SET_TFT_WITH_TT)

            return features
        case DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
            return [
                DeviceFeatureEnum.MODE_AUTO,
                DeviceFeatureEnum.MODE_COOL,
                DeviceFeatureEnum.MODE_DEHUMIDIFICATION,
                DeviceFeatureEnum.MODE_FAN,
                DeviceFeatureEnum.MODE_HEAT,
                DeviceFeatureEnum.SENSOR_CURRENT_TEMPERATURE,
                DeviceFeatureEnum.SENSOR_INTERNAL_UNIT_COIL_TEMPERATURE,
                DeviceFeatureEnum.SENSOR_EXTERNAL_UNIT_COIL_TEMPERATURE,
                DeviceFeatureEnum.SENSOR_EXTERNAL_UNIT_TEMPERATURE,
                DeviceFeatureEnum.SENSOR_EXTERNAL_UNIT_EXHAUST_TEMPERATURE,
                DeviceFeatureEnum.SENSOR_IS_ONLINE,
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
        case DeviceTypeEnum.WINDOW_AC:
            return [
                DeviceFeatureEnum.MODE_AUTO,
                DeviceFeatureEnum.MODE_COOL,
                DeviceFeatureEnum.MODE_DEHUMIDIFICATION,
                DeviceFeatureEnum.MODE_FAN,
                DeviceFeatureEnum.SENSOR_CURRENT_TEMPERATURE,
                DeviceFeatureEnum.SENSOR_IS_ONLINE,
                DeviceFeatureEnum.SWITCH_POWER,
                DeviceFeatureEnum.SWITCH_BEEP,
                DeviceFeatureEnum.SWITCH_ECO,
                DeviceFeatureEnum.SWITCH_SCREEN,
                DeviceFeatureEnum.SWITCH_SLEEP,
                DeviceFeatureEnum.SELECT_MODE,
                DeviceFeatureEnum.SELECT_WINDOW_AS_WIND_SPEED,
                DeviceFeatureEnum.NUMBER_TARGET_TEMPERATURE,
                DeviceFeatureEnum.NUMBER_TARGET_TEMPERATURE_ALLOW_HALF_DIGITS,                
                DeviceFeatureEnum.CLIMATE,
                DeviceFeatureEnum.USER_CONFIG_BEHAVIOR_MEMORIZE_TEMP_BY_MODE,
                DeviceFeatureEnum.USER_CONFIG_BEHAVIOR_MEMORIZE_FAN_SPEED_BY_MODE,
                DeviceFeatureEnum.USER_CONFIG_BEHAVIOR_SILENT_BEEP_WHEN_TURN_ON,
            ]
        case DeviceTypeEnum.PORTABLE_AC:
            features = [
                DeviceFeatureEnum.MODE_DEHUMIDIFICATION,
                DeviceFeatureEnum.MODE_FAN,
                DeviceFeatureEnum.MODE_COOL,
                DeviceFeatureEnum.SWITCH_POWER,
                DeviceFeatureEnum.SWITCH_SLEEP,
                DeviceFeatureEnum.SELECT_MODE,
                DeviceFeatureEnum.SELECT_PORTABLE_WIND_SPEED,
                DeviceFeatureEnum.NUMBER_TARGET_DEGREE,
                DeviceFeatureEnum.SENSOR_IS_ONLINE,
            ]
            
            if has_property(aws_thing_state_reported, "swingWind"):
                features.append(DeviceFeatureEnum.SWITCH_SWING_WIND)
                features.append(DeviceFeatureEnum.MODE_AUTO)
                
            return features
        case _:
            return []
