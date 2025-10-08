"""Switch setup for our Integration."""

import logging
from typing import Any

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .config_entry import New_NameConfigEntry
from .coordinator import IotDeviceCoordinator
from .device import Device, Device, DeviceTypeEnum
from .device_features import DeviceFeatureEnum
from .tcl_entity_base import TclEntityBase, TclNonPollingEntityBase
from .self_diagnostics import SelfDiagnostics
from .data_storage import safe_set_value, set_stored_data, get_stored_data,safe_get_value

_LOGGER = logging.getLogger(__name__)


class DesiredStateHandlerForButton:
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

    async def call_button(self, value: int) -> str:
        match self.deviceFeature:
            case DeviceFeatureEnum.BUTTON_SELF_CLEAN:
                return await self.BUTTON_SELF_CLEAN(value=value)

    async def BUTTON_SELF_CLEAN(self, value: int):
        desired_state = {}
        if value == 1:
            desired_state = {"powerSwitch": 0, "selfClean": 1}
        else:
            desired_state = {"selfClean": 0}
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

    buttons = []
    for device in config_entry.devices:
        buttons.append(
            NotImplementedDevice_Clear_ManualStateDump_Button(
                hass, coordinator, device, False
            )
        )
        buttons.append(Reload_Button(coordinator, device))
        buttons.append(Reset_Has_Power_Consumption_Button(hass,coordinator, device,False))
        buttons.append(Reset_Has_Work_Time_Button(hass,coordinator, device,False))        

        if DeviceFeatureEnum.BUTTON_SELF_CLEAN in device.supported_features:
            buttons.append(
                ButtonHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    type="SelfCleanButton",
                    name="Evaporator Clean",
                    name_fn=lambda device: "Stop Evaporator Cleaning"
                    if device.data.self_clean == 1
                    else "Start Evaporator Cleaning",
                    deviceFeature=DeviceFeatureEnum.BUTTON_SELF_CLEAN,
                    icon_fn=lambda device: "mdi:cancel"
                    if device.data.self_clean == 1
                    else "mdi:broom",
                    value_fn=lambda device: device.data.self_clean,
                )
            )

    for device in config_entry.non_implemented_devices:
        buttons.append(
            NotImplementedDevice_Clear_ManualStateDump_Button(
                hass, coordinator, device, True
            )
        )

    async_add_entities(buttons)


class ButtonHandler(TclEntityBase, ButtonEntity):
    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: IotDeviceCoordinator,
        device: Device,
        type: str,
        name: str,
        deviceFeature: DeviceFeatureEnum,
        icon_fn: lambda device: str,
        name_fn: lambda device: str,
        value_fn: lambda device: int,
    ) -> None:
        TclEntityBase.__init__(self, coordinator, type, name, device)
        self.name_fn = name_fn
        self.icon_fn = icon_fn
        self.value_fn = value_fn
        self.iot_handler = DesiredStateHandlerForButton(
            hass=hass,
            coordinator=coordinator,
            deviceFeature=deviceFeature,
            device=self.device,
        )

    @property
    def name(self) -> str:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        self.iot_handler.refreshDevice(self.device)

        return self.name_fn(self.device)

    @property
    def device_class(self) -> str:
        return ButtonDeviceClass.UPDATE

    @property
    def icon(self):
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        self.iot_handler.refreshDevice(self.device)

        return self.icon_fn(self.device)

    async def async_press(self) -> None:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        self.iot_handler.refreshDevice(self.device)

        if self.value_fn(self.device) == 1:
            await self.iot_handler.call_button(0)
        else:
            await self.iot_handler.call_button(1)
        await self.coordinator.async_refresh()


