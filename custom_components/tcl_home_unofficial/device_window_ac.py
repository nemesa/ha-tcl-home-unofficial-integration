"""."""

from dataclasses import dataclass

from homeassistant.core import HomeAssistant

from .calculations import try_get_value
from .device_data_storage import get_stored_data, safe_set_value, set_stored_data
from .device_enums import ModeEnum
from .device_features import DeviceFeatureEnum


@dataclass
class TCL_WindowAC_DeviceData:
    def __init__(self, device_id: str, aws_thing_state: dict, delta: dict) -> None:
        self.device_id = device_id
        self.power_switch               = int(try_get_value(delta, aws_thing_state, "powerSwitch", -1))
        self.wind_speed                 = int(try_get_value(delta, aws_thing_state, "windSpeed", -1))
        self.work_mode                  = int(try_get_value(delta, aws_thing_state, "workMode", -1))
        self.target_temperature         = float(try_get_value(delta, aws_thing_state, "targetTemperature", -1))
        self.current_temperature        = float(try_get_value(delta, aws_thing_state, "currentTemperature", -1))
        self.sleep                      = int(try_get_value(delta, aws_thing_state, "sleep", -1))
        self.eco                        = int(try_get_value(delta, aws_thing_state, "ECO", -1))
        self.beep_switch                = int(try_get_value(delta, aws_thing_state, "beepSwitch", -1))
        self.screen                     = int(try_get_value(delta, aws_thing_state, "screen", -1))
        self.lower_temperature_limit    = int(try_get_value(delta, aws_thing_state, "lowerTemperatureLimit", 16))
        self.upper_temperature_limit    = int(try_get_value(delta, aws_thing_state, "upperTemperatureLimit", 31))

    device_id: str
    power_switch: int | bool
    wind_speed: int | bool
    work_mode: int | bool
    target_temperature: float | bool
    current_temperature: float | bool
    sleep: int | bool
    eco: int
    beep_switch: int | bool
    screen: int | bool
    upper_temperature_limit: int
    lower_temperature_limit: int


async def get_stored_window_ac_data(
    hass: HomeAssistant, device_id: str
) -> dict[str, any]:
    need_save = False
    stored_data = await get_stored_data(hass, device_id)
    if stored_data is None:
        stored_data = {}
        need_save = True

    stored_data, need_save = safe_set_value(stored_data, "non_user_config.native_temp_step", 1, True)

    stored_data, need_save = safe_set_value(stored_data, "user_config.behavior.memorize_temp_by_mode", False)
    stored_data, need_save = safe_set_value(stored_data, "user_config.behavior.memorize_fan_speed_by_mode", False)
    stored_data, need_save = safe_set_value(stored_data, "user_config.behavior.silent_beep_when_turn_on", False)

    stored_data, need_save = safe_set_value(stored_data, "target_temperature.Cool.value", 22)

    default_wind_speed = "Auto"
    stored_data, need_save = safe_set_value(stored_data, "fan_speed.Cool.value", default_wind_speed)
    stored_data, need_save = safe_set_value(stored_data, "fan_speed.Dehumidification.value", default_wind_speed)
    stored_data, need_save = safe_set_value(stored_data, "fan_speed.Fan.value", default_wind_speed)
    stored_data, need_save = safe_set_value(stored_data, "fan_speed.Auto.value", default_wind_speed)
    if need_save:
        await set_stored_data(hass, device_id, stored_data)
    return stored_data


def handle_window_ac_mode_change(desired_state:dict, value:ModeEnum, supported_features: list[DeviceFeatureEnum], stored_data: dict) -> dict:
    match value:
        case ModeEnum.AUTO:
            desired_state["ECO"] = 0
            desired_state["windSpeed"] = 0  
            desired_state["sleep"] = 0  
        case ModeEnum.COOL:
            desired_state["ECO"] = 1
            desired_state["windSpeed"] = 0
            desired_state["sleep"] = 0
        case ModeEnum.DEHUMIDIFICATION:
            desired_state["ECO"] = 1
            desired_state["windSpeed"] = 2
            desired_state["sleep"] = 0
        case ModeEnum.FAN:
            desired_state["ECO"] = 0
            desired_state["windSpeed"] = 0  
            desired_state["sleep"] = 0      
    return desired_state