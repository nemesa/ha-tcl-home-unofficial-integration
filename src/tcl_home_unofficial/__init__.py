"""The TCL Home - Unofficial integration."""

from __future__ import annotations

import logging

# from homeassistant.const import Platform
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .aws_iot import AwsIot
from .config_entry import New_NameConfigEntry
from .device import Device
from .session_manager import SessionManager

_PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR, Platform.SWITCH]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config_entry: New_NameConfigEntry
) -> bool:
    """Set up TCL Home - Unofficial from a config entry."""

    config_entry.devices = []

    sessionManager: SessionManager = SessionManager(
        hass=hass, config_entry=config_entry
    )
    await sessionManager.async_load()

    things = await sessionManager.async_get_things_not_stored()
    awsCred = await sessionManager.async_aws_credentials()

    config_entry.aws_iot = AwsIot(
        region_name=config_entry.data["aws_region"],
        access_key_id=awsCred.Credentials.access_key_id,
        secret_access_key=awsCred.Credentials.secret_key,
        session_token=awsCred.Credentials.session_token,
    )

    for device in things.data:
        aws_thing = await hass.async_add_executor_job(
            config_entry.aws_iot.getThing, device.device_id
        )

        beep_switch_state = int(aws_thing["state"]["reported"]["beepSwitch"])
        power_state = int(aws_thing["state"]["reported"]["powerSwitch"])
        target_temperature = int(aws_thing["state"]["reported"]["targetTemperature"])

        config_entry.devices.append(
            Device(
                device_id=device.device_id,
                device_type=device.device_name,
                name=device.nick_name,
                firmware_version=device.firmware_version,
                power_state=power_state,
                beep_switch_state=beep_switch_state,
                target_temperature=target_temperature,
            )
        )

    await hass.config_entries.async_forward_entry_setups(config_entry, _PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: New_NameConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("init.async_unload_entry %s", entry)
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
