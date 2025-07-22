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


class DesiredStateHandlerForSwitch:
    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: IotDeviceCoordinator,
        deviceFeature: DeviceFeature,
        device: Device,
    ) -> None:
        self.hass = hass
        self.coordinator = coordinator
        self.deviceFeature = deviceFeature
        self.device = device

    def refreshDevice(self, device: Device):
        self.device = device

    async def call_switch(self, value: int) -> str:
        match self.deviceFeature:
            case DeviceFeature.SWITCH_POWER:
                return await self.SWITCH_POWER(value=value)
            case DeviceFeature.SWITCH_HEALTHY:
                return await self.SWITCH_HEALTHY(value=value)
            case DeviceFeature.SWITCH_BEEP:
                return await self.SWITCH_BEEP(value=value)
            case DeviceFeature.SWITCH_ECO:
                return await self.SWITCH_ECO(value=value)
            case DeviceFeature.SWITCH_DRYING:
                return await self.SWITCH_DRYING(value=value)
            case DeviceFeature.SWITCH_SCREEN:
                return await self.SWITCH_SCREEN(value=value)
            case DeviceFeature.SWITCH_LIGHT_SENSE:
                return await self.SWITCH_LIGHT_SENSE(value=value)
            case DeviceFeature.SWITCH_SWING_WIND:
                return await self.SWITCH_SWING_WIND(value=value)
            case DeviceFeature.SWITCH_SLEEP:
                return await self.SWITCH_SLEEP(value=value)

    async def SWITCH_POWER(self, value: int):
        turnOffBeep = self.coordinator.get_config_data().behavior_mute_beep_on_power_on
        desired_state = {"powerSwitch": value}
        if turnOffBeep and value == 1:
            desired_state["beepSwitch"] = 0
        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )

    async def SWITCH_BEEP(self, value: int):
        desired_state = {"beepSwitch": value}
        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )

    async def SWITCH_ECO(self, value: int):
        desired_state = {"ECO": value}
        if self.device.device_type == DeviceTypeEnum.SPLIT_AC_TYPE_1:
            desired_state["highTemperatureWind"] = 0
            desired_state["turbo"] = 0
            desired_state["silenceSwitch"] = 0
            desired_state["windSpeed"] = 0

        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )

    async def SWITCH_HEALTHY(self, value: int):
        desired_state = {"healthy": value}
        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )

    async def SWITCH_DRYING(self, value: int):
        desired_state = {"antiMoldew": value}
        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )

    async def SWITCH_SCREEN(self, value: int):
        desired_state = {"screen": value}
        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )

    async def SWITCH_LIGHT_SENSE(self, value: int):
        desired_state = {"lightSense": value}
        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )

    async def SWITCH_SWING_WIND(self, value: int):
        desired_state = {"swingWind": value}
        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )

    async def SWITCH_SLEEP(self, value: int):
        desired_state = {"sleep": value}
        if self.device.device_type == DeviceTypeEnum.PORTABLE_AC:
            desired_state["windSpeed"] = 1 if value == 1 else 2
        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )


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
                SwitchHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeature.SWITCH_POWER,
                    type="Power",
                    name="Power Switch",
                    icon_fn=lambda device: "mdi:power-plug"
                    if device.data.power_switch == 1
                    else "mdi:power-plug-off",
                    is_on_fn=lambda device: device.data.power_switch,
                )
            )

        if DeviceFeature.SWITCH_BEEP in supported_features:
            switches.append(
                SwitchHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeature.SWITCH_BEEP,
                    type="BeepMode",
                    name="Beep Mode Switch",
                    icon_fn=lambda device: "mdi:volume-high"
                    if device.data.beep_switch == 1
                    else "mdi:volume-off",
                    is_on_fn=lambda device: device.data.beep_switch,
                )
            )

        if DeviceFeature.SWITCH_ECO in supported_features:
            switches.append(
                SwitchHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeature.SWITCH_ECO,
                    type="ECO",
                    name="ECO Switch",
                    icon_fn=lambda device: "mdi:leaf"
                    if device.data.eco == 1
                    else "mdi:leaf-off",
                    is_on_fn=lambda device: device.data.eco,
                )
            )

        if DeviceFeature.SWITCH_HEALTHY in supported_features:
            switches.append(
                SwitchHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeature.SWITCH_HEALTHY,
                    type="Healthy",
                    name="Healthy Switch",
                    icon_fn=lambda device: "mdi:heart"
                    if device.data.healthy == 1
                    else "mdi:heart-off",
                    is_on_fn=lambda device: device.data.healthy,
                )
            )

        if DeviceFeature.SWITCH_DRYING in supported_features:
            switches.append(
                SwitchHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeature.SWITCH_DRYING,
                    type="Drying",
                    name="Drying Switch",
                    icon_fn=lambda device: "mdi:opacity"
                    if device.data.anti_moldew == 1
                    else "mdi:water-off-outline",
                    is_on_fn=lambda device: device.data.anti_moldew,
                )
            )

        if DeviceFeature.SWITCH_SCREEN in supported_features:
            switches.append(
                SwitchHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeature.SWITCH_SCREEN,
                    type="DiplayLight",
                    name="Diplay Light Switch",
                    icon_fn=lambda device: "mdi:lightbulb-outline"
                    if device.data.screen == 1
                    else "mdi:lightbulb-off-outline",
                    is_on_fn=lambda device: device.data.screen,
                )
            )

        if DeviceFeature.SWITCH_LIGHT_SENSE in supported_features:
            switches.append(
                SwitchHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeature.SWITCH_LIGHT_SENSE,
                    type="LightSense",
                    name="Light Sense",
                    icon_fn=lambda device: "mdi:theme-light-dark",
                    is_on_fn=lambda device: device.data.light_sense,
                )
            )

        if DeviceFeature.SWITCH_SWING_WIND in supported_features:
            switches.append(
                SwitchHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeature.SWITCH_SWING_WIND,
                    type="SwingWind",
                    name="Up and down wind",
                    icon_fn=lambda device: "mdi:swap-vertical",
                    is_on_fn=lambda device: device.data.swing_wind,
                )
            )

        if DeviceFeature.SWITCH_SLEEP in supported_features:
            switches.append(
                DynamicSwitchHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeature.SWITCH_SLEEP,
                    type="Sleep",
                    name="Sleep",
                    icon_fn=lambda device: "mdi:sleep",
                    is_on_fn=lambda device: device.data.sleep,
                    available_fn=lambda device: (device.data.work_mode != 3),
                )
            )

    async_add_entities(switches)


