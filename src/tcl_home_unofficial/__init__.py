"""The TCL Home - Unofficial integration."""

from __future__ import annotations

import logging

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .aws_iot import AwsIot
from .config_entry import New_NameConfigEntry, RuntimeData
from .coordinator import IotDeviceCoordinator
from .device import Device

_PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.SELECT,
    Platform.NUMBER,
    Platform.BUTTON,
]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config_entry: New_NameConfigEntry
) -> bool:
    """Set up TCL Home - Unofficial from a config entry."""

    config_entry.devices = []

    aws_iot = AwsIot(
        hass=hass,
        config_entry=config_entry,
    )
    await aws_iot.async_init()

    things = await aws_iot.get_all_things()

    for thing in things.data:
        aws_thing = await aws_iot.async_get_thing(thing.device_id)

        config_entry.devices.append(
            Device(
                device_id=thing.device_id,
                device_type=thing.device_name,
                name=thing.nick_name,
                firmware_version=thing.firmware_version,
                aws_thing=aws_thing,
            )
        )

    coordinator = IotDeviceCoordinator(hass, config_entry, aws_iot)
    await coordinator.async_config_entry_first_refresh()
    config_entry.runtime_data = RuntimeData(coordinator)

    await hass.config_entries.async_forward_entry_setups(config_entry, _PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: New_NameConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
