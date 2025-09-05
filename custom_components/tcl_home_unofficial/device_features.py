"""."""

from enum import StrEnum
import logging

from .device_capabilities import DeviceCapabilityEnum
from .device_types import DeviceTypeEnum

_LOGGER = logging.getLogger(__name__)

class DeviceFeatureEnum(StrEnum):
    MODE_AC_AUTO = "mode.ac.auto"
    MODE_AC_COOL = "mode.ac.cool"
    MODE_AC_DEHUMIDIFICATION = "mode.ac.dehumidification"
    MODE_AC_FAN = "mode.ac.fan"
    MODE_AC_HEAT = "mode.ac.heat"
    MODE_DEHUMIDIFIER_DRY = "mode.dehumidifier.dry"
    MODE_DEHUMIDIFIER_TURBO = "mode.dehumidifier.turbo"
    MODE_DEHUMIDIFIER_COMFORT = "mode.dehumidifier.comfort"
    MODE_DEHUMIDIFIER_CONTINUE = "mode.dehumidifier.continue"
    SENSOR_IS_ONLINE = "sensor.is_online"
    SENSOR_CURRENT_TEMPERATURE = "sensor.current_temperature"
    SENSOR_DEHUMIDIFIER_ENV_HUMIDITY = "sensor.dehumidifier.env_humidity"
    SENSOR_DEHUMIDIFIER_WATER_BUCKET_FULL = "sensor.dehumidifier.is_water_bucket_full"
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
    SELECT_DEHUMIDIFIER_WIND_SPEED_LOW_MEDIUM_HEIGH = "select.dehumidifier.windSpeed.lowMediumHigh"
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
    SELECT_PORTABLE_WIND_4VALUE_SPEED = "select.portableWind4ValueSpeed"
    SELECT_WINDOW_AS_WIND_SPEED = "select.WindowAcWindSpeed"
    NUMBER_DEHUMIDIFIER_HUMIDITY = "number.dehumidifier.humidity"
    NUMBER_TARGET_DEGREE = "number.targetDegree"
    NUMBER_TARGET_TEMPERATURE = "number.targetTemperature"
    NUMBER_TARGET_TEMPERATURE_ALLOW_HALF_DIGITS = "number.targetTemperature.allow_half_digits"
    DIAGNOSIC_ERROR_CODES = "diagnosic.error.codes"
    BUTTON_SELF_CLEAN = "button.selfClean"
    CLIMATE = "climate"
    HUMIDIFIER = "humidifier"
    INTERNAL_IS_AC = "internal.is.ac"
    INTERNAL_IS_DEHUMIDIFIER = "internal.is.dehumidifier"
    INTERNAL_HAS_SWING_SWITCH = "internal.hasSwingSwitch"
    INTERNAL_HAS_TURBO_PROPERTY = "internal.has_turbo_property"
    INTERNAL_HAS_HIGHTEMPERATUREWIND_PROPERTY = "internal.has_highTemperatureWind_property"
    INTERNAL_HAS_SILENCESWITCH_PROPERTY = "internal.has_silenceSwitch_property"
    INTERNAL_SET_TFT_WITH_TT = "internal.set_targetFahrenheitTemp_with_targetTemperature"
    USER_CONFIG_BEHAVIOR_MEMORIZE_TEMP_BY_MODE = "user_config.behavior.memorize_temp_by_mode"
    USER_CONFIG_BEHAVIOR_MEMORIZE_FAN_SPEED_BY_MODE = "user_config.behavior.memorize_fan_speed_by_mode"
    USER_CONFIG_BEHAVIOR_MEMORIZE_HUMIDITY_BY_MODE = "user_config.behavior.memorize_humidity_by_mode"
    USER_CONFIG_BEHAVIOR_SILENT_BEEP_WHEN_TURN_ON = "user_config.behavior.silent_beep_when_turn_on"


def has_property(aws_thing_state_reported: dict[str, any], propertyName: str) -> bool:
    return propertyName in aws_thing_state_reported


