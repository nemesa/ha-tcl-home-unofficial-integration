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
from .device import Device, getModeFromDeviceData
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

    # Create the binary sensors.
    async_add_entities(sensors)


class TargetTemperatureSensor(TclEntityBase, SensorEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        TclEntityBase.__init__(
            self, coordinator, "TargetTemperature", "Target Temperature", device
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
        TclEntityBase.__init__(self, coordinator, "Mode", "Mode", device)

    @property
    def device_class(self) -> str:
        return SensorDeviceClass.ENUM

    @property
    def native_value(self) -> int | float:
        self.device: Device = self.coordinator.get_device_by_id(self.device.device_id)
        return getModeFromDeviceData(self.device.data)

    @property
    def native_unit_of_measurement(self) -> str | None:
        return None

    @property
    def state_class(self) -> str | None:
        return SensorStateClass.MEASUREMENT
