"""."""

from dataclasses import dataclass

from homeassistant.core import HomeAssistant

from .calculations import try_get_value
from .data_storage import get_stored_data, safe_set_value, set_stored_data,setup_common_init_values
from .device_enums import ModeEnum
from .device_features import DeviceFeatureEnum


@dataclass
class TCL_DuctAC_DeviceData:
    def __init__(self, device_id: str, aws_thing_state: dict, delta: dict) -> None:
        self.device_id = device_id
        self.power_switch               = int(try_get_value(delta, aws_thing_state, "powerSwitch", -1))
        self.beep_switch                = int(try_get_value(delta, aws_thing_state, "beepSwitch", -1))
        self.screen                     = int(try_get_value(delta, aws_thing_state, "screen", -1))
        self.target_temperature         = int(try_get_value(delta, aws_thing_state, "targetTemperature", -1))
        self.current_temperature        = int(try_get_value(delta, aws_thing_state, "currentTemperature", -1))
        self.work_mode                  = int(try_get_value(delta, aws_thing_state, "workMode", -1))
        self.vertical_direction         = int(try_get_value(delta, aws_thing_state, "verticalDirection", -1))
        self.eight_add_hot              = int(try_get_value(delta, aws_thing_state, "eightAddHot", -1))
        self.sleep                      = int(try_get_value(delta, aws_thing_state, "sleep", -1))
        self.anti_moldew                = int(try_get_value(delta, aws_thing_state, "antiMoldew", -1))
        self.self_clean                 = int(try_get_value(delta, aws_thing_state, "selfClean", -1))
        self.wind_speed_auto_switch     = int(try_get_value(delta, aws_thing_state, "windSpeedAutoSwitch", -1))
        self.wind_speed_7_gear          = int(try_get_value(delta, aws_thing_state, "windSpeed7Gear", -1))
        self.ai_eco                     = int(try_get_value(delta, aws_thing_state, "AIECOSwitch", -1))
        self.external_unit_temperature  = int(try_get_value(delta, aws_thing_state, "externalUnitTemperature", -1))
        self.lower_temperature_limit    = int(try_get_value(delta, aws_thing_state, "lowerTemperatureLimit", 16))
        self.upper_temperature_limit    = int(try_get_value(delta, aws_thing_state, "upperTemperatureLimit", 31))

    device_id: str
    power_switch: int | bool
    beep_switch: int | bool
    target_temperature: int
    current_temperature: int
    vertical_direction: int
    sleep: int
    anti_moldew: int
    self_clean: int
    eight_add_hot: int
    screen: int
    wind_speed_7_gear: int
    ai_eco: int
    wind_speed_auto_switch: int
    external_unit_temperature: int
    upper_temperature_limit: int
    lower_temperature_limit: int


async def get_stored_duct_ac_data(
    hass: HomeAssistant, device_id: str
) -> dict[str, any]:
    need_save = False
    stored_data = await get_stored_data(hass, device_id)
    if stored_data is None:
        stored_data = {}
        need_save = True
    stored_data, need_save = setup_common_init_values(stored_data)
    
    stored_data, need_save = safe_set_value(stored_data, "non_user_config.native_temp_step", 1.0)
    
    stored_data, need_save = safe_set_value(stored_data, "user_config.behavior.memorize_temp_by_mode", True)
    stored_data, need_save = safe_set_value(stored_data, "user_config.behavior.memorize_fan_speed_by_mode", False)
    stored_data, need_save = safe_set_value(stored_data, "user_config.behavior.silent_beep_when_turn_on", False)

    stored_data, need_save = safe_set_value(stored_data, "target_temperature.Cool.value", 24)
    stored_data, need_save = safe_set_value(stored_data, "target_temperature.Heat.value", 36)
    stored_data, need_save = safe_set_value(stored_data, "target_temperature.Dehumidification.value", 24)
    stored_data, need_save = safe_set_value(stored_data, "target_temperature.Fan.value", 24)
    stored_data, need_save = safe_set_value(stored_data, "target_temperature.Auto.value", 24)

    default_wind_speed = "Auto"
    stored_data, need_save = safe_set_value(stored_data, "fan_speed.Cool.value", default_wind_speed)
    stored_data, need_save = safe_set_value(stored_data, "fan_speed.Heat.value", default_wind_speed)
    stored_data, need_save = safe_set_value(stored_data, "fan_speed.Dehumidification.value", default_wind_speed)
    stored_data, need_save = safe_set_value(stored_data, "fan_speed.Fan.value", default_wind_speed)
    stored_data, need_save = safe_set_value(stored_data, "fan_speed.Auto.value", default_wind_speed)

    if need_save:
        await set_stored_data(hass, device_id, stored_data)
    return stored_data

def handle_duct_ac_mode_change(desired_state:dict, value:ModeEnum, supported_features: list[DeviceFeatureEnum], stored_data: dict) -> dict:
    match value:
        case ModeEnum.AUTO:
            if (DeviceFeatureEnum.SWITCH_8_C_HEATING in supported_features):
                desired_state["eightAddHot"] = 0
            if (DeviceFeatureEnum.SELECT_WIND_SPEED_7_GEAR in supported_features):
                desired_state["windSpeedAutoSwitch"] = 1
                desired_state["windSpeed7Gear"] = 0                                   
        case ModeEnum.COOL:
            if (DeviceFeatureEnum.SWITCH_8_C_HEATING in supported_features):
                desired_state["eightAddHot"] = 0
            if (DeviceFeatureEnum.SELECT_WIND_SPEED_7_GEAR in supported_features):
                desired_state["windSpeedAutoSwitch"] = 1
                desired_state["windSpeed7Gear"] = 0
        case ModeEnum.DEHUMIDIFICATION:
            if (DeviceFeatureEnum.SWITCH_8_C_HEATING in supported_features):
                desired_state["eightAddHot"] = 0
            if (DeviceFeatureEnum.SELECT_WIND_SPEED_7_GEAR in supported_features):
                desired_state["windSpeed7Gear"] = 2
                desired_state["windSpeedAutoSwitch"] = 0
        case ModeEnum.FAN:            
            if (DeviceFeatureEnum.SWITCH_8_C_HEATING in supported_features):
                desired_state["eightAddHot"] = 0
            if (DeviceFeatureEnum.SELECT_WIND_SPEED_7_GEAR in supported_features):
                desired_state["windSpeedAutoSwitch"] = 1
                desired_state["windSpeed7Gear"] = 0
        case ModeEnum.HEAT:
            if (DeviceFeatureEnum.SWITCH_8_C_HEATING in supported_features):
                desired_state["eightAddHot"] = 0
            if (DeviceFeatureEnum.SELECT_WIND_SPEED_7_GEAR in supported_features):
                desired_state["windSpeedAutoSwitch"] = 1
                desired_state["windSpeed7Gear"] = 0
    return desired_state