def getSupportedFeatures(
    device_type: DeviceTypeEnum, aws_thing_state_reported: dict[str, any], device_storage: dict[str, any] | None = None,
) -> list[DeviceFeatureEnum]:
    capabilities = aws_thing_state_reported.get("capabilities", [])
    has_rn_probe_data= False
    rn_probe_data={}
    if device_storage is not None:
        has_rn_probe_data= device_storage.get("non_user_config", {}).get("rn_probe_data", {}).get("is_success", False)
        rn_probe_data=device_storage.get("non_user_config", {}).get("rn_probe_data", {}).get("data", {})

    match device_type:
        case DeviceTypeEnum.SPLIT_AC:
            features = [
                DeviceFeatureEnum.INTERNAL_IS_AC,
                DeviceFeatureEnum.MODE_AC_AUTO,
                DeviceFeatureEnum.MODE_AC_COOL,
                DeviceFeatureEnum.MODE_AC_DEHUMIDIFICATION,
                DeviceFeatureEnum.MODE_AC_FAN,
                DeviceFeatureEnum.MODE_AC_HEAT,
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
                DeviceFeatureEnum.INTERNAL_IS_AC,
                DeviceFeatureEnum.MODE_AC_AUTO,
                DeviceFeatureEnum.MODE_AC_COOL,
                DeviceFeatureEnum.MODE_AC_DEHUMIDIFICATION,
                DeviceFeatureEnum.MODE_AC_FAN,
                DeviceFeatureEnum.MODE_AC_HEAT,
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
                DeviceFeatureEnum.INTERNAL_IS_AC,
                DeviceFeatureEnum.MODE_AC_AUTO,
                DeviceFeatureEnum.MODE_AC_COOL,
                DeviceFeatureEnum.MODE_AC_DEHUMIDIFICATION,
                DeviceFeatureEnum.MODE_AC_FAN,
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
        case DeviceTypeEnum.DEHUMIDIFIER_DEM:
            return [
                DeviceFeatureEnum.INTERNAL_IS_DEHUMIDIFIER,
                DeviceFeatureEnum.MODE_DEHUMIDIFIER_DRY,
                DeviceFeatureEnum.MODE_DEHUMIDIFIER_TURBO,
                DeviceFeatureEnum.MODE_DEHUMIDIFIER_COMFORT,
                DeviceFeatureEnum.MODE_DEHUMIDIFIER_CONTINUE,
                DeviceFeatureEnum.SWITCH_POWER,
                DeviceFeatureEnum.SELECT_MODE,
                DeviceFeatureEnum.NUMBER_DEHUMIDIFIER_HUMIDITY,
                DeviceFeatureEnum.SENSOR_DEHUMIDIFIER_ENV_HUMIDITY,
                DeviceFeatureEnum.SENSOR_DEHUMIDIFIER_WATER_BUCKET_FULL,
                DeviceFeatureEnum.USER_CONFIG_BEHAVIOR_MEMORIZE_HUMIDITY_BY_MODE,
                DeviceFeatureEnum.DIAGNOSIC_ERROR_CODES,
                DeviceFeatureEnum.HUMIDIFIER,
            ]
        case DeviceTypeEnum.DEHUMIDIFIER_DF:
            return [
                DeviceFeatureEnum.INTERNAL_IS_DEHUMIDIFIER,
                DeviceFeatureEnum.MODE_DEHUMIDIFIER_DRY,
                DeviceFeatureEnum.MODE_DEHUMIDIFIER_COMFORT,
                DeviceFeatureEnum.SWITCH_POWER,
                DeviceFeatureEnum.SELECT_MODE,
                DeviceFeatureEnum.SELECT_DEHUMIDIFIER_WIND_SPEED_LOW_MEDIUM_HEIGH,
                DeviceFeatureEnum.NUMBER_DEHUMIDIFIER_HUMIDITY,
                DeviceFeatureEnum.SENSOR_DEHUMIDIFIER_ENV_HUMIDITY,
                #DeviceFeatureEnum.SENSOR_DEHUMIDIFIER_WATER_BUCKET_FULL,
                DeviceFeatureEnum.USER_CONFIG_BEHAVIOR_MEMORIZE_HUMIDITY_BY_MODE,
                DeviceFeatureEnum.USER_CONFIG_BEHAVIOR_MEMORIZE_FAN_SPEED_BY_MODE,
                DeviceFeatureEnum.DIAGNOSIC_ERROR_CODES,
                DeviceFeatureEnum.HUMIDIFIER,
            ]
        case DeviceTypeEnum.PORTABLE_AC:
            features = [
                DeviceFeatureEnum.INTERNAL_IS_AC,
                DeviceFeatureEnum.MODE_AC_DEHUMIDIFICATION,
                DeviceFeatureEnum.MODE_AC_FAN,
                DeviceFeatureEnum.MODE_AC_COOL,
                DeviceFeatureEnum.SWITCH_POWER,
                DeviceFeatureEnum.SWITCH_SLEEP,
                DeviceFeatureEnum.SELECT_MODE,
                DeviceFeatureEnum.NUMBER_TARGET_DEGREE,
                DeviceFeatureEnum.SENSOR_IS_ONLINE,
            ]
            
            if has_rn_probe_data:
                fan_speed_mapping = rn_probe_data.get("fan_speed_mapping", [])
                if ("FAN_SPEED_AUTO" in fan_speed_mapping 
                    and "FAN_SPEED_LOW" in fan_speed_mapping
                    and ("FAN_SPEED_MED" in fan_speed_mapping or "FAN_SPEED_MEDIUM" in fan_speed_mapping)
                    and "FAN_SPEED_HIGH" in fan_speed_mapping):
                    features.append(DeviceFeatureEnum.SELECT_PORTABLE_WIND_4VALUE_SPEED)
                else:
                    features.append(DeviceFeatureEnum.SELECT_PORTABLE_WIND_SPEED)
            else:
                features.append(DeviceFeatureEnum.SELECT_PORTABLE_WIND_SPEED)
            
            if has_rn_probe_data:
                fan_speed_mapping = rn_probe_data.get("fan_speed_mapping", [])
                if ("FAN_SPEED_AUTO" in fan_speed_mapping 
                    and "FAN_SPEED_LOW" in fan_speed_mapping
                    and ("FAN_SPEED_MED" in fan_speed_mapping or "FAN_SPEED_MEDIUM" in fan_speed_mapping)
                    and "FAN_SPEED_HIGH" in fan_speed_mapping):
                    features.append(DeviceFeatureEnum.SELECT_PORTABLE_WIND_4VALUE_SPEED)
                else:
                    features.append(DeviceFeatureEnum.SELECT_PORTABLE_WIND_SPEED)
            else:
                features.append(DeviceFeatureEnum.SELECT_PORTABLE_WIND_SPEED)
            
            if has_property(aws_thing_state_reported, "swingWind"):
                features.append(DeviceFeatureEnum.SWITCH_SWING_WIND)
                features.append(DeviceFeatureEnum.MODE_AC_AUTO)
            
            
            if has_property(aws_thing_state_reported, "currentTemperature"):
                features.append(DeviceFeatureEnum.SENSOR_CURRENT_TEMPERATURE)
                features.append(DeviceFeatureEnum.CLIMATE)
                
            return features
        case _:
            return []
