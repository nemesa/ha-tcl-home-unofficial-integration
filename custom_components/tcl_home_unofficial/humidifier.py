"""."""

import logging

from typing import Any

from homeassistant.components.humidifier import (
    HumidifierAction,
    HumidifierDeviceClass,
    HumidifierEntity,
    HumidifierEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .config_entry import New_NameConfigEntry
from .coordinator import IotDeviceCoordinator
from .device import Device
from .device_features import DeviceFeatureEnum
from .device_enums import DehumidifierModeEnum
from .tcl_entity_base import TclEntityBase
from .number import DesiredStateHandlerForNumber
from .switch import DesiredStateHandlerForSwitch
from .select import DesiredStateHandlerForSelect

_LOGGER = logging.getLogger(__name__)


def get_current_mode_fn(device: Device) -> str:    
    return device.mode_value_to_enum_mapp.get(device.data.work_mode, DehumidifierModeEnum.DRY)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: New_NameConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Binary Sensors."""
    coordinator = config_entry.runtime_data.coordinator

    humidifiers = []
    for device in config_entry.devices:
        if DeviceFeatureEnum.HUMIDIFIER in device.supported_features:
            humidifiers.append(
                DeHumidifierHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    type="DeHumidifierControll",
                    name="Dehumidifier",
                    mode_select_feature=DeviceFeatureEnum.SELECT_MODE,
                    power_switch_feature=DeviceFeatureEnum.SWITCH_POWER,
                    humidity_set_feature=DeviceFeatureEnum.NUMBER_DEHUMIDIFIER_HUMIDITY,
                    is_on_fn=lambda device: device.data.power_switch==1,
                    current_mode_fn= lambda device: get_current_mode_fn(device),
                    current_humidity_fn=lambda device: device.data.env_humidity,
                    target_humidity_fn=lambda device: device.data.humidity,
                    options_mode=[map_mode_to_humidifier_mode(e) for e in device.get_supported_modes()],
                )
            )

    async_add_entities(humidifiers)

def map_mode_to_humidifier_mode(mode: DehumidifierModeEnum) -> str:
    
    """
MODE_NORMAL = "normal"
MODE_ECO = "eco"
MODE_AWAY = "away"
MODE_BOOST = "boost"
MODE_COMFORT = "comfort"
MODE_HOME = "home"
MODE_SLEEP = "sleep"
MODE_AUTO = "auto"
MODE_BABY = "baby"

    """
    match mode:
        case DehumidifierModeEnum.DRY:
            return "normal"
        case DehumidifierModeEnum.TURBO:
            return "boost"
        case DehumidifierModeEnum.COMFORT:
            return "comfort"
        case DehumidifierModeEnum.CONTINUE:
            return "home"
        case _:
            return "normal"


def map_humidifier_mode_to_tcl_mode(mode: str) -> DehumidifierModeEnum:
    match mode:
        case "normal":
            return DehumidifierModeEnum.DRY
        case "boost":
            return DehumidifierModeEnum.TURBO
        case "comfort":
            return DehumidifierModeEnum.COMFORT
        case "home":
            return DehumidifierModeEnum.CONTINUE
        case _:
            return DehumidifierModeEnum.DRY
    
    
class DeHumidifierHandler(TclEntityBase, HumidifierEntity):
    _attr_should_poll = False

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: IotDeviceCoordinator,
        device: Device,      
        type: str,  
        name: str,     
        mode_select_feature: str,
        power_switch_feature:str,
        humidity_set_feature:str,   
        is_on_fn=lambda device: bool | float,  
        current_humidity_fn=lambda device: bool | float,  
        current_mode_fn=lambda device: str,
        target_humidity_fn=lambda device: bool | float,  
        options_mode=list[str],              
    ) -> None:
        TclEntityBase.__init__(self, coordinator, type, name, device)
        self.is_on_fn=is_on_fn        
        self.current_humidity_fn=current_humidity_fn
        self.target_humidity_fn=target_humidity_fn
        self.current_mode_fn=current_mode_fn


        self.iot_handler_power = DesiredStateHandlerForSwitch(
            hass=hass,
            coordinator=coordinator,
            device=device,
            deviceFeature=power_switch_feature,
        )

        self.iot_handler_humidity = DesiredStateHandlerForNumber(
            hass=hass,
            coordinator=coordinator,
            device=device,
            deviceFeature=humidity_set_feature,
        )

        self.iot_handler_mode = DesiredStateHandlerForSelect(
            hass=hass,
            coordinator=coordinator,
            device=device,
            deviceFeature=mode_select_feature,
        )

        
        self._attr_is_on = self.is_on_fn(device)
        self._attr_action = HumidifierAction.DRYING,
        self._attr_supported_features = HumidifierEntityFeature(0)

        if options_mode != None and len(options_mode) > 0:
            self._attr_supported_features |= HumidifierEntityFeature.MODES            
            self._attr_available_modes = options_mode
        
        
        self._attr_mode = map_mode_to_humidifier_mode(self.current_mode_fn(device))
        self._attr_target_humidity =self.target_humidity_fn(device)
        self._attr_current_humidity = self.current_humidity_fn(device)        
        self._attr_device_class = HumidifierDeviceClass.DEHUMIDIFIER

    def refresh_device(self) -> None:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        self.iot_handler_power.refreshDevice(self.device)
        self.iot_handler_humidity.refreshDevice(self.device)
        self.iot_handler_mode.refreshDevice(self.device)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.iot_handler_power.call_switch(1)
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.iot_handler_power.call_switch(0)
        await self.coordinator.async_refresh()

    async def async_set_humidity(self, humidity: int) -> None:
        self.refresh_device()
        await self.iot_handler_humidity.call_set_number(humidity)
        await self.iot_handler_humidity.store_humidity(humidity)
        await self.coordinator.async_refresh()
        self.async_write_ha_state()

    async def async_set_mode(self, mode: str) -> None:
        self.refresh_device()
        await self.iot_handler_mode.call_select_option(
                map_humidifier_mode_to_tcl_mode(mode)
            )
        await self.coordinator.async_refresh()
