"""."""

from dataclasses import dataclass

from homeassistant.core import HomeAssistant

from .calculations import try_get_value
from .device_data_storage import get_stored_data, safe_set_value, set_stored_data


@dataclass
class TCL_PortableAC_DeviceData:
    def __init__(self, device_id: str, aws_thing_state: dict, delta: dict) -> None:
        self.device_id = device_id
        self.power_switch               = int(try_get_value(delta, aws_thing_state, "powerSwitch", -1))
        self.wind_speed                 = int(try_get_value(delta, aws_thing_state, "windSpeed", -1))
        self.swing_wind                 = int(try_get_value(delta, aws_thing_state, "swingWind", -1))
        self.work_mode                  = int(try_get_value(delta, aws_thing_state, "workMode", -1))
        self.target_fahrenheit_degree   = int(try_get_value(delta, aws_thing_state, "targetFahrenheitDegree", -1))
        self.target_temperature         = int(try_get_value(delta, aws_thing_state, "targetCelsiusDegree", -1))
        self.target_celsius_degree      = int(try_get_value(delta, aws_thing_state, "targetCelsiusDegree", -1))
        self.temperature_type           = int(try_get_value(delta, aws_thing_state, "temperatureType", -1))
        self.sleep                      = int(try_get_value(delta, aws_thing_state, "sleep", -1))
        self.lower_temperature_limit    = int(try_get_value(delta, aws_thing_state, "lowerTemperatureLimit", 18))
        self.upper_temperature_limit    = int(try_get_value(delta, aws_thing_state, "upperTemperatureLimit", 32))

    device_id: str
    power_switch: int | bool
    wind_speed: int | bool
    swing_wind: int | bool
    work_mode: int | bool
    target_fahrenheit_degree: int | bool
    target_temperature: int | bool
    target_celsius_degree: int | bool
    temperature_type: int | bool
    sleep: int | bool
    upper_temperature_limit: int
    lower_temperature_limit: int


async def get_stored_portable_ac_data(
    hass: HomeAssistant, device_id: str
) -> dict[str, any]:
    need_save = False
    stored_data = await get_stored_data(hass, device_id)
    if stored_data is None:
        stored_data = {}
        need_save = True

    stored_data, need_save = safe_set_value(stored_data, "non_user_config.native_temp_step", 1)

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

