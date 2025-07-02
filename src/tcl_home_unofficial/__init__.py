"""The TCL Home - Unofficial integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .aws_iot import AwsIot
from .config_entry import (
    New_NameConfigEntry,
    RuntimeData,
    convertToConfigData,
    sanitizeConfigData,
)
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
    configData = convertToConfigData(config_entry)

    if configData.verbose_setup_logging:
        _LOGGER.info(
            "Setup.async_setup_entry %s",
            sanitizeConfigData(configData),
        )

    config_entry.devices = []

    aws_iot = AwsIot(
        hass=hass,
        config_entry=config_entry,
    )
    await aws_iot.async_init()

    if configData.verbose_setup_logging:
        _LOGGER.info("Setup.async_setup_entry clear session storage")
    await aws_iot.get_session_manager().clear_storage()

    things = await aws_iot.get_all_things()

    for thing in things.data:
        aws_thing = await aws_iot.async_get_thing(thing.device_id)

        device = Device(
            device_id=thing.device_id,
            device_type=thing.device_name,
            name=thing.nick_name,
            firmware_version=thing.firmware_version,
            aws_thing=aws_thing,
        )

        if configData.verbose_setup_logging:
            _LOGGER.info("Setup.async_setup_entry found device:%s", device)

        if device.is_implemented_by_integration:
            config_entry.devices.append(device)
        else:
            _LOGGER.warning(
                "Setup.async_setup_entry device is not implemented by this integration: %s",
                device,
            )

    # Initialise a listener for config flow options changes.
    cancel_update_listener = config_entry.async_on_unload(
        config_entry.add_update_listener(_async_update_listener)
    )

    coordinator = IotDeviceCoordinator(hass, config_entry, aws_iot)
    await coordinator.async_config_entry_first_refresh()
    config_entry.runtime_data = RuntimeData(coordinator, cancel_update_listener)

    await hass.config_entries.async_forward_entry_setups(config_entry, _PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: New_NameConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)


async def _async_update_listener(hass: HomeAssistant, config_entry: ConfigEntry):
    """Handle config options update.

    Reload the integration when the options change.
    Called from our listener created above.
    """
    configData = convertToConfigData(config_entry)

    if configData.verbose_setup_logging:
        _LOGGER.info(
            "Setup._async_update_listener %s",
            sanitizeConfigData(configData),
        )
    await hass.config_entries.async_reload(config_entry.entry_id)
