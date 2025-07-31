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

    aws_iot_init_success = False
    aws_iot_init_error = None

    try:
        await aws_iot.async_init()
        aws_iot_init_success = True
    except Exception as e:
        aws_iot_init_error = {"error": str(e)}

    tcl_thing = []
    try:
        all_things_response = await aws_iot.get_all_things()
        for thing in all_things_response.data:
            if thing.device_id == device_id:
                tcl_thing.append(
                    {
                        "device_id": thing.device_id,
                        "platform": thing.platform,
                        "nick_name": thing.nick_name,
                        "device_name": thing.device_name,
                        "category": thing.category,
                        "type": thing.type,
                        "device_type": thing.device_type,
                        "firmware_version": thing.firmware_version,
                        "net_type": thing.net_type,
                        "is_online": thing.is_online,
                    }
                )
    except Exception as e:
        tcl_thing = {"error": str(e)}

    aws_thing = None
    try:
        aws_thing = await aws_iot.async_get_thing(device_id)
    except Exception as e:
        aws_thing = {"error": str(e)}

    self_diagnostics = SelfDiagnostics(hass=hass, device_id=device_id)
    manual_state_dump_data = await self_diagnostics.get_stored_data()

    return {
        "device": {
            "model": device.model,
            "sw_version": device.sw_version,
        },
        "aws_iot_init_success": aws_iot_init_success,
        "aws_iot_init_error": aws_iot_init_error,
        "tcl_thing": tcl_thing,
        "aws_thing": aws_thing,
        "manual_state_dump_data": manual_state_dump_data,
    }
