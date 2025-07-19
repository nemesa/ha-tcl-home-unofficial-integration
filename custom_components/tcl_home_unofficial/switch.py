"""Switch setup for our Integration."""

import logging
from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .config_entry import New_NameConfigEntry
from .coordinator import IotDeviceCoordinator
from .device import Device, getSupportedFeatures, DeviceFeature, DeviceTypeEnum
from .tcl_entity_base import TclEntityBase

_LOGGER = logging.getLogger(__name__)


def get_SWITCH_DRYING_name(device: Device) -> str:
    if device.device_type == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
        return "Mildewproof Switch"
    return "Drying Switch"


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: New_NameConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Binary Sensors."""
    coordinator = config_entry.runtime_data.coordinator

    switches = []
    for device in config_entry.devices:
        supported_features = getSupportedFeatures(device.device_type)

        if DeviceFeature.SWITCH_POWER in supported_features:
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
                        device.device_id, device.device_type, 1
                    ),
                    turn_off_fn=lambda device: coordinator.get_aws_iot().async_set_power(
                        device.device_id, device.device_type, 0
                    ),
                )
            )

        if DeviceFeature.SWITCH_BEEP in supported_features:
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
                        device.device_id, device.device_type, 1
                    ),
                    turn_off_fn=lambda device: coordinator.get_aws_iot().async_set_beep_mode(
                        device.device_id, device.device_type, 0
                    ),
                )
            )

        if DeviceFeature.SWITCH_ECO in supported_features:
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
                        device.device_id, device.device_type, 1
                    ),
                    turn_off_fn=lambda device: coordinator.get_aws_iot().async_set_eco(
                        device.device_id, device.device_type, 0
                    ),
                )
            )

        if DeviceFeature.SWITCH_HEALTHY in supported_features:
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
                        device.device_id, device.device_type, 1
                    ),
                    turn_off_fn=lambda device: coordinator.get_aws_iot().async_set_healthy(
                        device.device_id, device.device_type, 0
                    ),
                )
            )

        if DeviceFeature.SWITCH_DRYING in supported_features:
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
                        device.device_id, device.device_type, 1
                    ),
                    turn_off_fn=lambda device: coordinator.get_aws_iot().async_set_drying(
                        device.device_id, device.device_type, 0
                    ),
                )
            )

        if DeviceFeature.SWITCH_SCREEN in supported_features:
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
                        device.device_id, device.device_type, 1
                    ),
                    turn_off_fn=lambda device: coordinator.get_aws_iot().async_set_light(
                        device.device_id, device.device_type, 0
                    ),
                )
            )

        if DeviceFeature.SWITCH_LIGHT_SENSE in supported_features:
            switches.append(
                Switch(
                    coordinator=coordinator,
                    device=device,
                    type="LightSense",
                    name="Light Sense",
                    icon_fn=lambda device: "mdi:theme-light-dark",
                    is_on_fn=lambda device: device.data.light_sense,
                    turn_on_fn=lambda device: coordinator.get_aws_iot().async_set_light_sense(
                        device.device_id, device.device_type, 1
                    ),
                    turn_off_fn=lambda device: coordinator.get_aws_iot().async_set_light_sense(
                        device.device_id, device.device_type, 0
                    ),
                )
            )

        if DeviceFeature.SWITCH_SWING_WIND in supported_features:
            switches.append(
                Switch(
                    coordinator=coordinator,
                    device=device,
                    type="SwingWind",
                    name="Up and down wind",
                    icon_fn=lambda device: "mdi:swap-vertical",
                    is_on_fn=lambda device: device.data.swing_wind,
                    turn_on_fn=lambda device: coordinator.get_aws_iot().async_set_swing_wind(
                        device.device_id, device.device_type, 1
                    ),
                    turn_off_fn=lambda device: coordinator.get_aws_iot().async_set_swing_wind(
                        device.device_id, device.device_type, 0
                    ),
                )
            )

        if DeviceFeature.SWITCH_SLEEP in supported_features:
            switches.append(
                DynamicSwitch(
                    coordinator=coordinator,
                    device=device,
                    type="Sleep",
                    name="Sleep",
                    icon_fn=lambda device: "mdi:sleep",
                    is_on_fn=lambda device: device.data.sleep,
                    turn_on_fn=lambda device: coordinator.get_aws_iot().async_set_sleep(
                        device.device_id, device.device_type, 1
                    ),
                    turn_off_fn=lambda device: coordinator.get_aws_iot().async_set_sleep(
                        device.device_id, device.device_type, 0
                    ),
                    available_fn=lambda device: (device.data.work_mode != 3),
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


class DynamicSwitch(TclEntityBase, SwitchEntity):
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
        available_fn: lambda device: bool,
    ) -> None:
        TclEntityBase.__init__(self, coordinator, type, name, device)
        self.icon_fn = icon_fn
        self.turn_on_fn = turn_on_fn
        self.turn_off_fn = turn_off_fn
        self.is_on_fn = is_on_fn
        self.available_fn = available_fn

    @property
    def device_class(self) -> str:
        return SwitchDeviceClass.SWITCH

    @property
    def icon(self):
        return self.icon_fn(self.device)

    @property
    def available(self) -> bool:
        return self.available_fn(self.device)

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
