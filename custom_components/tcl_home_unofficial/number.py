"""."""

import logging

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .config_entry import New_NameConfigEntry
from .coordinator import IotDeviceCoordinator
from .device import Device, getSupportedFeatures,DeviceFeature
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
        supported_features = getSupportedFeatures(device.device_type)
                
        if DeviceFeature.NUMBER_TARGET_TEMPERATURE in supported_features:
            customEntities.append(SetTargetTempEntity(coordinator, device))

    async_add_entities(customEntities)


class SetTargetTempEntity(TclEntityBase, NumberEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        TclEntityBase.__init__(
            self, coordinator, "SetTargetTempEntity", "Set Target Temperature", device
        )
        
        self.device_features= getSupportedFeatures(device.device_type)

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
        if DeviceFeature.NUMBER_TARGET_TEMPERATURE_ALLOW_HALF_DIGITS in self.device_features:
            self._attr_native_step = 0.5
            self._attr_native_min_value = 16.0
            self._attr_native_max_value = 36.0

    @property
    def device_class(self) -> str:
        return NumberDeviceClass.TEMPERATURE

    @property
    def native_value(self) -> int | float:
        if DeviceFeature.NUMBER_TARGET_TEMPERATURE_ALLOW_HALF_DIGITS in self.device_features:
            return float(self.device.data.target_temperature)
        return int(self.device.data.target_temperature)

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        
        value_to_set = int(value)
        if DeviceFeature.NUMBER_TARGET_TEMPERATURE_ALLOW_HALF_DIGITS in self.device_features:
            value_to_set= float(value)
        
        await self.aws_iot.async_set_target_temperature(
            self.device.device_id,set.device.device_type,  value_to_set
        )
        self.device.data.target_temperature = int(value)
        self.coordinator.set_device(self.device)
        await self.coordinator.async_refresh()
        self.async_write_ha_state()
