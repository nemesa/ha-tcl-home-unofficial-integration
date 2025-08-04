"""Interfaces with the Example api sensors."""

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .config_entry import New_NameConfigEntry
from .coordinator import IotDeviceCoordinator
from .device_features import DeviceFeatureEnum
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
        if DeviceFeatureEnum.SENSOR_IS_ONLINE in device.supported_features:
            sensors.append(
                DynamicBinarySensorHandlerNoAutoIsOnlineCheck(
                    coordinator=coordinator,
                    device=device,
                    type="IsOnline",
                    name="Is Online",
                    deviceFeature=DeviceFeatureEnum.SENSOR_IS_ONLINE,
                    icon_fn=lambda device: "mdi:cloud-check-outline"
                    if device.is_online == 1
                    else "mdi:cloud-cancel-outline",
                    is_on_fn=lambda device: device.is_online,
                    is_available_fn=lambda device: True,
                )
            )

    async_add_entities(sensors)


class BinarySensorHandler(TclEntityBase, BinarySensorEntity):
    def __init__(
        self,
        coordinator: IotDeviceCoordinator,
        device: Device,
        type: str,
        name: str,
        deviceFeature: DeviceFeatureEnum,
        icon_fn: lambda device: str,
        is_on_fn: lambda device: bool,
    ) -> None:
        TclEntityBase.__init__(self, coordinator, type, name, device)
        self.icon_fn = icon_fn
        self.is_on_fn = is_on_fn
        self.entity_description = BinarySensorEntityDescription(
            key=deviceFeature,
            translation_key=deviceFeature,
        )

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


class DynamicBinarySensorHandlerNoAutoIsOnlineCheck(
    BinarySensorHandler, BinarySensorEntity
):
    def __init__(
        self,
        coordinator: IotDeviceCoordinator,
        device: Device,
        type: str,
        name: str,
        deviceFeature: DeviceFeatureEnum,
        icon_fn: lambda device: str,
        is_on_fn: lambda device: bool,
        is_available_fn: lambda device: bool,
    ) -> None:
        BinarySensorHandler.__init__(
            self,
            coordinator=coordinator,
            device=device,
            type=type,
            name=name,
            deviceFeature=deviceFeature,
            icon_fn=icon_fn,
            is_on_fn=is_on_fn,
        )
        self.is_available_fn = is_available_fn

    @property
    def available(self) -> bool:
        return self.is_available_fn(self.device)