class Reload_Button(TclNonPollingEntityBase, ButtonEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        TclNonPollingEntityBase.__init__(
            self, "ForceReladDevice", "Sync with TCL Home", device
        )
        self.coordinator = coordinator
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def device_class(self) -> str:
        return ButtonDeviceClass.RESTART

    @property
    def icon(self):
        return "mdi:cloud-sync"

    async def async_press(self) -> None:        
        power_consumption_data_enabled= safe_get_value(self.device.storage, "non_user_config.power_consumption.enabled", False)
        work_time_data_enabled= safe_get_value(self.device.storage, "non_user_config.work_time.enabled", False)        
        if power_consumption_data_enabled or work_time_data_enabled:        
            device_id=self.device.device_id
            storage_data=await get_stored_data(self.hass, device_id)        
            storage_data, need_save= safe_set_value(storage_data, "non_user_config.power_consumption.last_response.timestamp", 1759400000, True)            
            storage_data, need_save= safe_set_value(storage_data, "non_user_config.work_time.last_response.timestamp", 1759400000, True)          
            if need_save:
                self.device.storage= await set_stored_data(self.hass, device_id, storage_data)
        await self.coordinator.async_refresh()


class NotImplementedDevice_Clear_ManualStateDump_Button(
    TclNonPollingEntityBase, ButtonEntity
):
    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: IotDeviceCoordinator,
        device: Device,
        enabled: bool = True,
    ) -> None:
        TclNonPollingEntityBase.__init__(
            self,
            "ClearManualStateDump",
            "Clear Manual State Dump Storage",
            device,
        )
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self.selfDiagnostics = SelfDiagnostics(hass=hass, device_id=device.device_id)
        self._attr_entity_registry_enabled_default = enabled

    @property
    def device_class(self) -> str:
        return ButtonDeviceClass.RESTART

    @property
    def icon(self):
        return "mdi:delete"

    async def async_press(self) -> None:
        await self.selfDiagnostics.clearStorage()

class Reset_Has_Power_Consumption_Button(TclNonPollingEntityBase, ButtonEntity):
    def __init__(self,
        hass: HomeAssistant, 
        coordinator: IotDeviceCoordinator, 
        device: Device,
        enabled: bool = False) -> None:
        TclNonPollingEntityBase.__init__(
            self, "ForceResetHasPowerConsumption", "Try get Power Consumption Data", device
        )
        self.hass=hass
        self.coordinator = coordinator
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_entity_registry_enabled_default = enabled

    @property
    def device_class(self) -> str:
        return ButtonDeviceClass.RESTART

    @property
    def icon(self):
        return "mdi:transmission-tower-export"

    async def async_press(self) -> None:        
        storage_data=await get_stored_data(self.hass, self.device.device_id)        
        storage_data, need_save= safe_set_value(storage_data, "non_user_config.power_consumption.init_done", False, True)      
        storage_data, need_save= safe_set_value(storage_data, "non_user_config.power_consumption.enabled", True, True)            
        if need_save:
            await set_stored_data(self.hass, self.device.device_id, storage_data)
            await self.coordinator.async_refresh()

class Reset_Has_Work_Time_Button(TclNonPollingEntityBase, ButtonEntity):
    def __init__(self,
        hass: HomeAssistant, 
        coordinator: IotDeviceCoordinator, 
        device: Device,
        enabled: bool = False) -> None:
        TclNonPollingEntityBase.__init__(
            self, "ForceResetHasWorkTime", "Try get Work time Data", device
        )
        self.hass=hass
        self.coordinator = coordinator
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_entity_registry_enabled_default = enabled

    @property
    def device_class(self) -> str:
        return ButtonDeviceClass.RESTART

    @property
    def icon(self):
        return "mdi:clock-time-eight-outline"

    async def async_press(self) -> None:
        storage_data=await get_stored_data(self.hass, self.device.device_id)                
        storage_data, need_save= safe_set_value(storage_data, "non_user_config.work_time.init_done", False, True)            
        storage_data, need_save= safe_set_value(storage_data, "non_user_config.work_time.enabled", True, True)            
        if need_save:  
            await set_stored_data(self.hass, self.device.device_id, storage_data)
            await self.coordinator.async_refresh()