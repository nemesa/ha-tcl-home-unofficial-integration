"""Interfaces with the Example api sensors."""

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

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
    # coordinator: ExampleCoordinator = config_entry.runtime_data.coordinator

    # Enumerate all the binary sensors in your data value from your DataUpdateCoordinator and add an instance of your binary sensor class
    # to a list for each one.
    # This maybe different in your specific case, depending on how your data is structured

    sensors = []
    for device in config_entry.devices:
        sensors.append(PowerStateBinarySensor(device))
        sensors.append(BeepSwitchBinarySensor(device))

    # Create the binary sensors.
    async_add_entities(sensors)


class PowerStateBinarySensor(BinarySensorEntity):
    """Implementation of a sensor."""

    def __init__(self, device: Device) -> None:
        _LOGGER.info("Creating PowerStateBinarySensor for device: %s", device)
        self.device = device

    @callback
    def _handle_coordinator_update(self) -> None:
        _LOGGER.info("PowerStateBinarySensor._handle_coordinator_update")

    @property
    def device_class(self) -> str:
        """Return device class."""
        # https://developers.home-assistant.io/docs/core/entity/binary-sensor#available-device-classes
        return BinarySensorDeviceClass.POWER

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
        return "Power State"

    @property
    def is_on(self) -> bool | None:
        """Return if the binary sensor is on."""
        # This needs to enumerate to true or false
        return self.device.power_state

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        # All entities must have a unique id.  Think carefully what you want this to be as
        # changing it later will cause HA to create new entities.
        return f"{DOMAIN}-PowerState-{self.device.device_id}"

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        # Add any additional attributes you want on your sensor.
        attrs = {}
        attrs["extra_info"] = "Extra Info"
        return attrs


class BeepSwitchBinarySensor(BinarySensorEntity):
    """Implementation of a sensor."""

    def __init__(self, device: Device) -> None:
        _LOGGER.info("Creating BeepSwitchBinarySensor for device: %s", device)
        self.device = device

    @callback
    def _handle_coordinator_update(self) -> None:
        _LOGGER.info("BeepSwitchBinarySensor._handle_coordinator_update")

    @property
    def device_class(self) -> str:
        """Return device class."""
        # https://developers.home-assistant.io/docs/core/entity/binary-sensor#available-device-classes
        return BinarySensorDeviceClass.SOUND

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
        return "Beep Switch State"

    @property
    def is_on(self) -> bool | None:
        """Return if the binary sensor is on."""
        # This needs to enumerate to true or false
        return self.device.beep_switch_state

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        # All entities must have a unique id.  Think carefully what you want this to be as
        # changing it later will cause HA to create new entities.
        return f"{DOMAIN}-BeepSwitch-{self.device.device_id}"

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        # Add any additional attributes you want on your sensor.
        attrs = {}
        attrs["extra_info"] = "Extra Info"
        return attrs
