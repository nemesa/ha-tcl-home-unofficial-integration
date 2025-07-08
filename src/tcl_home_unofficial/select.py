"""Switch setup for our Integration."""

import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .aws_iot import AwsIot
from .config_entry import New_NameConfigEntry
from .coordinator import IotDeviceCoordinator
from .device import (
    Device,
    TCL_SplitAC_DeviceData_Helper,
    ModeEnum,
    WindSeedEnum,
    UpAndDownAirSupplyVectorEnum,
    LeftAndRightAirSupplyVectorEnum,
    SleepModeEnum,
)
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
        switches.append(ModeSelect(coordinator, device))
        switches.append(WindSpeedSelect(coordinator, device))
        switches.append(UpAndDownAirSupplyVectorSelect(coordinator, device))
        switches.append(LeftAndRightAirSupplyVectorSelect(coordinator, device))
        switches.append(SleepModeSelect(coordinator, device))

    async_add_entities(switches)


class ModeSelect(TclEntityBase, SelectEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        TclEntityBase.__init__(self, coordinator, "ModeSelect", "Set Mode", device)

        helper = TCL_SplitAC_DeviceData_Helper(device.data)
        self.aws_iot = coordinator.get_aws_iot()
        self._attr_current_option = helper.getMode()
        self._attr_options = [e.value for e in ModeEnum]

    @property
    def icon(self):
        return "mdi:set-none"

    async def async_select_option(self, option: str) -> None:
        await self.aws_iot.async_set_mode(self.device.device_id, option)
        self._attr_current_option = option
        self.async_write_ha_state()
        await self.coordinator.async_refresh()


class WindSpeedSelect(TclEntityBase, SelectEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        TclEntityBase.__init__(
            self, coordinator, "WindSpeedSelect", "Wind Speed", device
        )

        self.aws_iot = coordinator.get_aws_iot()
        helper = TCL_SplitAC_DeviceData_Helper(device.data)
        self._attr_current_option = helper.getWindSpeed()
        self._attr_options = [e.value for e in WindSeedEnum]

    @property
    def icon(self):
        return "mdi:weather-windy"

    async def async_select_option(self, option: str) -> None:
        await self.aws_iot.async_set_wind_speed(self.device.device_id, option)
        self._attr_current_option = option
        self.async_write_ha_state()
        await self.coordinator.async_refresh()


class UpAndDownAirSupplyVectorSelect(TclEntityBase, SelectEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        TclEntityBase.__init__(
            self,
            coordinator,
            "UpAndDownAirSupplyVectorSelect",
            "Up and down air supply",
            device,
        )

        self.aws_iot = coordinator.get_aws_iot()
        helper = TCL_SplitAC_DeviceData_Helper(device.data)
        self._attr_current_option = helper.getUpAndDownAirSupplyVector()
        self._attr_options = [e.value for e in UpAndDownAirSupplyVectorEnum]

    @property
    def icon(self):
        return "mdi:swap-vertical"

    async def async_select_option(self, option: str) -> None:
        await self.aws_iot.async_set_up_and_down_air_supply_vector(
            self.device.device_id, option
        )
        self._attr_current_option = option
        self.async_write_ha_state()
        await self.coordinator.async_refresh()


class LeftAndRightAirSupplyVectorSelect(TclEntityBase, SelectEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        TclEntityBase.__init__(
            self,
            coordinator,
            "LeftAndRightAirSupplyVectorSelect",
            "Left and right air supply",
            device,
        )

        self.aws_iot = coordinator.get_aws_iot()
        helper = TCL_SplitAC_DeviceData_Helper(device.data)
        self._attr_current_option = helper.getLeftAndRightAirSupplyVector()
        self._attr_options = [e.value for e in LeftAndRightAirSupplyVectorEnum]

    @property
    def icon(self):
        return "mdi:swap-horizontal"

    async def async_select_option(self, option: str) -> None:
        await self.aws_iot.async_set_left_and_right_air_supply_vector(
            self.device.device_id, option
        )
        self._attr_current_option = option
        self.async_write_ha_state()
        await self.coordinator.async_refresh()


class SleepModeSelect(TclEntityBase, SelectEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        TclEntityBase.__init__(
            self, coordinator, "SleepModeSelect", "Sleep Mode", device
        )

        self.aws_iot = coordinator.get_aws_iot()
        helper = TCL_SplitAC_DeviceData_Helper(device.data)
        self._attr_current_option = helper.getSleepMode()
        self._attr_options = [e.value for e in SleepModeEnum]

    @property
    def icon(self):
        return "mdi:sleep"

    async def async_select_option(self, option: str) -> None:
        await self.aws_iot.async_set_sleep_mode(self.device.device_id, option)
        self._attr_current_option = option
        self.async_write_ha_state()
        await self.coordinator.async_refresh()
