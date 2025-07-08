"""."""

import logging

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .aws_iot import AwsIot
from .config_entry import New_NameConfigEntry
from .coordinator import IotDeviceCoordinator
from .device import Device
from .tcl_entity_base import TclEntityBase

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: New_NameConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Binary Sensors."""
    coordinator = config_entry.runtime_data.coordinator

    customEntities = []
    for device in config_entry.devices:
        customEntities.append(SetTargetTempEntity(coordinator, device))

    async_add_entities(customEntities)


class SetTargetTempEntity(TclEntityBase, NumberEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        TclEntityBase.__init__(
            self, coordinator, "SetTargetTempEntity", "Set Target Temperature", device
        )

        self.aws_iot = coordinator.get_aws_iot()

        self._attr_assumed_state = False
        self._attr_device_class = NumberDeviceClass.TEMPERATURE
        self._attr_translation_key = None
        self._attr_mode = NumberMode.BOX
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_native_value = device.data.target_temperature

        self._attr_native_min_value = 16
        self._attr_native_max_value = 36
        self._attr_native_step = 1

    @property
    def device_class(self) -> str:
        return NumberDeviceClass.TEMPERATURE

    @property
    def native_value(self) -> int | float:
        return float(self.device.data.target_temperature)

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        # _LOGGER.info("Setting target temperature for device %s to %s",self.device.device_id,value)
        await self.aws_iot.async_set_target_temperature(
            self.device.device_id, int(value)
        )
        self.device.data.target_temperature = int(value)
        self.coordinator.set_device(self.device)
        await self.coordinator.async_refresh()
        self.async_write_ha_state()
