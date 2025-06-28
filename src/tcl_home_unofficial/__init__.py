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
from .tcl import get_aws_credentials, get_sub_from_jwt_token, get_things

_PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR, Platform.SWITCH]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config_entry: New_NameConfigEntry
) -> bool:
    """Set up TCL Home - Unofficial from a config entry."""
    # _LOGGER.info("init.async_setup_entry %s", entry.data)

    config_entry.devices = []

    sessionManager: SessionManager = SessionManager(
        hass=hass, config_entry=config_entry
    )
    await sessionManager.async_load()

    authResult = await sessionManager.async_get_auth_data()

    refreshTokensResult = await sessionManager.async_refresh_tokens()

    saas_token = refreshTokensResult.data.saas_token

    things = await get_things(saas_token, authResult.user.country_abbr)

    identity_pool_id = get_sub_from_jwt_token(refreshTokensResult.data.cognito_token)

    _LOGGER.info("identity_pool_id: %s", identity_pool_id)

    awsCred = await get_aws_credentials(
        identity_pool_id, refreshTokensResult.data.cognito_token
    )

    config_entry.aws_iot = AwsIot(
        region_name=config_entry.data["aws_region"],
        access_key_id=awsCred["Credentials"]["AccessKeyId"],
        secret_access_key=awsCred["Credentials"]["SecretKey"],
        session_token=awsCred["Credentials"]["SessionToken"],
    )

    ##devices = []

    for device in things["data"]:
        aws_thing = await hass.async_add_executor_job(
            config_entry.aws_iot.getThing, device["deviceId"]
        )

        # _LOGGER.info("aws_thing_type: %s", type(aws_thing))
        # _LOGGER.info("aws_thing: %s", aws_thing["state"]["reported"])

        beep_switch_state = int(aws_thing["state"]["reported"]["beepSwitch"])
        power_state = int(aws_thing["state"]["reported"]["powerSwitch"])
        target_temperature = int(aws_thing["state"]["reported"]["targetTemperature"])

        config_entry.devices.append(
            Device(
                device_id=device["deviceId"],
                device_type=device["deviceName"],
                name=device["nickName"],
                firmware_version=device["firmwareVersion"],
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
