"""Interfaces with the Example api sensors."""

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .config_entry import New_NameConfigEntry
from .coordinator import IotDeviceCoordinator
from .device import Device
from .tcl_entity_base import TclEntityBase

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: New_NameConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Binary Sensors."""

    coordinator = config_entry.runtime_data.coordinator

    sensors = []
    for device in config_entry.devices:
        sensors.append(PowerStateBinarySensor(coordinator, device))
        sensors.append(BeepSwitchBinarySensor(coordinator, device))
        sensors.append(EcoSwitchBinarySensor(coordinator, device))
        sensors.append(HealthySwitchBinarySensor(coordinator, device))
        sensors.append(BeepSwitchBinarySensor(coordinator, device))

    async_add_entities(sensors)


class PowerStateBinarySensor(TclEntityBase, BinarySensorEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        TclEntityBase.__init__(self, coordinator, "Power-State-sensor", "Power State", device)

    @property
    def device_class(self) -> str:
        return BinarySensorDeviceClass.POWER

    @property
    def is_on(self) -> bool | None:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        return self.device.data.power_switch


class BeepSwitchBinarySensor(TclEntityBase, BinarySensorEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        TclEntityBase.__init__(
            self, coordinator, "Beep-Switch-sensor", "Beep Switch State", device
        )

    @property
    def icon(self):
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        if self.device.data.beep_switch == 1:
            return "mdi:volume-high"
        return "mdi:volume-off"

    @property
    def device_class(self) -> str:
        return BinarySensorDeviceClass.POWER

    @property
    def is_on(self) -> bool | None:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        return self.device.data.beep_switch

class EcoSwitchBinarySensor(TclEntityBase, BinarySensorEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        TclEntityBase.__init__(
            self, coordinator, "ECO-Switch-sensor", "Eco Switch State", device
        )

    @property
    def icon(self):
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        if self.device.data.eco == 1:
            return "mdi:volume-high"
        return "mdi:volume-off"

    @property
    def device_class(self) -> str:
        return BinarySensorDeviceClass.POWER

    @property
    def is_on(self) -> bool | None:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        return self.device.data.eco


class HealthySwitchBinarySensor(TclEntityBase, BinarySensorEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        TclEntityBase.__init__(
            self, coordinator, "Healthy-Switch-sensor", "Healthy Switch State", device
        )

    @property
    def icon(self):
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        if self.device.data.healthy == 1:
            return "mdi:volume-high"
        return "mdi:volume-off"

    @property
    def device_class(self) -> str:
        return BinarySensorDeviceClass.POWER

    @property
    def is_on(self) -> bool | None:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        return self.device.data.healthy


class DryingSwitchBinarySensor(TclEntityBase, BinarySensorEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        TclEntityBase.__init__(
            self, coordinator, "Drying-Switch-sensor", "Drying Switch State", device
        )

    @property
    def icon(self):
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        if self.device.data.anti_moldew == 1:
            return "mdi:volume-high"
        return "mdi:volume-off"

    @property
    def device_class(self) -> str:
        return BinarySensorDeviceClass.POWER

    @property
    def is_on(self) -> bool | None:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        return self.device.data.anti_moldew                