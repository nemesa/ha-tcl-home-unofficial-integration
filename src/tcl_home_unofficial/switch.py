"""Switch setup for our Integration."""

import logging
from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .aws_iot import AwsIot
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

    aws_iot = AwsIot(
        hass=hass,
        config_entry=config_entry,
    )
    await aws_iot.async_init()

    switches = []
    for device in config_entry.devices:
        switches.append(PowerSwitch(coordinator, device, aws_iot))

    async_add_entities(switches)


class PowerSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(
        self, coordinator: IotDeviceCoordinator, device: Device, aws_iot: AwsIot
    ) -> None:
        super().__init__(coordinator)
        self.device = device
        self.aws_iot = aws_iot

    @callback
    def _handle_coordinator_update(self) -> None:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        self.async_write_ha_state()

    @property
    def device_class(self) -> str:
        return SwitchDeviceClass.SWITCH

    @property
    def unique_id(self) -> str:
        return f"{DOMAIN}-PowerSwitch-{self.device.device_id}"

    @property
    def device_info(self) -> DeviceInfo:
        return toDeviceInfo(self.device)

    @property
    def name(self) -> str:
        return "Power Switch"

    @property
    def is_on(self) -> bool | None:
        device = self.coordinator.get_device_by_id(self.device.device_id)
        return device.data.power_switch

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.aws_iot.turnOn(self.device.device_id)

        self.device.data.power_switch = 1
        self.coordinator.set_device(self.device)
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.aws_iot.async_turnOff(self.device.device_id)

        self.device.data.power_switch = 0
        self.coordinator.set_device(self.device)
        await self.coordinator.async_refresh()
