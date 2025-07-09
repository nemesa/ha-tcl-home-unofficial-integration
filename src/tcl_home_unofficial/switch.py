"""Switch setup for our Integration."""

import logging
from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
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

    switches = []
    for device in config_entry.devices:
        if device.device_type == DeviceTypeEnum.SPLIT_AC:
            switches.append(
                Switch(
                    coordinator=coordinator,
                    device=device,
                    type="Power",
                    name="Power Switch",
                    icon_fn=lambda device: "mdi:power-plug"
                    if device.data.power_switch == 1
                    else "mdi:power-plug-off",
                    is_on_fn=lambda device: device.data.power_switch,
                    turn_on_fn=lambda device: coordinator.get_aws_iot().async_set_power(
                        device.device_id, 1
                    ),
                    turn_off_fn=lambda device: coordinator.get_aws_iot().async_set_power(
                        device.device_id, 0
                    ),
                )
            )
            switches.append(
                Switch(
                    coordinator=coordinator,
                    device=device,
                    type="BeepMode",
                    name="Beep Mode Switch",
                    icon_fn=lambda device: "mdi:volume-high"
                    if device.data.beep_switch == 1
                    else "mdi:volume-off",
                    is_on_fn=lambda device: device.data.beep_switch,
                    turn_on_fn=lambda device: coordinator.get_aws_iot().async_set_beep_mode(
                        device.device_id, 1
                    ),
                    turn_off_fn=lambda device: coordinator.get_aws_iot().async_set_beep_mode(
                        device.device_id, 0
                    ),
                )
            )
            switches.append(
                Switch(
                    coordinator=coordinator,
                    device=device,
                    type="ECO",
                    name="ECO Switch",
                    icon_fn=lambda device: "mdi:leaf"
                    if device.data.eco == 1
                    else "mdi:leaf-off",
                    is_on_fn=lambda device: device.data.eco,
                    turn_on_fn=lambda device: coordinator.get_aws_iot().async_set_eco(
                        device.device_id, 1
                    ),
                    turn_off_fn=lambda device: coordinator.get_aws_iot().async_set_eco(
                        device.device_id, 0
                    ),
                )
            )
            switches.append(
                Switch(
                    coordinator=coordinator,
                    device=device,
                    type="Healthy",
                    name="Healthy Switch",
                    icon_fn=lambda device: "mdi:heart"
                    if device.data.healthy == 1
                    else "mdi:heart-off",
                    is_on_fn=lambda device: device.data.healthy,
                    turn_on_fn=lambda device: coordinator.get_aws_iot().async_set_healthy(
                        device.device_id, 1
                    ),
                    turn_off_fn=lambda device: coordinator.get_aws_iot().async_set_healthy(
                        device.device_id, 0
                    ),
                )
            )
            switches.append(
                Switch(
                    coordinator=coordinator,
                    device=device,
                    type="Drying",
                    name="Drying Switch",
                    icon_fn=lambda device: "mdi:opacity"
                    if device.data.anti_moldew == 1
                    else "mdi:water-off-outline",
                    is_on_fn=lambda device: device.data.anti_moldew,
                    turn_on_fn=lambda device: coordinator.get_aws_iot().async_set_drying(
                        device.device_id, 1
                    ),
                    turn_off_fn=lambda device: coordinator.get_aws_iot().async_set_drying(
                        device.device_id, 0
                    ),
                )
            )
            switches.append(
                Switch(
                    coordinator=coordinator,
                    device=device,
                    type="DiplayLight",
                    name="Diplay Light Switch",
                    icon_fn=lambda device: "mdi:lightbulb-outline"
                    if device.data.screen == 1
                    else "mdi:lightbulb-off-outline",
                    is_on_fn=lambda device: device.data.screen,
                    turn_on_fn=lambda device: coordinator.get_aws_iot().async_set_light(
                        device.device_id, 1
                    ),
                    turn_off_fn=lambda device: coordinator.get_aws_iot().async_set_light(
                        device.device_id, 0
                    ),
                )
            )

    async_add_entities(switches)


class Switch(TclEntityBase, SwitchEntity):
    def __init__(
        self,
        coordinator: IotDeviceCoordinator,
        device: Device,
        type: str,
        name: str,
        icon_fn: lambda device: str,
        is_on_fn: lambda device: bool | None,
        turn_on_fn: lambda device: None,
        turn_off_fn: lambda device: None,
    ) -> None:
        TclEntityBase.__init__(self, coordinator, type, name, device)
        self.icon_fn = icon_fn
        self.turn_on_fn = turn_on_fn
        self.turn_off_fn = turn_off_fn
        self.is_on_fn = is_on_fn

    @property
    def device_class(self) -> str:
        return SwitchDeviceClass.SWITCH

    @property
    def icon(self):
        return self.icon_fn(self.device)

    @property
    def is_on(self) -> bool | None:
        device = self.coordinator.get_device_by_id(self.device.device_id)
        return self.is_on_fn(device)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.turn_on_fn(self.device)
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.turn_off_fn(self.device)
        await self.coordinator.async_refresh()
