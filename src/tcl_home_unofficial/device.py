"""."""

from dataclasses import dataclass

from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN


@dataclass
class Device:
    """Device."""

    device_id: int
    device_type: str
    name: str
    firmware_version: str
    power_state: int | bool
    beep_switch_state: int | bool
    target_temperature: int


def toDeviceInfo(device: Device) -> DeviceInfo:
    """Convert Device to DeviceInfo."""
    return DeviceInfo(
        name=f"{device.name} ({device.device_id})",
        manufacturer="TCL",
        model=device.device_type,
        sw_version=device.firmware_version,
        identifiers={
            (
                DOMAIN,
                f"TCL-{device.device_id}",
            )
        },
    )
