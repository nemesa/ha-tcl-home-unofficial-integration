"""Switch setup for our Integration."""

import logging
from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .aws_iot import AwsIot
from .config_entry import New_NameConfigEntry
from .const import DOMAIN
from .device import Device, toDeviceInfo

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: New_NameConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Binary Sensors."""
    # This gets the data update coordinator from the config entry runtime data as specified in your __init__.py

    switches = []
    for device in config_entry.devices:
        switches.append(PowerSwitch(device, config_entry.aws_iot))

    async_add_entities(switches)


class PowerSwitch(SwitchEntity):
    def __init__(self, device: Device, aws_iot: AwsIot) -> None:
        """Initialise sensor."""
        self.device = device
        self.aws_iot = aws_iot

    @callback
    def _handle_coordinator_update(self) -> None:
        _LOGGER.info("PowerSwitch._handle_coordinator_update")

    @property
    def device_class(self) -> str:
        """Return device class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
        return SwitchDeviceClass.SWITCH

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        # All entities must have a unique id.  Think carefully what you want this to be as
        # changing it later will cause HA to create new entities.
        return f"{DOMAIN}-PowerSwitch-{self.device.device_id}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        # Identifiers are what group entities into the same device.
        # If your device is created elsewhere, you can just specify the indentifiers parameter.
        # If your device connects via another device, add via_device parameter with the indentifiers of that device.
        return toDeviceInfo(self.device)

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Power Switch"

    @property
    def is_on(self) -> bool | None:
        """Return if the binary sensor is on."""
        # This needs to enumerate to true or false
        return self.device.power_state

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        _LOGGER.info("PowerSwitch.async_turn_on")
        await self.hass.async_add_executor_job(
            self.aws_iot.turnOn, self.device.device_id
        )
        # ----------------------------------------------------------------------------
        # Use async_refresh on the DataUpdateCoordinator to perform immediate update.
        # Using self.async_update or self.coordinator.async_request_refresh may delay update due
        # to trying to batch requests.
        # ----------------------------------------------------------------------------
        # await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        _LOGGER.info("PowerSwitch.async_turn_off")
        await self.hass.async_add_executor_job(
            self.aws_iot.turnOff, self.device.device_id
        )
        # await self.hass.async_add_executor_job(
        #     self.coordinator.api.set_data, self.device_id, self.parameter, "OFF"
        # )
        # ----------------------------------------------------------------------------
        # Use async_refresh on the DataUpdateCoordinator to perform immediate update.
        # Using self.async_update or self.coordinator.async_request_refresh may delay update due
        # to trying to batch requests.
        # ----------------------------------------------------------------------------
        # await self.coordinator.async_refresh()

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        # Add any additional attributes you want on your sensor.
        attrs = {}
        # attrs["last_rebooted"] = self.coordinator.get_device_parameter(
        #     self.device_id, "last_reboot"
        # )
        return attrs
