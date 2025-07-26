"""."""

from dataclasses import dataclass
from enum import StrEnum
import json
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from .device_ac_common import ModeEnum
from .device_portable_ac import TCL_PortableAC_DeviceData, get_stored_portable_ac_data
from .device_spit_ac_fresh_air import (
    TCL_SplitAC_Fresh_Air_DeviceData,
    get_stored_spit_ac_fresh_data,
)
from .device_spit_ac_type1 import (
    TCL_SplitAC_Type1_DeviceData,
    get_SplitAC_Type1_capabilities,
    get_stored_spit_ac_type1_data,
)
from .device_spit_ac_type2 import (
    TCL_SplitAC_Type2_DeviceData,
    get_SplitAC_Type2_capabilities,
    get_stored_spit_ac_type2_data,
)


_LOGGER = logging.getLogger(__name__)


class DeviceTypeEnum(StrEnum):
    SPLIT_AC = "Split AC"
    SPLIT_AC_TYPE_1 = "Split AC (Type 1)"
    SPLIT_AC_TYPE_2 = "Split AC (Type 2)"
    SPLIT_AC_FRESH_AIR = "Split AC Fresh air"
    PORTABLE_AC = "Portable AC"


class DeviceFeature(StrEnum):
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


def getSupportedFeatures(device_type: DeviceTypeEnum) -> list[DeviceFeature]:
    match device_type:
        case DeviceTypeEnum.SPLIT_AC_TYPE_1:
            return [
                DeviceFeature.MODE_HEAT,
                DeviceFeature.SENSOR_CURRENT_TEMPERATURE,
                DeviceFeature.SWITCH_POWER,
                DeviceFeature.SWITCH_BEEP,
                DeviceFeature.SWITCH_ECO,
                DeviceFeature.SWITCH_HEALTHY,
                DeviceFeature.SWITCH_DRYING,
                DeviceFeature.SWITCH_SCREEN,
                DeviceFeature.SWITCH_8_C_HEATING,
                DeviceFeature.SELECT_MODE,
                DeviceFeature.SELECT_WIND_SPEED,
                DeviceFeature.SELECT_VERTICAL_DIRECTION,
                DeviceFeature.SELECT_HORIZONTAL_DIRECTION,
                DeviceFeature.SELECT_SLEEP_MODE,
                DeviceFeature.NUMBER_TARGET_TEMPERATURE,
                DeviceFeature.BUTTON_SELF_CLEAN,
                DeviceFeature.CLIMATE,
                DeviceFeature.INTERNAL_HAS_SWING_SWITCH,
                DeviceFeature.USER_CONFIG_BEHAVIOR_MEMORIZE_TEMP_BY_MODE,
                DeviceFeature.USER_CONFIG_BEHAVIOR_MEMORIZE_FAN_SPEED_BY_MODE,
                DeviceFeature.USER_CONFIG_BEHAVIOR_SILENT_BEEP_WHEN_TURN_ON,
            ]
        case DeviceTypeEnum.SPLIT_AC_TYPE_2:
            return [
                DeviceFeature.MODE_HEAT,
                DeviceFeature.SENSOR_CURRENT_TEMPERATURE,
                DeviceFeature.SENSOR_EXTERNAL_UNIT_TEMPERATURE,
                DeviceFeature.SWITCH_POWER,
                DeviceFeature.SWITCH_BEEP,
                DeviceFeature.SWITCH_AI_ECO,
                DeviceFeature.SWITCH_HEALTHY,
                DeviceFeature.SWITCH_DRYING,
                DeviceFeature.SWITCH_SCREEN,
                DeviceFeature.SWITCH_8_C_HEATING,
                DeviceFeature.SWITCH_SOFT_WIND,
                DeviceFeature.SELECT_MODE,
                DeviceFeature.SELECT_WIND_SPEED_7_GEAR,
                DeviceFeature.SELECT_VERTICAL_DIRECTION,
                DeviceFeature.SELECT_HORIZONTAL_DIRECTION,
                DeviceFeature.SELECT_SLEEP_MODE,
                DeviceFeature.NUMBER_TARGET_TEMPERATURE,
                DeviceFeature.SELECT_GENERATOR_MODE,
                DeviceFeature.BUTTON_SELF_CLEAN,
                DeviceFeature.CLIMATE,
                DeviceFeature.INTERNAL_SET_TFT_WITH_TT,
                DeviceFeature.USER_CONFIG_BEHAVIOR_MEMORIZE_TEMP_BY_MODE,
                DeviceFeature.USER_CONFIG_BEHAVIOR_MEMORIZE_FAN_SPEED_BY_MODE,
                DeviceFeature.USER_CONFIG_BEHAVIOR_SILENT_BEEP_WHEN_TURN_ON,
            ]
        case DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
            return [
                DeviceFeature.MODE_HEAT,
                DeviceFeature.SENSOR_CURRENT_TEMPERATURE,
                DeviceFeature.SENSOR_INTERNAL_UNIT_COIL_TEMPERATURE,
                DeviceFeature.SENSOR_EXTERNAL_UNIT_COIL_TEMPERATURE,
                DeviceFeature.SENSOR_EXTERNAL_UNIT_TEMPERATURE,
                DeviceFeature.SENSOR_EXTERNAL_UNIT_EXHAUST_TEMPERATURE,
                DeviceFeature.SWITCH_POWER,
                DeviceFeature.SWITCH_BEEP,
                DeviceFeature.SWITCH_ECO,
                DeviceFeature.SWITCH_HEALTHY,
                DeviceFeature.SWITCH_DRYING,
                DeviceFeature.SWITCH_SCREEN,
                DeviceFeature.SWITCH_LIGHT_SENSE,
                DeviceFeature.SWITCH_FRESH_AIR,
                DeviceFeature.SELECT_MODE,
                DeviceFeature.SELECT_VERTICAL_DIRECTION,
                DeviceFeature.SELECT_HORIZONTAL_DIRECTION,
                DeviceFeature.SELECT_SLEEP_MODE,
                DeviceFeature.SELECT_WIND_SPEED_7_GEAR,
                DeviceFeature.SELECT_WIND_FEELING,
                DeviceFeature.SELECT_FRESH_AIR,
                DeviceFeature.SELECT_GENERATOR_MODE,
                DeviceFeature.NUMBER_TARGET_TEMPERATURE,
                DeviceFeature.NUMBER_TARGET_TEMPERATURE_ALLOW_HALF_DIGITS,
                DeviceFeature.BUTTON_SELF_CLEAN,
                DeviceFeature.CLIMATE,
                DeviceFeature.USER_CONFIG_BEHAVIOR_MEMORIZE_TEMP_BY_MODE,
                DeviceFeature.USER_CONFIG_BEHAVIOR_MEMORIZE_FAN_SPEED_BY_MODE,
                DeviceFeature.USER_CONFIG_BEHAVIOR_SILENT_BEEP_WHEN_TURN_ON,
            ]
        case DeviceTypeEnum.PORTABLE_AC:
            return [
                DeviceFeature.SWITCH_POWER,
                DeviceFeature.SWITCH_SWING_WIND,
                DeviceFeature.SWITCH_SLEEP,
                DeviceFeature.SELECT_MODE,
                DeviceFeature.SELECT_PORTABLE_WIND_SEED,
                DeviceFeature.NUMBER_TARGET_DEGREE,
            ]
        case _:
            return []


