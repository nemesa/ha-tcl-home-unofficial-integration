"""Interfaces with the Example api sensors."""

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import generate_entity_id
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
    """Set up the Binary Sensors."""

    coordinator = config_entry.runtime_data.coordinator

    sensors = []
    for device in config_entry.devices:
        sensors.append(PowerStateBinarySensor(coordinator, device))
        sensors.append(BeepSwitchBinarySensor(coordinator, device))

    async_add_entities(sensors)


class PowerStateBinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        super().__init__(coordinator)
        self.device = device

    @callback
    def _handle_coordinator_update(self) -> None:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        self.async_write_ha_state()

    @property
    def device_class(self) -> str:
        return BinarySensorDeviceClass.POWER

    @property
    def device_info(self) -> DeviceInfo:
        return toDeviceInfo(self.device)

    @property
    def name(self) -> str:
        return "Power State"

    @property
    def is_on(self) -> bool | None:
        return self.device.data.power_switch

    @property
    def unique_id(self) -> str:
        return f"{DOMAIN}-PowerState-{self.device.device_id}"


class BeepSwitchBinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        super().__init__(coordinator)
        self.device = device

    @callback
    def _handle_coordinator_update(self) -> None:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        self.async_write_ha_state()

    @property
    def device_class(self) -> str:
        return BinarySensorDeviceClass.SOUND

    @property
    def device_info(self) -> DeviceInfo:
        return toDeviceInfo(self.device)

    @property
    def name(self) -> str:
        return "Beep Switch State"

    @property
    def is_on(self) -> bool | None:
        return self.device.data.beep_switch

    @property
    def unique_id(self) -> str:
        return f"{DOMAIN}-BeepSwitch-{self.device.device_id}"
