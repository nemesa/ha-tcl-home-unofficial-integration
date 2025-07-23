"""Diagnostics for tcl_home_unofficial integration."""

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry

from .aws_iot import AwsIot
from .config_entry import New_NameConfigEntry
from .self_diagnostics import SelfDiagnostics


async def async_get_device_diagnostics(
    hass: HomeAssistant, entry: New_NameConfigEntry, device: DeviceEntry
) -> dict[str, Any]:
    """Return diagnostics for a device."""

    device_id = next(
        identifier[1]
        for identifier in device.identifiers
        if identifier[0] == "tcl_home_unofficial"
    ).split("-")[1]

    aws_iot = AwsIot(
        hass=hass,
        config_entry=entry,
    )
    await aws_iot.async_init()
    aws_thing = await aws_iot.async_get_thing(device_id)

    self_diagnostics = SelfDiagnostics(hass=hass, device_id=device_id)
    manual_state_dump_data = await self_diagnostics.get_stored_data()

    return {
        "device": {
            "model": device.model,
            "sw_version": device.sw_version,
        },
        "aws_thing": aws_thing,
        "manual_state_dump_data": manual_state_dump_data,
    }
