"""Interfaces with the Example api sensors."""

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .config_entry import New_NameConfigEntry
from .const import DOMAIN
from .device import Device, toDeviceInfo

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: New_NameConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Binary Sensors."""

    sensors = []
    for device in config_entry.non_implemented_devices:
        sensors.append(NotImplementedDeviceBinarySensor(device))

    async_add_entities(sensors)


class NotImplementedDeviceBinarySensor(BinarySensorEntity):
    def __init__(self, device: Device) -> None:
        self.device = device
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{DOMAIN}-{type}-{device.device_id}"

    @property
    def unique_id(self) -> str:
        return self._attr_unique_id

    @property
    def device_info(self) -> DeviceInfo:
        return toDeviceInfo(self.device)

    @property
    def name(self) -> str:
        return "NotImplemented"

    @property
    def state_class(self) -> str | None:
        return None

    @property
    def device_class(self) -> str:
        return BinarySensorDeviceClass.POWER

    @property
    def is_on(self) -> bool | None:
        return False
