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
from .data_storage import get_stored_data
from .config_entry import ConfigData

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

        self.hass = hass
        self.aws_iot = aws_iot
        self.poll_interval = config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} ({config_entry.unique_id})",
            update_method=self.async_update_data,
            update_interval=timedelta(seconds=self.poll_interval),
        )

    def get_aws_iot(self) -> AwsIot:
        """Return the AwsIot instance."""
        return self.aws_iot

    def get_config_data(self) -> AwsIot:
        """Return the AwsIot instance."""
        return self.aws_iot.get_session_manager().get_config_data()

    async def async_update_data(self):
        """Fetch data"""

        devices = []
        try:
            tcl_things = await self.aws_iot.get_all_things()
            for tcl_thing in tcl_things.data:
                aws_thing = None
                storage = None    
                extra_tcl_data={}            
                if tcl_thing.is_online:
                    aws_thing = await self.aws_iot.async_get_thing(tcl_thing.device_id)
                    storage = await get_stored_data(self.hass, tcl_thing.device_id)
                    extra_tcl_data=await self.aws_iot.get_extra_tcl_data(storage,tcl_thing.device_id)
                    
                d = Device(
                    tcl_thing=tcl_thing,
                    aws_thing=aws_thing,
                    device_storage=storage,
                    extra_tcl_data=extra_tcl_data
                )                
                devices.append(d)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        return IotDeviceCoordinatorData(devices)

    def get_device_by_id(self, device_id: str) -> Device | None:
        """Return device by device id."""
        try:
            return [
                device for device in self.data.devices if device.device_id == device_id
            ][0]
        except IndexError:
            return None

    def set_device(self, device: Device) -> None:
        """Set device in coordinator data."""
        for i, d in enumerate(self.data.devices):
            if d.device_id == device.device_id:
                self.data.devices[i] = device
                break
        else:
            self.data.devices.append(device)
