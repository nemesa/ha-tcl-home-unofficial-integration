"""."""

import logging
from dataclasses import dataclass

from homeassistant.core import HomeAssistant

from .calculations import try_get_value
from .data_storage import (get_stored_data, safe_set_value, set_stored_data,
                           setup_common_init_values)

_LOGGER = logging.getLogger(__name__)

@dataclass
class TCL_Breeva_DeviceData:
    def __init__(self, device_id: str, aws_thing_state: dict, delta: dict) -> None:
        self.device_id = device_id
        self.power_switch = int(
            try_get_value(delta, aws_thing_state, "powerSwitch", -1)
        )
        self.pm25_sensor_value = int(
            try_get_value(delta, aws_thing_state, "PM25SensorValue", -1)
        )
        self.voc_sensor_level = int(
            try_get_value(delta, aws_thing_state, "VOCSensorLevel", -1)
        )
        self.voc_sensor_level = int(
            try_get_value(delta, aws_thing_state, "filterLifeTime", -1)
        )
        self.filter_life_time = int(
            try_get_value(delta, aws_thing_state, "filterLifeTime", -1)
        )
        self.work_mode = int(try_get_value(delta, aws_thing_state, "workMode", -1))
        self.wind_speed = int(try_get_value(delta, aws_thing_state, "windSpeed", -1))
        self.screen_switch = int(try_get_value(delta, aws_thing_state, "screenSwitch", -1))
        self.shield_switch = int(try_get_value(delta, aws_thing_state, "shieldSwitch", -1))
        # ambient_light's shape is ambient_light.powerSwitch and ambient_light.brightness
        # TODO: need to figure out if dot notation works here
        # self.ambient_light = int(try_get_value(delta, aws_thing_state, "ambientLight", -1))
        self.child_lock_switch = int(try_get_value(delta, aws_thing_state, "childLockSwitch", -1))
        self.timer_remaining = int(try_get_value(delta, aws_thing_state, "timerRemaining", -1))
        self.panel_light_auto_off = int(try_get_value(delta, aws_thing_state, "panelLightAutoOFF", -1))
        self.favourite_mode_switch = int(try_get_value(delta, aws_thing_state, "favouriteModeSwitch", -1))

    device_id: str
    power_switch: int | bool
    pm25_sensor_value: int | bool
    voc_sensor_level: int | bool
    filter_life_time: int | bool
    work_mode: int | bool
    wind_speed: int | bool
    screen_switch: int | bool
    shield_switch: int | bool
    child_lock_switch: int | bool
    timer_remaining: int | bool
    panel_light_auto_off: int | bool
    favourite_mode_switch: int | bool

async def get_stored_breeva_data(
    hass: HomeAssistant, device_id: str
) -> dict[str, any]:
    need_save = False
    stored_data = await get_stored_data(hass, device_id)
    _LOGGER.info("Breeva stored data: %s", stored_data)
    
    if stored_data is None:
        stored_data = {}
        need_save = True

    stored_data, need_save = setup_common_init_values(stored_data)
    if need_save:
        await set_stored_data(hass, device_id, stored_data)
    return stored_data