def is_implemented_by_integration(device_type: str) -> bool:
    known_device_types = [
        "Split AC",
        "Split AC-1",
        "Split AC Fresh air",
        "Portable AC"
    ]
    if device_type.lower() in list(map(str.lower,known_device_types)):
        return True
    return False


def calculateDeviceType(
    device_id: str, device_type: str, aws_thing: dict | None
) -> DeviceTypeEnum | None:
    _LOGGER.debug("Calculating device type for %s (%s)", device_id, device_type)
    if device_type == "Portable AC":
        return DeviceTypeEnum.PORTABLE_AC
    elif device_type == "Split AC Fresh air":
        return DeviceTypeEnum.SPLIT_AC_FRESH_AIR
    elif device_type == "Split AC" or device_type == "Split AC-1":
        if aws_thing is not None:
            capabilities = aws_thing["state"]["reported"].get("capabilities", [])
            capabilities.sort()
            for type_capabilities in get_SplitAC_Type1_capabilities():
                if capabilities == type_capabilities:
                    return DeviceTypeEnum.SPLIT_AC_TYPE_1
            for type_capabilities in get_SplitAC_Type2_capabilities():
                if capabilities == type_capabilities:
                    return DeviceTypeEnum.SPLIT_AC_TYPE_2
            return DeviceTypeEnum.SPLIT_AC
    return None


