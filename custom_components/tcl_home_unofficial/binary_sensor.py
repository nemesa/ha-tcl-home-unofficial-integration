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
from .device import Device, DeviceTypeEnum
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
    # for device in config_entry.devices:
    #     if device.device_type == DeviceTypeEnum.SPLIT_AC_TYPE_1:
    #         sensors.append(
    #             BinarySensor(
    #                 coordinator=coordinator,
    #                 device=device,
    #                 type="BeepMode",
    #                 name="Beep Mode",
    #                 icon_fn=lambda device: "mdi:volume-high"
    #                 if device.data.beep_switch == 1
    #                 else "mdi:volume-off",
    #                 is_on_fn=lambda device: device.data.beep_switch,
    #             )
    #         )

    async_add_entities(sensors)


class BinarySensor(TclEntityBase, BinarySensorEntity):
    def __init__(
        self,
        coordinator: IotDeviceCoordinator,
        device: Device,
        type: str,
        name: str,
        icon_fn: lambda device: str,
        is_on_fn: lambda device: bool,
    ) -> None:
        TclEntityBase.__init__(self, coordinator, type, name, device)
        self.icon_fn = icon_fn
        self.is_on_fn = is_on_fn

    @property
    def icon(self):
        return self.icon_fn(self.device)

    @property
    def device_class(self) -> str:
        return BinarySensorDeviceClass.POWER

    @property
    def is_on(self) -> bool | None:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        return self.is_on_fn(self.device)
