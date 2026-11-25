"""Interfaces with the Integration 101 Template api sensors."""
import logging
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity,SensorStateClass
from homeassistant.const import UnitOfEnergy, UnitOfTemperature, UnitOfTime, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .config_entry import New_NameConfigEntry
from .coordinator import IotDeviceCoordinator
from .device import Device
from .device_features import DeviceFeatureEnum
from .device_types import DeviceTypeEnum
from .tcl_entity_base import TclEntityBase
from .weather_curves import (
    get_heating_curve_attributes,
    get_heating_curve_name,
)
_LOGGER = logging.getLogger(__name__)
async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: New_NameConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Sensors."""
    coordinator = config_entry.runtime_data.coordinator
    sensors = []
    for device in config_entry.devices:
        if DeviceFeatureEnum.SENSOR_CURRENT_TEMPERATURE in device.supported_features:
            s_name = "Room Temperature Zone 1" if device.device_type == DeviceTypeEnum.ATW_HEAT_PUMP else "Current Temperature"
            sensors.append(
                TemperatureSensor(
                    coordinator=coordinator,
                    device=device,
                    type="CurrentTemperature",
                    name=s_name,
                    value_fn=lambda device: device.data.current_temperature,
                )
            )
        if DeviceFeatureEnum.SENSOR_ATW_ZONE2_TEMPERATURE in device.supported_features:
            sensors.append(
                TemperatureSensor(
                    coordinator=coordinator,
                    device=device,
                    type="Zone2Temperature",
                    name="Zone 2 Temperature",
                    value_fn=lambda device: device.data.current_temp_2,
                )
            )
        if DeviceFeatureEnum.SENSOR_ATW_ZONE3_TEMPERATURE in device.supported_features:
            sensors.append(
                TemperatureSensor(
                    coordinator=coordinator,
                    device=device,
                    type="Zone3Temperature",
                    name="Zone 3 Temperature",
                    value_fn=lambda device: device.data.current_temp_3,
                )
            )
        if DeviceFeatureEnum.SENSOR_ATW_DHW_TEMPERATURE in device.supported_features:
            sensors.append(
                TemperatureSensor(
                    coordinator=coordinator,
                    device=device,
                    type="DomesticHotWaterTemperature",
                    name="Domestic Hot Water Temperature",
                    value_fn=lambda device: device.data.current_temp_domestic,
                )
            )
        if DeviceFeatureEnum.SENSOR_ATW_DHW_TARGET_TEMPERATURE in device.supported_features:
            sensors.append(
                TemperatureSensor(
                    coordinator=coordinator,
                    device=device,
                    type="TargetDomesticHotWaterTemperature",
                    name="Target Domestic Hot Water Temperature",
                    value_fn=lambda device: device.data.target_temp_domestic,
                )
            )
        if DeviceFeatureEnum.SENSOR_ATW_HEAT_Z1_TARGET_TEMPERATURE in device.supported_features:
            sensors.append(
                TemperatureSensor(
                    coordinator=coordinator,
                    device=device,
                    type="TargetHeatingWaterTempZone1",
                    name="Target Heating Water Temp Zone 1",
                    value_fn=lambda device: device.data.target_temp_heat_z1,
                )
            )
        if DeviceFeatureEnum.SENSOR_ATW_ROOM_Z1_TARGET in device.supported_features:
            sensors.append(
                TemperatureSensor(
                    coordinator=coordinator,
                    device=device,
                    type="TargetRoomTempZone1",
                    name="Target Room Temperature Zone 1",
                    value_fn=lambda device: device.data.target_temp_room_z1,
                )
            )
        if DeviceFeatureEnum.SENSOR_ATW_HEATING_CURVE_1 in device.supported_features:
            sensors.append(
                WeatherCurveSensor(
                    coordinator=coordinator,
                    device=device,
                    type="ATWHeatingCurve1",
                    name="Heating Weather Curve Zone 1",
                )
            )
        if DeviceFeatureEnum.SENSOR_ATW_CURVE_TARGET_WATER_TEMP_1 in device.supported_features:
            sensors.append(
                TemperatureSensor(
                    coordinator=coordinator,
                    device=device,
                    type="CurveTargetWaterTempZone1",
                    name="Curve Target Flow Temp Zone 1",
                    value_fn=lambda device: device.data.target_temp_curve_z1,
                )
            )
        if (
            DeviceFeatureEnum.SENSOR_ATW_WATER_TEMP_FLOW_1 in device.supported_features
            or DeviceFeatureEnum.SENSOR_ATW_WATER_TEMP_RETURN_1 in device.supported_features
        ):
            sensors.append(
                TemperatureSensor(
                    coordinator=coordinator,
                    device=device,
                    type="WaterFlowTempZone1",
                    name="Water Flow Temp Zone 1",
                    value_fn=lambda device: device.data.temp_water_flow_z1,
                )
            )
        if DeviceFeatureEnum.SENSOR_ATW_ESTIMATED_RETURN_WATER_TEMP_1 in device.supported_features:
            sensors.append(
                TemperatureSensor(
                    coordinator=coordinator,
                    device=device,
                    type="EstimatedReturnWaterTempZone1",
                    name="Estimated Return Water Temp Zone 1",
                    value_fn=lambda device: round(
                        (device.data.temp_water_flow_z1 - 4.0)
                        if device.data.temp_water_flow_z1 > 10
                        else device.data.temp_water_flow_z1,
                        1,
                    ),
                )
            )
        if DeviceFeatureEnum.SENSOR_ATW_ROOM_TEMP_RETURN_1 in device.supported_features:
            sensors.append(
                TemperatureSensor(
                    coordinator=coordinator,
                    device=device,
                    type="ReturnRoomTempZone1",
                    name="Return Room Temp Zone 1",
                    value_fn=lambda device: device.data.temp_room_return_z1,
                )
            )
        if DeviceFeatureEnum.SENSOR_ATW_COOLING_CURVE_1 in device.supported_features:
            sensors.append(
                IntNumberSensor(
                    coordinator=coordinator,
                    device=device,
                    type="ATWCoolingCurve1",
                    name="Cooling Weather Curve Zone 1 Sensor",
                    device_classification=None,
                    state_classification=None,
                    icon_fn=lambda device: "mdi:chart-bell-curve",
                    native_unit_of_measurement="",
                    value_fn=lambda device: device.data.cooling_curve_1,
                )
            )
        if DeviceFeatureEnum.SENSOR_INTERNAL_UNIT_COIL_TEMPERATURE in device.supported_features:
            sensors.append(
                TemperatureSensor(
                    coordinator=coordinator,
                    device=device,
                    type="InternalUnitCoilTemperature",
                    name="Internal Unit Coil Temperature",
                    value_fn=lambda device: device.data.internal_unit_coil_temperature,
                )
            )
        if DeviceFeatureEnum.SENSOR_EXTERNAL_UNIT_COIL_TEMPERATURE in device.supported_features:
            sensors.append(
                TemperatureSensor(
                    coordinator=coordinator,
                    device=device,
                    type="ExternalUnitCoilTemperature",
                    name="External Unit Coil Temperature",
                    value_fn=lambda device: device.data.external_unit_coil_temperature,
                )
            )
        if DeviceFeatureEnum.SENSOR_EXTERNAL_UNIT_TEMPERATURE in device.supported_features:
            sensors.append(
                TemperatureSensor(
                    coordinator=coordinator,
                    device=device,
                    type="ExternalUnitTemperature",
                    name="External Unit Temperature",
                    value_fn=lambda device: device.data.external_unit_temperature,
                )
            )
        if DeviceFeatureEnum.SENSOR_EXTERNAL_UNIT_EXHAUST_TEMPERATURE in device.supported_features:
            sensors.append(
                TemperatureSensor(
                    coordinator=coordinator,
                    device=device,
                    type="ExternalUnitExhaustTemperature",
                    name="External Unit Exhaust Temperature",
                    value_fn=lambda device: device.data.external_unit_exhaust_temperature,
                )
            )
        if DeviceFeatureEnum.SENSOR_DEHUMIDIFIER_ENV_HUMIDITY in device.supported_features:
            sensors.append(
                HumiditySensor(
                    coordinator=coordinator,
                    device=device,
                    type="DehumidifierEnvHumidity",
                    name="Environment Humidity",
                    value_fn=lambda device: device.data.env_humidity,
                )
            )
        if DeviceFeatureEnum.SENSOR_FRESH_AIR_TVOC in device.supported_features:
            sensors.append(
                VolatileOrganicCompoundsSensor(
                    coordinator=coordinator,
                    device=device,
                    type="TVOC.Value",
                    name="TVOC Value",
                    value_fn=lambda device: device.data.tvoc_value,
                )
            )
            sensors.append(
                IntNumberSensor(
                    coordinator=coordinator,
                    device=device,
                    type="TVOC.Level",
                    name="TVOC Level",
                    device_classification=None,
                    state_classification=SensorStateClass.MEASUREMENT,
                    icon_fn=lambda device: "mdi:dots-hexagon",
                    native_unit_of_measurement="",
                    value_fn=lambda device: device.data.tvoc_level,
                )
            )
        
        if DeviceFeatureEnum.SENSOR_SPLIT_AC_TVOC_VALUE in device.supported_features:
            sensors.append(
                VolatileOrganicCompoundsSensor(
                    coordinator=coordinator,
                    device=device,
                    type="SplitAC.TVOC.Value",
                    name="TVOC Value",
                    value_fn=lambda device: device.data.sensor_TVOC_value,
                )
            )
        
        if DeviceFeatureEnum.SENSOR_SPLIT_AC_TVOC_LEVEL in device.supported_features:
            sensors.append(
                IntNumberSensor(
                    coordinator=coordinator,
                    device=device,
                    type="SplitAC.TVOC.Level",
                    name="TVOC Level",
                    device_classification=None,
                    state_classification=SensorStateClass.MEASUREMENT,
                    icon_fn=lambda device: "mdi:dots-hexagon",
                    native_unit_of_measurement="",
                    value_fn=lambda device: device.data.sensor_TVOC_level,
                )
            )

        if DeviceFeatureEnum.SENSOR_PM25_SENSOR_LEVEL in device.supported_features:            
            sensors.append(
                IntNumberSensor(
                    coordinator=coordinator,
                    device=device,
                    type="PM25.Level",
                    name="PM25 Level",
                    device_classification=None,
                    state_classification=SensorStateClass.MEASUREMENT,
                    icon_fn=lambda device: "mdi:dots-hexagon",
                    native_unit_of_measurement="",
                    value_fn=lambda device: device.data.pm25_sensor_level,
                )
            )
        if DeviceFeatureEnum.SENSOR_VOC_SENSOR_LEVEL in device.supported_features:            
            sensors.append(
                IntNumberSensor(
                    coordinator=coordinator,
                    device=device,
                    type="TVOC.SENSOR.Level",
                    name="TVOC Level",
                    device_classification=None,
                    state_classification=SensorStateClass.MEASUREMENT,
                    icon_fn=lambda device: "mdi:dots-hexagon",
                    native_unit_of_measurement="",
                    value_fn=lambda device: device.data.voc_sensor_level,
                )
            )
        if DeviceFeatureEnum.SENSOR_POWER_CONSUMPTION_DAILY in device.supported_features:
            sensors.append(
                EnergyConsumptionSensor(
                    coordinator=coordinator,
                    device=device,
                    type="TodayEnergyConsumption",
                    name="Today Energy Consumption",
                    value_fn=lambda device: round(device.extra_tcl_data.get("today_total_electricity",0),2),
                )
            )
            sensors.append(
                EnergyConsumptionSensor(
                    coordinator=coordinator,
                    device=device,
                    type="YesterdayEnergyConsumption",
                    name="Yesterday Energy Consumption",
                    value_fn=lambda device: round(device.extra_tcl_data.get("yesterday_total_electricity",0),2),
                )
            )
        if DeviceFeatureEnum.SENSOR_WORK_TIME_DAILY in device.supported_features:            
            sensors.append(
                IntNumberSensor(
                    coordinator=coordinator,
                    device=device,
                    type="TodayWorkTime",
                    name="Today Work Time",
                    device_classification=SensorDeviceClass.DURATION,
                    state_classification=SensorStateClass.TOTAL_INCREASING,
                    native_unit_of_measurement=UnitOfTime.HOURS,
                    icon_fn=lambda device: "mdi:clock-time-eight-outline",
                    value_fn=lambda device: round((device.extra_tcl_data.get("today_work_time",0)/60),2),
                )
            )
            sensors.append(
                IntNumberSensor(
                    coordinator=coordinator,
                    device=device,
                    type="YesterdayWorkTime",
                    name="Yesterday Work Time",
                    device_classification=SensorDeviceClass.DURATION,
                    state_classification=SensorStateClass.TOTAL_INCREASING,
                    native_unit_of_measurement=UnitOfTime.HOURS,
                    icon_fn=lambda device: "mdi:clock-time-eight-outline",
                    value_fn=lambda device: round((device.extra_tcl_data.get("yesterday_work_time",0)/60),2),
                )
            )

        if DeviceFeatureEnum.SENSOR_FILTER_LIFETIME in device.supported_features:
            sensors.append(
                IntNumberSensor(
                    coordinator=coordinator,
                    device=device,
                    type="FilterLifeTime",
                    name="Filter Life Time",
                    device_classification=SensorDeviceClass.DURATION,
                    state_classification=SensorStateClass.MEASUREMENT,
                    native_unit_of_measurement=UnitOfTime.HOURS,
                    icon_fn=lambda device: "mdi:filter-check",
                    value_fn=lambda device: device.data.filter_life_time,
                )
            )
        
        if DeviceFeatureEnum.SENSOR_PM25_SENSOR_VALUE in device.supported_features:
            sensors.append(
                IntNumberSensor(
                    coordinator=coordinator,
                    device=device,
                    type="PM25SensorValue",
                    name="PM2.5 Sensor Value",
                    device_classification=SensorDeviceClass.PM25,
                    state_classification=SensorStateClass.MEASUREMENT,
                    native_unit_of_measurement="µg/m³",
                    icon_fn=lambda device: "mdi:air-filter",
                    value_fn=lambda device: device.data.pm25_sensor_value,
                )
            )

    async_add_entities(sensors)
class TemperatureSensor(TclEntityBase, SensorEntity):
    def __init__(
        self,
        coordinator: IotDeviceCoordinator,
        device: Device,
        type: str,
        name: str,
        value_fn,
    ) -> None:
        TclEntityBase.__init__(self, coordinator, type, name, device)
        self.value_fn = value_fn
    @property
    def device_class(self) -> str:
        return SensorDeviceClass.TEMPERATURE
    @property
    def native_value(self) -> int | float:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        return float(self.value_fn(self.device))
    @property
    def native_unit_of_measurement(self) -> str | None:
        return UnitOfTemperature.CELSIUS
    @property
    def state_class(self) -> str | None:
        return SensorStateClass.MEASUREMENT
class HumiditySensor(TclEntityBase, SensorEntity):
    def __init__(
        self,
        coordinator: IotDeviceCoordinator,
        device: Device,
        type: str,
        name: str,
        value_fn,
    ) -> None:
        TclEntityBase.__init__(self, coordinator, type, name, device)
        self.value_fn = value_fn
    @property
    def device_class(self) -> str:
        return SensorDeviceClass.HUMIDITY
    @property
    def native_value(self) -> int | float:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        return float(self.value_fn(self.device))
    @property
    def native_unit_of_measurement(self) -> str | None:
        return PERCENTAGE
    @property
    def state_class(self) -> str | None:
        return SensorStateClass.MEASUREMENT
class VolatileOrganicCompoundsSensor(TclEntityBase, SensorEntity):
    def __init__(
        self,
        coordinator: IotDeviceCoordinator,
        device: Device,
        type: str,
        name: str,
        value_fn,
    ) -> None:
        TclEntityBase.__init__(self, coordinator, type, name, device)
        self.value_fn = value_fn
        
        self.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER = "µg/m³"
        self.CONCENTRATION_MILLIGRAMS_PER_CUBIC_METER = "mg/m³"
        self.CONCENTRATION_MICROGRAMS_PER_CUBIC_FOOT = "μg/ft³"
        self.CONCENTRATION_PARTS_PER_CUBIC_METER = "p/m³"
        self.CONCENTRATION_PARTS_PER_MILLION = "ppm"
        self.CONCENTRATION_PARTS_PER_BILLION = "ppb"
    @property
    def device_class(self) -> str:
        return SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS
    @property
    def native_value(self) -> int | float:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        return float(self.value_fn(self.device))
    @property
    def native_unit_of_measurement(self) -> str | None:
        #??? don't know the unit of measurement we only know the value
        return self.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
    @property
    def state_class(self) -> str | None:
        return SensorStateClass.MEASUREMENT
    
    @property
    def icon(self):
        return "mdi:dots-hexagon"
class IntNumberSensor(TclEntityBase, SensorEntity):
    def __init__(
        self,
        coordinator: IotDeviceCoordinator,
        device: Device,
        type: str,
        name: str,
        value_fn,
        icon_fn: lambda device: str,
        device_classification: str,
        state_classification: str,
        native_unit_of_measurement: str,
    ) -> None:
        TclEntityBase.__init__(self, coordinator, type, name, device)
        self.value_fn = value_fn
        self.state_classification=state_classification
        self.device_classification=device_classification
        self.icon_fn = icon_fn
        self.input_native_unit_of_measurement=native_unit_of_measurement
    @property
    def icon(self):
        return self.icon_fn(self.device)
    
    @property
    def device_class(self) -> str:
        return self.device_classification
    @property
    def native_value(self) -> int | float:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        return int(self.value_fn(self.device))
    @property
    def native_unit_of_measurement(self) -> str | None:
        #??? don't know the unit of measurement we only know the value
        return self.input_native_unit_of_measurement
    @property
    def state_class(self) -> str | None:
        return self.state_classification
    
    
class EnergyConsumptionSensor(TclEntityBase, SensorEntity):
    def __init__(
        self,
        coordinator: IotDeviceCoordinator,
        device: Device,
        type: str,
        name: str,
        value_fn,
    ) -> None:
        TclEntityBase.__init__(self, coordinator, type, name, device)
        self.value_fn = value_fn
    @property
    def device_class(self) -> str:
        return SensorDeviceClass.ENERGY
    @property
    def native_value(self) -> int | float:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        return float(self.value_fn(self.device))
    @property
    def native_unit_of_measurement(self) -> str | None:
        return UnitOfEnergy.KILO_WATT_HOUR
    @property
    def state_class(self) -> str | None:
        return SensorStateClass.TOTAL_INCREASING


class WeatherCurveSensor(TclEntityBase, SensorEntity):
    def __init__(
        self,
        coordinator: IotDeviceCoordinator,
        device: Device,
        type: str,
        name: str,
    ) -> None:
        TclEntityBase.__init__(self, coordinator, type, name, device)

    @property
    def icon(self):
        return "mdi:chart-bell-curve"

    @property
    def native_value(self) -> str:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        idx = int(getattr(self.device.data, "heating_curve_1", 1))
        return get_heating_curve_name(idx)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        idx = int(getattr(self.device.data, "heating_curve_1", 1))
        ambient = getattr(self.device.data, "current_temperature", None)
        attrs = get_heating_curve_attributes(idx, ambient)
        attrs["grid_target_water_temp"] = getattr(self.device.data, "target_temp_curve_z1", 0)
        attrs["water_flow_temp"] = getattr(self.device.data, "temp_water_flow_z1", 0)
        attrs["estimated_return_water_temp"] = (
            round(attrs["water_flow_temp"] - 4.0, 1) if attrs["water_flow_temp"] > 10 else attrs["water_flow_temp"]
        )
        attrs["estimated_delta_t"] = 4.0 if attrs["water_flow_temp"] > 10 else 0.0
        attrs["weather_control_active"] = (
            getattr(self.device.data, "weather_control_sw_1", 0) == 1
        )
        return attrs