@dataclass
class Device:
    """Device."""

    def __init__(
        self,
        device_id: str,
        device_type_str: str | None,
        device_type: DeviceTypeEnum | None,
        name: str,
        firmware_version: str,
        aws_thing: dict | None,
    ) -> None:
        self.device_type_str = device_type_str
        self.device_id = device_id
        if device_type is None:
            self.device_type = calculateDeviceType(
                device_id, device_type_str, aws_thing
            )
        else:
            self.device_type = device_type
        self.name = name
        self.storage = {}
        self.firmware_version = firmware_version
        self.is_implemented_by_integration = self.device_type is not None
        self.has_aws_thing = "false"
        self.capabilities_str = ""
        if aws_thing is not None:
            self.has_aws_thing = "true"
            try:
                if "state" in aws_thing:
                    if "reported" in aws_thing["state"]:
                        if "capabilities" in aws_thing["state"]["reported"]:
                            capabilities_array = aws_thing["state"]["reported"][
                                "capabilities"
                            ]
                            capabilities_array.sort()
                            self.capabilities_str = json.dumps(capabilities_array)
            except Exception as e:
                _LOGGER.error(
                    "Error while getting capabilities for device %s: %s",
                    device_id,
                    str(e),
                )
                self.capabilities_str = str(e)

            match self.device_type:
                case DeviceTypeEnum.SPLIT_AC_TYPE_1:
                    self.data = TCL_SplitAC_Type1_DeviceData(
                        device_id,
                        aws_thing["state"]["reported"],
                        aws_thing["state"].get("delta", {}),
                    )
                case DeviceTypeEnum.SPLIT_AC_TYPE_2:
                    self.data = TCL_SplitAC_Type2_DeviceData(
                        device_id,
                        aws_thing["state"]["reported"],
                        aws_thing["state"].get("delta", {}),
                    )
                case DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    self.data = TCL_SplitAC_Fresh_Air_DeviceData(
                        device_id,
                        aws_thing["state"]["reported"],
                        aws_thing["state"].get("delta", {}),
                    )
                case DeviceTypeEnum.PORTABLE_AC:
                    self.data = TCL_PortableAC_DeviceData(
                        device_id,
                        aws_thing["state"]["reported"],
                        aws_thing["state"].get("delta", {}),
                    )

                case _:
                    self.data = None
        else:
            self.data = None

    capabilities_str: str
    device_id: int
    device_type: str
    device_type_str: str
    has_aws_thing: str
    name: str
    firmware_version: str
    is_implemented_by_integration: bool
    storage: dict[str, any]
    data: (
        TCL_SplitAC_Type1_DeviceData
        | TCL_SplitAC_Fresh_Air_DeviceData
        | TCL_PortableAC_DeviceData
        | None
    ) = None


def toDeviceInfo(device: Device) -> DeviceInfo:
    """Convert Device to DeviceInfo."""
    return DeviceInfo(
        name=f"{device.name} ({device.device_id}){'' if device.is_implemented_by_integration else ' (Not implemented)'}",
        manufacturer="TCL",
        model=device.device_type,
        sw_version=device.firmware_version,
        identifiers={
            (
                DOMAIN,
                f"TCL-{device.device_id}",
            )
        },
    )


def get_supported_modes(device: Device) -> list[ModeEnum]:
    supported_features = getSupportedFeatures(device.device_type)
    if DeviceFeature.MODE_HEAT not in supported_features:
        return [e.value for e in ModeEnum if e != ModeEnum.HEAT]
    return [e.value for e in ModeEnum]


async def get_device_storage(hass: HomeAssistant, device: Device) -> None:
    if device.device_type == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
        return await get_stored_spit_ac_fresh_data(hass, device.device_id)
    elif device.device_type == DeviceTypeEnum.SPLIT_AC_TYPE_1:
        return await get_stored_spit_ac_type1_data(hass, device.device_id)
    elif device.device_type == DeviceTypeEnum.SPLIT_AC_TYPE_2:
        return await get_stored_spit_ac_type2_data(hass, device.device_id)
    elif device.device_type == DeviceTypeEnum.PORTABLE_AC:
        return await get_stored_portable_ac_data(hass, device.device_id)
