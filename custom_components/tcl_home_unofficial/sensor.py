"""Interfaces with the Integration 101 Template api sensors."""

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfEnergy, UnitOfTemperature, UnitOfTime, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .config_entry import New_NameConfigEntry
from .coordinator import IotDeviceCoordinator
from .device import Device
from .device_features import DeviceFeatureEnum
from .tcl_entity_base import TclEntityBase

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
            sensors.append(
                TemperatureSensor(
                    coordinator=coordinator,
                    device=device,
                    type="CurrentTemperature",
                    name="Current Temperature",
                    value_fn=lambda device: device.data.current_temperature,
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
                    device_classification=SensorDeviceClass.DATA_SIZE,
                    state_classification=SensorStateClass.MEASUREMENT,
                    icon_fn=lambda device: "mdi:dots-hexagon",
                    native_unit_of_measurement="",
                    value_fn=lambda device: device.data.tvoc_level,
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
        return ""

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