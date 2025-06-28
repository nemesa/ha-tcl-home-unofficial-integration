"""."""

from datetime import timedelta  # noqa: I001
import logging
from typing import Any

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .aws_iot import AwsIot
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN
from .device import Device

_LOGGER = logging.getLogger(__name__)


@dataclass
class IotDeviceCoordinatorData:
    devices: list[Device]


class IotDeviceCoordinator(DataUpdateCoordinator):
    """."""

    data: IotDeviceCoordinatorData

    def __init__(
        self, hass: HomeAssistant, config_entry: ConfigEntry, aws_iot: AwsIot
    ) -> None:
        """Initialize coordinator."""

        self.aws_iot = aws_iot
        # set variables from options.  You need a default here incase options have not been set
        self.poll_interval = config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        # Initialise DataUpdateCoordinator
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} ({config_entry.unique_id})",
            # Method to call on every update interval.
            update_method=self.async_update_data,
            # Polling interval. Will only be polled if there are subscribers.
            # Using config option here but you can just use a value.
            update_interval=timedelta(seconds=self.poll_interval),
        )

    async def async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        _LOGGER.info("coordinator.async_update_data")

        devices = []
        try:
            for device in self.config_entry.devices:
                _LOGGER.info("coordinator.async_update_data: %s", device)
                aws_thing = await self.aws_iot.async_getThing(device.device_id)
                d = Device(
                    device_id=device.device_id,
                    device_type=device.device_type,
                    name=device.name,
                    firmware_version=device.firmware_version,
                    aws_thing=aws_thing,
                )
                devices.append(d)
        except Exception as err:
            # This will show entities as unavailable by raising UpdateFailed exception
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        return IotDeviceCoordinatorData(devices)

    def get_device_by_id(self, device_id: str) -> Device | None:
        """Return device by device id."""
        # Called by the binary sensors and sensors to get their updated data from self.data
        try:
            found = [
                device for device in self.data.devices if device.device_id == device_id
            ][0]
            _LOGGER.info("coordinator.get_device_by_id: %s", found)
            return found
        except IndexError:
            return None

    def set_device(self, device: Device) -> None:
        """Set device in coordinator data."""
        # Called by the switch to set the device state
        for i, d in enumerate(self.data.devices):
            if d.device_id == device.device_id:
                self.data.devices[i] = device
                break
        else:
            self.data.devices.append(device)
