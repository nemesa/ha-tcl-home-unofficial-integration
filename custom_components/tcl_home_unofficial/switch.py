"""Switch setup for our Integration."""

import logging
from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .config_entry import New_NameConfigEntry
from .coordinator import IotDeviceCoordinator
from .device import Device
from .device_features import DeviceFeatureEnum
from .device_types import DeviceTypeEnum
from .device_data_storage import (
    get_stored_data,
    safe_get_value,
    safe_set_value,
    set_stored_data,
)
from .device_enums import ModeEnum
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
        deviceFeature: DeviceFeatureEnum,
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
            case DeviceFeatureEnum.SWITCH_POWER:
                return await self.SWITCH_POWER(value=value)
            case DeviceFeatureEnum.SWITCH_HEALTHY:
                return await self.SWITCH_HEALTHY(value=value)
            case DeviceFeatureEnum.SWITCH_BEEP:
                return await self.SWITCH_BEEP(value=value)
            case DeviceFeatureEnum.SWITCH_ECO:
                return await self.SWITCH_ECO(value=value)
            case DeviceFeatureEnum.SWITCH_DRYING:
                return await self.SWITCH_DRYING(value=value)
            case DeviceFeatureEnum.SWITCH_SCREEN:
                return await self.SWITCH_SCREEN(value=value)
            case DeviceFeatureEnum.SWITCH_LIGHT_SENSE:
                return await self.SWITCH_LIGHT_SENSE(value=value)
            case DeviceFeatureEnum.SWITCH_SWING_WIND:
                return await self.SWITCH_SWING_WIND(value=value)
            case DeviceFeatureEnum.SWITCH_SLEEP:
                return await self.SWITCH_SLEEP(value=value)
            case DeviceFeatureEnum.SWITCH_AI_ECO:
                return await self.SWITCH_AI_ECO(value=value)
            case DeviceFeatureEnum.SWITCH_8_C_HEATING:
                return await self.SWITCH_8_C_HEATING(value=value)
            case DeviceFeatureEnum.SWITCH_SOFT_WIND:
                return await self.SWITCH_SOFT_WIND(value=value)
            case DeviceFeatureEnum.SWITCH_FRESH_AIR:
                return await self.SWITCH_FRESH_AIR(value=value)

    def is_allowed(self) -> bool:
        mode = self.device.mode_value_to_enum_mapp.get(self.device.data.work_mode,ModeEnum.AUTO)
        match self.deviceFeature:
            case DeviceFeatureEnum.SWITCH_DRYING:
                if (
                    mode == ModeEnum.HEAT
                    or mode == ModeEnum.AUTO
                    or mode == ModeEnum.FAN
                ):
                    return False
                if (
                    DeviceFeatureEnum.SWITCH_8_C_HEATING
                    in self.device.supported_features
                ):
                    if self.device.data.eight_add_hot == 1:
                        return False
                return True
            case DeviceFeatureEnum.SWITCH_SOFT_WIND:
                if mode != ModeEnum.COOL:
                    return False
                return True
            case DeviceFeatureEnum.SWITCH_8_C_HEATING:
                if mode == ModeEnum.HEAT:
                    return True
                else:
                    return False
            case DeviceFeatureEnum.SWITCH_SLEEP:
                if mode == ModeEnum.FAN:
                    return False
                else:
                    return True
            case DeviceFeatureEnum.SWITCH_ECO:
                if (
                    mode == ModeEnum.FAN
                    or mode == ModeEnum.DEHUMIDIFICATION
                    or mode == ModeEnum.AUTO
                ):
                    return False
                else:
                    return True
            case DeviceFeatureEnum.SWITCH_FRESH_AIR:
                if mode == ModeEnum.DEHUMIDIFICATION:
                    return False
                else:
                    return True
            case DeviceFeatureEnum.SWITCH_AI_ECO:
                if (
                    mode == ModeEnum.FAN
                    or mode == ModeEnum.DEHUMIDIFICATION
                    or mode == ModeEnum.AUTO
                ):
                    return False
                else:
                    return True
            case _:
                return True

    async def SWITCH_POWER(self, value: int):
        stored_data = await get_stored_data(self.hass, self.device.device_id)
        silent_beep_when_turn_on = safe_get_value(
            stored_data, "user_config.behavior.silent_beep_when_turn_on", False
        )
        desired_state = {"powerSwitch": value}
        if silent_beep_when_turn_on:
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

        if (DeviceFeatureEnum.INTERNAL_HAS_TURBO_PROPERTY in self.device.supported_features
            and DeviceFeatureEnum.INTERNAL_HAS_HIGHTEMPERATUREWIND_PROPERTY in self.device.supported_features
            and DeviceFeatureEnum.INTERNAL_HAS_SILENCESWITCH_PROPERTY in self.device.supported_features
        ):
            desired_state["highTemperatureWind"] = 0
            desired_state["highTemperatureWind"] = 0
            desired_state["silenceSwitch"] = 0
            desired_state["windSpeed"] = 0

        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )

    async def SWITCH_AI_ECO(self, value: int):
        desired_state = {"eightAddHot": 0, "AIECOSwitch": value}

        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )

    async def SWITCH_8_C_HEATING(self, value: int):
        desired_state = {"eightAddHot": value}

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

    async def SWITCH_SOFT_WIND(self, value: int):
        desired_state = {"softWind": value}
        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )

    async def SWITCH_FRESH_AIR(self, value: int):
        desired_state = {"newWindSwitch": value}
        if value == 1:
            desired_state["selfClean"] = 0
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
        if DeviceFeatureEnum.SWITCH_POWER in device.supported_features:
            switches.append(
                SwitchHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SWITCH_POWER,
                    type="Power",
                    name="Power Switch",
                    icon_fn=lambda device: "mdi:power-plug"
                    if device.data.power_switch == 1
                    else "mdi:power-plug-off",
                    is_on_fn=lambda device: device.data.power_switch,
                )
            )

        if DeviceFeatureEnum.SWITCH_BEEP in device.supported_features:
            switches.append(
                SwitchHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SWITCH_BEEP,
                    type="BeepMode",
                    name="Beep Mode Switch",
                    icon_fn=lambda device: "mdi:volume-high"
                    if device.data.beep_switch == 1
                    else "mdi:volume-off",
                    is_on_fn=lambda device: device.data.beep_switch,
                )
            )

        if DeviceFeatureEnum.SWITCH_ECO in device.supported_features:
            switches.append(
                DynamicSwitchHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SWITCH_ECO,
                    type="ECO",
                    name="ECO Switch",
                    icon_fn=lambda device: "mdi:leaf"
                    if device.data.eco == 1
                    else "mdi:leaf-off",
                    is_on_fn=lambda device: device.data.eco,
                )
            )

        if DeviceFeatureEnum.SWITCH_AI_ECO in device.supported_features:
            switches.append(
                DynamicSwitchHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SWITCH_AI_ECO,
                    type="aiECO",
                    name="AI ECO Switch",
                    icon_fn=lambda device: "mdi:leaf"
                    if device.data.ai_eco == 1
                    else "mdi:leaf-off",
                    is_on_fn=lambda device: device.data.ai_eco,
                )
            )

        if DeviceFeatureEnum.SWITCH_8_C_HEATING in device.supported_features:
            switches.append(
                DynamicSwitchHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SWITCH_8_C_HEATING,
                    type="8CHeating",
                    name="8 °C Heating",
                    icon_fn=lambda device: "mdi:numeric-8-circle-outline",
                    is_on_fn=lambda device: device.data.eight_add_hot,
                )
            )

        if DeviceFeatureEnum.SWITCH_HEALTHY in device.supported_features:
            switches.append(
                SwitchHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SWITCH_HEALTHY,
                    type="Healthy",
                    name="Healthy Switch",
                    icon_fn=lambda device: "mdi:heart"
                    if device.data.healthy == 1
                    else "mdi:heart-off",
                    is_on_fn=lambda device: device.data.healthy,
                )
            )

        if DeviceFeatureEnum.SWITCH_DRYING in device.supported_features:
            switches.append(
                DynamicSwitchHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SWITCH_DRYING,
                    type="Drying",
                    name="Drying Switch",
                    icon_fn=lambda device: "mdi:opacity"
                    if device.data.anti_moldew == 1
                    else "mdi:water-off-outline",
                    is_on_fn=lambda device: device.data.anti_moldew,
                )
            )

        if DeviceFeatureEnum.SWITCH_SCREEN in device.supported_features:
            switches.append(
                SwitchHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SWITCH_SCREEN,
                    type="DiplayLight",
                    name="Diplay Light Switch",
                    icon_fn=lambda device: "mdi:lightbulb-outline"
                    if device.data.screen == 1
                    else "mdi:lightbulb-off-outline",
                    is_on_fn=lambda device: device.data.screen,
                )
            )

        if DeviceFeatureEnum.SWITCH_LIGHT_SENSE in device.supported_features:
            switches.append(
                SwitchHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SWITCH_LIGHT_SENSE,
                    type="LightSense",
                    name="Light Sense",
                    icon_fn=lambda device: "mdi:theme-light-dark",
                    is_on_fn=lambda device: device.data.light_sense,
                )
            )

        if DeviceFeatureEnum.SWITCH_SWING_WIND in device.supported_features:
            switches.append(
                SwitchHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SWITCH_SWING_WIND,
                    type="SwingWind",
                    name="Up and down wind",
                    icon_fn=lambda device: "mdi:swap-vertical",
                    is_on_fn=lambda device: device.data.swing_wind,
                )
            )

        if DeviceFeatureEnum.SWITCH_SLEEP in device.supported_features:
            switches.append(
                DynamicSwitchHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SWITCH_SLEEP,
                    type="Sleep",
                    name="Sleep",
                    icon_fn=lambda device: "mdi:sleep",
                    is_on_fn=lambda device: device.data.sleep,
                )
            )

        if DeviceFeatureEnum.SWITCH_SOFT_WIND in device.supported_features:
            switches.append(
                DynamicSwitchHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SWITCH_SOFT_WIND,
                    type="SoftWind",
                    name="Soft Wind",
                    icon_fn=lambda device: "mdi:weather-dust",
                    is_on_fn=lambda device: device.data.soft_wind,
                )
            )

        if DeviceFeatureEnum.SWITCH_FRESH_AIR in device.supported_features:
            switches.append(
                DynamicSwitchHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SWITCH_FRESH_AIR,
                    type="FreshAir",
                    name="Fresh Air",
                    icon_fn=lambda device: "mdi:window-open-variant"
                    if device.data.new_wind_switch == 1
                    else "mdi:window-closed-variant",
                    is_on_fn=lambda device: device.data.new_wind_switch,
                )
            )

        if (DeviceFeatureEnum.USER_CONFIG_BEHAVIOR_MEMORIZE_TEMP_BY_MODE in device.supported_features):
            switches.append(
                ConfigSwitchHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    config_path="user_config.behavior.memorize_temp_by_mode",
                    name="Save temp by mode",
                )
            )

        if (DeviceFeatureEnum.USER_CONFIG_BEHAVIOR_MEMORIZE_FAN_SPEED_BY_MODE in device.supported_features):
            switches.append(
                ConfigSwitchHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    config_path="user_config.behavior.memorize_fan_speed_by_mode",
                    name="Save fan speed by mode",
                )
            )

        if (DeviceFeatureEnum.USER_CONFIG_BEHAVIOR_SILENT_BEEP_WHEN_TURN_ON in device.supported_features):
            switches.append(
                ConfigSwitchHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    config_path="user_config.behavior.silent_beep_when_turn_on",
                    name="Silent beep when turn on",
                )
            )

        if (DeviceFeatureEnum.USER_CONFIG_BEHAVIOR_MEMORIZE_HUMIDITY_BY_MODE in device.supported_features):
            switches.append(
                ConfigSwitchHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    config_path="user_config.behavior.memorize_humidity_by_mode",
                    name="Save humidity by mode",
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
        deviceFeature: DeviceFeatureEnum,
        icon_fn: lambda device: str,
        is_on_fn: lambda device: bool | None,
    ) -> None:
        TclEntityBase.__init__(self, coordinator, type, name, device)
        self.icon_fn = icon_fn
        self.is_on_fn = is_on_fn
        self.iot_handler = DesiredStateHandlerForSwitch(
            hass=hass,
            coordinator=coordinator,
            deviceFeature=deviceFeature,
            device=self.device,
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


class ConfigSwitchHandler(TclEntityBase, SwitchEntity):
    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: IotDeviceCoordinator,
        device: Device,
        name: str,
        config_path: str,
    ) -> None:
        TclEntityBase.__init__(self, coordinator, config_path, name, device)
        self.hass = hass
        self.config_path = config_path
        self._attr_entity_category = EntityCategory.CONFIG

    @property
    def device_class(self) -> str:
        return SwitchDeviceClass.SWITCH

    @property
    def icon(self):
        return "mdi:cog"

    @property
    def is_on(self) -> bool | None:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        return safe_get_value(self.device.storage, self.config_path, False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)

        storage_data, need_save = safe_set_value(
            self.device.storage, self.config_path, True, overwrite_if_exists=True
        )

        if need_save:
            await set_stored_data(self.hass, self.device.device_id, storage_data)
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)

        storage_data, need_save = safe_set_value(
            self.device.storage, self.config_path, False, overwrite_if_exists=True
        )

        if need_save:
            await set_stored_data(self.hass, self.device.device_id, storage_data)
        await self.coordinator.async_refresh()


class DynamicSwitchHandler(SwitchHandler, SwitchEntity):
    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: IotDeviceCoordinator,
        device: Device,
        type: str,
        name: str,
        deviceFeature: DeviceFeatureEnum,
        icon_fn: lambda device: str,
        is_on_fn: lambda device: bool | None,
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

    @property
    def available(self) -> bool:
        if self.device.is_online:            
            self.device = self.coordinator.get_device_by_id(self.device.device_id)
            self.iot_handler.refreshDevice(self.device)
            return self.iot_handler.is_allowed()
        return False
