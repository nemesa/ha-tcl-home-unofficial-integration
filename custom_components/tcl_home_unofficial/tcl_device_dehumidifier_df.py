"""."""

from dataclasses import dataclass

from homeassistant.core import HomeAssistant

from .calculations import try_get_value
from .data_storage import get_stored_data, safe_set_value, set_stored_data,setup_common_init_values
from .device_enums import DehumidifierModeEnum
from .device_features import DeviceFeatureEnum


@dataclass
class TCL_Dehumidifier_DF_DeviceData:
    def __init__(self, device_id: str, aws_thing_state: dict, delta: dict) -> None:
        self.device_id = device_id
        self.power_switch               = int(try_get_value(delta, aws_thing_state, "powerSwitch", -1))
        self.work_mode                  = int(try_get_value(delta, aws_thing_state, "workMode", -1))
        self.humidity                   = int(try_get_value(delta, aws_thing_state, "Humidity", -1))
        self.env_humidity               = int(try_get_value(delta, aws_thing_state, "envHumidity", -1))
        self.water_pump_switch          = int(try_get_value(delta, aws_thing_state, "waterPumpSwitch", -1))
        self.wind_speed                 = int(try_get_value(delta, aws_thing_state, "windSpeed", -1))
        self.error_code                 = list[int](try_get_value(delta, aws_thing_state, "errorCode", []))

    device_id: str
    power_switch: int | bool
    work_mode: int | bool
    humidity: int | bool
    env_humidity: int | bool
    water_pump_switch: int | bool
    wind_speed: int | bool
    error_code: list[int]
    


async def get_stored_dehumidifier_df_data(
    hass: HomeAssistant, device_id: str
) -> dict[str, any]:
    need_save = False
    stored_data = await get_stored_data(hass, device_id)
    if stored_data is None:
        stored_data = {}
        need_save = True
    
    stored_data, need_save = setup_common_init_values(stored_data)    
    
    stored_data, need_save = safe_set_value(stored_data, "user_config.behavior.memorize_humidity_by_mode", False)
    stored_data, need_save = safe_set_value(stored_data, "user_config.behavior.memorize_fan_speed_by_mode", False)

    stored_data, need_save = safe_set_value(stored_data, "humidity.Dry.value", 60)
    stored_data, need_save = safe_set_value(stored_data, "humidity.Turbo.value", 35)
    stored_data, need_save = safe_set_value(stored_data, "humidity.Comfort.value", 50)
    stored_data, need_save = safe_set_value(stored_data, "humidity.Continue.value", 15)

    if need_save:
        await set_stored_data(hass, device_id, stored_data)
    return stored_data


def handle_dehumidifier_df_mode_change(desired_state:dict, value:DehumidifierModeEnum, supported_features: list[DeviceFeatureEnum], stored_data: dict) -> dict:
    match value:
        case DehumidifierModeEnum.DRY:
            pass
        case DehumidifierModeEnum.COMFORT:
            pass
    return desired_state