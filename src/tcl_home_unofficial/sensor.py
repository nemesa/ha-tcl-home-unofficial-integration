"""Interfaces with the Integration 101 Template api sensors."""

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .config_entry import New_NameConfigEntry
from .coordinator import IotDeviceCoordinator
from .device import Device, TCL_SplitAC_DeviceData_Helper
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
        sensors.append(TargetTemperatureSensor(coordinator, device))
        sensors.append(ModeSensor(coordinator, device))
        sensors.append(WindSpeedSensor(coordinator, device))
        sensors.append(UpAndDownAirSupplyVectorSensor(coordinator, device))
        sensors.append(LeftAndRightAirSupplyVectorSensor(coordinator, device))
        sensors.append(SleepModeSensor(coordinator, device))

    # Create the binary sensors.
    async_add_entities(sensors)


class TargetTemperatureSensor(TclEntityBase, SensorEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        TclEntityBase.__init__(
            self, coordinator, "TargetTemperature-sensor", "Target Temperature", device
        )

    @property
    def device_class(self) -> str:
        return SensorDeviceClass.TEMPERATURE

    @property
    def native_value(self) -> int | float:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        return float(self.device.data.target_temperature)

    @property
    def native_unit_of_measurement(self) -> str | None:
        return UnitOfTemperature.CELSIUS

    @property
    def state_class(self) -> str | None:
        return SensorStateClass.MEASUREMENT


class ModeSensor(TclEntityBase, SensorEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        TclEntityBase.__init__(self, coordinator, "Mode-sensor", "Mode", device)

    @property
    def device_class(self) -> str:
        return SensorDeviceClass.ENUM

    @property
    def icon(self):
        return "mdi:set-none"

    @property
    def native_value(self) -> int | float:
        self.device: Device = self.coordinator.get_device_by_id(self.device.device_id)
        helper = TCL_SplitAC_DeviceData_Helper(self.device.data)
        return helper.getMode()

    @property
    def native_unit_of_measurement(self) -> str | None:
        return None

    # @property
    # def state_class(self) -> str | None:
    #     return SensorStateClass.MEASUREMENT


class WindSpeedSensor(TclEntityBase, SensorEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        TclEntityBase.__init__(
            self, coordinator, "WindSpeed-sensor", "Wind Speed", device
        )

    @property
    def device_class(self) -> str:
        return SensorDeviceClass.ENUM

    @property
    def icon(self):
        return "mdi:weather-windy"

    @property
    def native_value(self) -> int | float:
        self.device: Device = self.coordinator.get_device_by_id(self.device.device_id)
        helper = TCL_SplitAC_DeviceData_Helper(self.device.data)
        return helper.getWindSpeed()

    @property
    def native_unit_of_measurement(self) -> str | None:
        return None

    # @property
    # def state_class(self) -> str | None:
    #     return SensorStateClass.MEASUREMENT


class UpAndDownAirSupplyVectorSensor(TclEntityBase, SensorEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        TclEntityBase.__init__(
            self,
            coordinator,
            "UpAndDownAirSupplyVector-sensor",
            "Up and down air supply",
            device,
        )

    @property
    def device_class(self) -> str:
        return SensorDeviceClass.ENUM

    @property
    def icon(self):
        return "mdi:swap-vertical"

    @property
    def native_value(self) -> int | float:
        self.device: Device = self.coordinator.get_device_by_id(self.device.device_id)
        helper = TCL_SplitAC_DeviceData_Helper(self.device.data)
        return helper.getUpAndDownAirSupplyVector()

    @property
    def native_unit_of_measurement(self) -> str | None:
        return None

    # @property
    # def state_class(self) -> str | None:
    #     return SensorStateClass.MEASUREMENT


class LeftAndRightAirSupplyVectorSensor(TclEntityBase, SensorEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        TclEntityBase.__init__(
            self,
            coordinator,
            "LeftAndRightAirSupplyVector-sensor",
            "Left and right air supply",
            device,
        )

    @property
    def device_class(self) -> str:
        return SensorDeviceClass.ENUM

    @property
    def icon(self):
        return "mdi:swap-horizontal"

    @property
    def native_value(self) -> int | float:
        self.device: Device = self.coordinator.get_device_by_id(self.device.device_id)
        helper = TCL_SplitAC_DeviceData_Helper(self.device.data)
        return helper.getLeftAndRightAirSupplyVector()

    @property
    def native_unit_of_measurement(self) -> str | None:
        return None

    # @property
    # def state_class(self) -> str | None:
    #     return SensorStateClass.MEASUREMENT


class SleepModeSensor(TclEntityBase, SensorEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        TclEntityBase.__init__(
            self, coordinator, "Sleep-Mode-sensor", "Sleep Mode", device
        )

    @property
    def device_class(self) -> str:
        return SensorDeviceClass.ENUM

    @property
    def icon(self):
        return "mdi:sleep"

    @property
    def native_value(self) -> int | float:
        self.device: Device = self.coordinator.get_device_by_id(self.device.device_id)
        helper = TCL_SplitAC_DeviceData_Helper(self.device.data)
        return helper.getSleepMode()

    @property
    def native_unit_of_measurement(self) -> str | None:
        return None

    # @property
    # def state_class(self) -> str | None:
    #     return SensorStateClass.MEASUREMENT
