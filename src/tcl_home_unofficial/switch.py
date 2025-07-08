"""Switch setup for our Integration."""

import logging
from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
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

    switches = []
    for device in config_entry.devices:
        switches.append(PowerSwitch(coordinator, device))
        switches.append(BeepSwitch(coordinator, device))
        switches.append(EcoSwitch(coordinator, device))
        switches.append(HealthySwitch(coordinator, device))
        switches.append(DryingSwitch(coordinator, device))
        switches.append(LightSwitch(coordinator, device))

    async_add_entities(switches)


class PowerSwitch(TclEntityBase, SwitchEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        TclEntityBase.__init__(self, coordinator, "PowerSwitch", "Power Switch", device)

        self.aws_iot = coordinator.get_aws_iot()

    @property
    def device_class(self) -> str:
        return SwitchDeviceClass.SWITCH

    @property
    def icon(self):
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        if self.device.data.power_switch == 1:
            return "mdi:power-plug"
        return "mdi:power-plug-off"

    @property
    def is_on(self) -> bool | None:
        device = self.coordinator.get_device_by_id(self.device.device_id)
        return device.data.power_switch

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.aws_iot.async_set_power(self.device.device_id, 1)

        self.device.data.power_switch = 1
        self.coordinator.set_device(self.device)
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.aws_iot.async_set_power(self.device.device_id, 0)

        self.device.data.power_switch = 0
        self.coordinator.set_device(self.device)
        await self.coordinator.async_refresh()


class BeepSwitch(TclEntityBase, SwitchEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        TclEntityBase.__init__(self, coordinator, "BeepSwitch", "Beep", device)

        self.aws_iot = coordinator.get_aws_iot()

    @property
    def device_class(self) -> str:
        return SwitchDeviceClass.SWITCH

    @property
    def icon(self):
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        if self.device.data.beep_switch == 1:
            return "mdi:volume-high"
        return "mdi:volume-off"

    @property
    def is_on(self) -> bool | None:
        device = self.coordinator.get_device_by_id(self.device.device_id)
        return device.data.beep_switch

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.aws_iot.async_set_beep_mode(self.device.device_id, 1)

        self.device.data.beep_switch = 1
        self.coordinator.set_device(self.device)
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.aws_iot.async_set_beep_mode(self.device.device_id, 0)

        self.device.data.beep_switch = 0
        self.coordinator.set_device(self.device)
        await self.coordinator.async_refresh()


class EcoSwitch(TclEntityBase, SwitchEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        TclEntityBase.__init__(self, coordinator, "ECO-Switch", "ECO", device)

        self.aws_iot = coordinator.get_aws_iot()

    @property
    def device_class(self) -> str:
        return SwitchDeviceClass.SWITCH

    @property
    def icon(self):
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        if self.device.data.eco == 1:
            return "mdi:leaf"
        return "mdi:leaf-off"

    @property
    def is_on(self) -> bool | None:
        device = self.coordinator.get_device_by_id(self.device.device_id)
        return device.data.eco

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.aws_iot.async_set_eco(self.device.device_id, 1)

        self.device.data.eco = 1
        self.coordinator.set_device(self.device)
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.aws_iot.async_set_eco(self.device.device_id, 0)

        self.device.data.eco = 0
        self.coordinator.set_device(self.device)
        await self.coordinator.async_refresh()


class HealthySwitch(TclEntityBase, SwitchEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        TclEntityBase.__init__(self, coordinator, "Helathy-Switch", "Healthy", device)

        self.aws_iot = coordinator.get_aws_iot()

    @property
    def device_class(self) -> str:
        return SwitchDeviceClass.SWITCH

    @property
    def icon(self):
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        if self.device.data.healthy == 1:
            return "mdi:heart"
        return "mdi:heart-off"

    @property
    def is_on(self) -> bool | None:
        device = self.coordinator.get_device_by_id(self.device.device_id)
        return device.data.healthy

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.aws_iot.async_set_healthy(self.device.device_id, 1)

        self.device.data.healthy = 1
        self.coordinator.set_device(self.device)
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.aws_iot.async_set_healthy(self.device.device_id, 0)

        self.device.data.healthy = 0
        self.coordinator.set_device(self.device)
        await self.coordinator.async_refresh()


class DryingSwitch(TclEntityBase, SwitchEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        TclEntityBase.__init__(self, coordinator, "Drying-Switch", "Drying", device)

        self.aws_iot = coordinator.get_aws_iot()

    @property
    def device_class(self) -> str:
        return SwitchDeviceClass.SWITCH

    @property
    def icon(self):
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        if self.device.data.anti_moldew == 1:
            return "mdi:water-opacity"
        return "mdi:water-off-outline"

    @property
    def is_on(self) -> bool | None:
        device = self.coordinator.get_device_by_id(self.device.device_id)
        return device.data.anti_moldew

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.aws_iot.async_set_drying(self.device.device_id, 1)

        self.device.data.anti_moldew = 1
        self.coordinator.set_device(self.device)
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.aws_iot.async_set_drying(self.device.device_id, 0)

        self.device.data.anti_moldew = 0
        self.coordinator.set_device(self.device)
        await self.coordinator.async_refresh()


class LightSwitch(TclEntityBase, SwitchEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        TclEntityBase.__init__(
            self, coordinator, "Light-Switch", "Screen Light", device
        )

        self.aws_iot = coordinator.get_aws_iot()

    @property
    def device_class(self) -> str:
        return SwitchDeviceClass.SWITCH

    @property
    def icon(self):
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        if self.device.data.screen == 1:
            return "mdi:lightbulb-outline"
        return "mdi:lightbulb-off-outline"

    @property
    def is_on(self) -> bool | None:
        device = self.coordinator.get_device_by_id(self.device.device_id)
        return device.data.screen

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.aws_iot.async_set_light(self.device.device_id, 1)

        self.device.data.screen = 1
        self.coordinator.set_device(self.device)
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.aws_iot.async_set_light(self.device.device_id, 0)

        self.device.data.screen = 0
        self.coordinator.set_device(self.device)
        await self.coordinator.async_refresh()
