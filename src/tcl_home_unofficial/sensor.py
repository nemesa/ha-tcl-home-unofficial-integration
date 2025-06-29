"""Interfaces with the Integration 101 Template api sensors."""

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .config_entry import New_NameConfigEntry
from .const import DOMAIN
from .coordinator import IotDeviceCoordinator
from .device import Device, toDeviceInfo

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

    # Create the binary sensors.
    async_add_entities(sensors)


class TargetTemperatureSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        super().__init__(coordinator)
        self.device = device

    @callback
    def _handle_coordinator_update(self) -> None:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        self.async_write_ha_state()

    @property
    def device_class(self) -> str:
        return SensorDeviceClass.TEMPERATURE

    @property
    def device_info(self) -> DeviceInfo:
        return toDeviceInfo(self.device)

    @property
    def name(self) -> str:
        return "Target Temperature"

    @property
    def native_value(self) -> int | float:
        return float(self.device.data.target_temperature)

    @property
    def native_unit_of_measurement(self) -> str | None:
        return UnitOfTemperature.CELSIUS

    @property
    def state_class(self) -> str | None:
        return SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        return f"{DOMAIN}-TargetTemperature-{self.device.device_id}"
