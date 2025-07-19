"""."""

from dataclasses import dataclass
from enum import StrEnum

from .device_ac_common import (
    LeftAndRightAirSupplyVectorEnum,
    ModeEnum,
    SleepModeEnum,
    UpAndDownAirSupplyVectorEnum,
    getLeftAndRightAirSupplyVector,
    getMode,
    getSleepMode,
    getUpAndDownAirSupplyVector,
)


class PortableWindSeedEnum(StrEnum):    
    HEIGH = "Heigh"
    LOW = "Low"
    AUTO = "Auto"
    
    

class TemperatureTypeEnum(StrEnum):    
    FAHRENHEIT = "Fahrenheit"
    CELSIUS = "Celsius"


@dataclass
class TCL_PortableAC_DeviceData:
    def __init__(self, device_id: str, aws_thing_state: dict, delta: dict) -> None:
        
        self.power_switch = int(delta.get("powerSwitch", aws_thing_state["powerSwitch"]))
        self.wind_speed = int(delta.get("windSpeed", aws_thing_state["windSpeed"]))
        self.swing_wind = int(delta.get("swingWind", aws_thing_state["swingWind"]))
        self.work_mode = int(delta.get("workMode", aws_thing_state["workMode"]))
        self.target_fahrenheit_degree = int(delta.get("targetFahrenheitDegree", aws_thing_state["targetFahrenheitDegree"]))
        self.target_celsius_degree = int(delta.get("targetCelsiusDegree", aws_thing_state["targetCelsiusDegree"]))
        self.temperature_type = int(delta.get("temperatureType", aws_thing_state["temperatureType"]))
        self.sleep = int(delta.get("sleep", aws_thing_state["sleep"]))
        

    power_switch: int | bool
    wind_speed: int | bool
    swing_wind: int | bool
    work_mode: int | bool
    target_fahrenheit_degree: int | bool
    target_celsius_degree: int | bool
    temperature_type: int | bool
    sleep: int | bool

class TCL_PortableAC_DeviceData_Helper:
    def __init__(self, data: TCL_PortableAC_DeviceData) -> None:
        self.data = data

    def getMode(self) -> ModeEnum:
        return getMode(self.data.work_mode)

    def getWindSpeed(self) -> PortableWindSeedEnum:
        match self.data.wind_speed:
            case 2:
                return PortableWindSeedEnum.HEIGH
            case 1:
                return PortableWindSeedEnum.LOW
            case 0:
                return PortableWindSeedEnum.AUTO
            case _:
                return PortableWindSeedEnum.AUTO

    def getTemperatureType(self) -> TemperatureTypeEnum:
        match self.data.temperature_type:
            case 1:
                return TemperatureTypeEnum.FAHRENHEIT
            case 0:
                return TemperatureTypeEnum.CELSIUS
            case _:
                return TemperatureTypeEnum.CELSIUS