class SwitchHandler(TclEntityBase, SwitchEntity):
    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: IotDeviceCoordinator,
        device: Device,
        type: str,
        name: str,
        deviceFeature: DeviceFeature,
        icon_fn: lambda device: str,
        is_on_fn: lambda device: bool | None,
    ) -> None:
        TclEntityBase.__init__(self, coordinator, type, name, device)
        self.icon_fn = icon_fn
        self.is_on_fn = is_on_fn
        self.iot_handler = DesiredStateHandlerForSwitch(hass=hass,coordinator=coordinator, deviceFeature=deviceFeature, device=self.device
        )

    @property
    def device_class(self) -> str:
        return SwitchDeviceClass.SWITCH

    @property
    def icon(self):
        return self.icon_fn(self.device)

    @property
    def is_on(self) -> bool | None:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        self.iot_handler.refreshDevice(self.device)
        return self.is_on_fn(self.device)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.iot_handler.call_switch(1)
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.iot_handler.call_switch(0)
        await self.coordinator.async_refresh()


class DynamicSwitchHandler(SwitchHandler, SwitchEntity):
    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: IotDeviceCoordinator,
        device: Device,
        type: str,
        name: str,
        deviceFeature: DeviceFeature,
        icon_fn: lambda device: str,
        is_on_fn: lambda device: bool | None,
        available_fn: lambda device: bool,
    ) -> None:
        SwitchHandler.__init__(
            self,
            coordinator=coordinator,
            device=device,
            type=type,
            name=name,
            deviceFeature=deviceFeature,
            hass=hass,
            icon_fn=icon_fn,
            is_on_fn=is_on_fn,
        )

        self.available_fn = available_fn

    @property
    def available(self) -> bool:
        return self.available_fn(self.device)
