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
    getModeFromDeviceData,
    ModeEnum,
    WindSeedEnum,
    getWindSpeedFromDeviceData,
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

    aws_iot = AwsIot(
        hass=hass,
        config_entry=config_entry,
    )
    await aws_iot.async_init()

    switches = []
    for device in config_entry.devices:
        switches.append(ModeSelect(coordinator, device, aws_iot))
        switches.append(WindSpeedSelect(coordinator, device, aws_iot))

    async_add_entities(switches)


class ModeSelect(TclEntityBase, SelectEntity):
    def __init__(
        self, coordinator: IotDeviceCoordinator, device: Device, aws_iot: AwsIot
    ) -> None:
        TclEntityBase.__init__(self, coordinator, "ModeSelect", "Set Mode", device)

        self.aws_iot = aws_iot
        self._attr_current_option = getModeFromDeviceData(device.data)
        self._attr_options = [e.value for e in ModeEnum]

    # @property
    # def device_class(self) -> str:
    #     return SwitchDeviceClass.SWITCH

    @property
    def icon(self):
        return "mdi:set-none"

    async def async_select_option(self, option: str) -> None:
        await self.aws_iot.async_set_mode(self.device.device_id, option)
        self._attr_current_option = option
        self.async_write_ha_state()
        await self.coordinator.async_refresh()


class WindSpeedSelect(TclEntityBase, SelectEntity):
    def __init__(
        self, coordinator: IotDeviceCoordinator, device: Device, aws_iot: AwsIot
    ) -> None:
        TclEntityBase.__init__(
            self, coordinator, "WindSpeedSelect", "Wind Speed", device
        )

        self.aws_iot = aws_iot
        self._attr_current_option = getWindSpeedFromDeviceData(device.data)
        self._attr_options = [e.value for e in WindSeedEnum]

    @property
    def icon(self):
        return "mdi:weather-windy"

    async def async_select_option(self, option: str) -> None:
        await self.aws_iot.async_set_wind_speed(self.device.device_id, option)
        self._attr_current_option = option
        self.async_write_ha_state()
        await self.coordinator.async_refresh()
