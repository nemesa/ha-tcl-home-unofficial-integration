"""TCL ATW Heat Pump device handler."""

from dataclasses import dataclass
from homeassistant.core import HomeAssistant
from .calculations import try_get_value
from .data_storage import get_stored_data, set_stored_data, setup_common_init_values


@dataclass
class TCL_ATW_HeatPump_DeviceData:
    def __init__(self, device_id: str, aws_thing_state: dict, delta: dict) -> None:
        self.device_id = device_id
        self.pwr_sw_1 = int(try_get_value(delta, aws_thing_state, "pwrSw1", 0))
        self.pwr_sw_2 = int(try_get_value(delta, aws_thing_state, "pwrSw2", 0))
        self.pwr_sw_3 = int(try_get_value(delta, aws_thing_state, "pwrSw3", 0))
        self.dhw_switch = int(try_get_value(delta, aws_thing_state, "lvHWtSw", 0))
        self.work_mode = int(try_get_value(delta, aws_thing_state, "workMode", 0))
        self.current_temperature = float(try_get_value(delta, aws_thing_state, "currentTemp1", 0))
        self.current_temp_2 = float(try_get_value(delta, aws_thing_state, "currentTemp2", 0))
        self.current_temp_3 = float(try_get_value(delta, aws_thing_state, "currentTemp3", 0))
        self.current_temp_domestic = float(try_get_value(delta, aws_thing_state, "currentTempDomestic", 0))
        self.target_temp_domestic = float(try_get_value(delta, aws_thing_state, "lvHWtT", 0))
        self.target_temp_heat_z1 = float(try_get_value(delta, aws_thing_state, "htWtTWd1", 0))
        self.target_temp_room_z1 = float(try_get_value(delta, aws_thing_state, "htEvTGd1", try_get_value(delta, aws_thing_state, "htEvTWd1", 20)))
        self.eco_status = int(try_get_value(delta, aws_thing_state, "ECOStatus", 0))
        self.eco_mode = int(try_get_value(delta, aws_thing_state, "ECOMode", 0))
        self.eco_timer = int(try_get_value(delta, aws_thing_state, "ECOTmSw", 0))
        self.ptc = int(try_get_value(delta, aws_thing_state, "PTC", 0))
        self.weather_control_sw_1 = int(try_get_value(delta, aws_thing_state, "wthCtlSw1", 0))
        self.heating_curve_1 = int(try_get_value(delta, aws_thing_state, "htWthCtl1", 1))
        self.cooling_curve_1 = int(try_get_value(delta, aws_thing_state, "clWthCtl1", 0))
        self.target_temp_curve_z1 = float(try_get_value(delta, aws_thing_state, "htWtTGd1", 0))
        self.temp_water_flow_z1 = float(try_get_value(delta, aws_thing_state, "htWtTRr1", 0))
        self.temp_water_return_z1 = self.temp_water_flow_z1
        self.temp_room_reference_z1 = float(try_get_value(delta, aws_thing_state, "htEvTRr1", 0))
        self.temp_room_return_z1 = self.temp_room_reference_z1

    device_id: str
    pwr_sw_1: int
    pwr_sw_2: int
    pwr_sw_3: int
    dhw_switch: int
    work_mode: int
    current_temperature: float
    current_temp_2: float
    current_temp_3: float
    current_temp_domestic: float
    target_temp_domestic: float
    target_temp_heat_z1: float
    target_temp_room_z1: float
    eco_status: int
    eco_mode: int
    eco_timer: int
    ptc: int
    weather_control_sw_1: int
    heating_curve_1: int
    cooling_curve_1: int
    target_temp_curve_z1: float
    temp_water_flow_z1: float
    temp_water_return_z1: float
    temp_room_reference_z1: float
    temp_room_return_z1: float


async def get_stored_atw_heat_pump_data(
    hass: HomeAssistant, device_id: str
) -> dict[str, any]:
    stored_data = await get_stored_data(hass, device_id)
    if stored_data is None:
        stored_data = {}
    stored_data, need_save = setup_common_init_values(stored_data)
    if need_save:
        await set_stored_data(hass, device_id, stored_data)
    return stored_data
