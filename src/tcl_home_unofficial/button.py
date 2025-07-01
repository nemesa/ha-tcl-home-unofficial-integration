"""Switch setup for our Integration."""

import logging
from typing import Any

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .aws_iot import AwsIot
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

    aws_iot = AwsIot(
        hass=hass,
        config_entry=config_entry,
    )
    await aws_iot.async_init()

    switches = []
    for device in config_entry.devices:
        switches.append(SelfCleanButton(coordinator, device, aws_iot))

    async_add_entities(switches)


class SelfCleanButton(TclEntityBase, ButtonEntity):
    def __init__(
        self, coordinator: IotDeviceCoordinator, device: Device, aws_iot: AwsIot
    ) -> None:
        TclEntityBase.__init__(
            self, coordinator, "SelfCleanButton", "Evaporator Clean", device
        )

        self.aws_iot = aws_iot

    @property
    def name(self) -> str:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        if self.device.data.self_clean == 1:
            return "Stop Evaporator Cleaning"
        return "Start Evaporator Cleaning"

    @property
    def device_class(self) -> str:
        return ButtonDeviceClass.UPDATE

    @property
    def icon(self):
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        if self.device.data.self_clean == 1:
            return "mdi:cancel"
        return "mdi:broom"

    async def async_press(self) -> None:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        if self.device.data.self_clean == 1:
            await self.aws_iot.async_self_clean_stop(self.device.device_id)
        else:
            await self.aws_iot.async_self_clean_start(self.device.device_id)
        await self.coordinator.async_refresh()
