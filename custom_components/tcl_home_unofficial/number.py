"""."""

import logging

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .config_entry import New_NameConfigEntry
from .coordinator import IotDeviceCoordinator
from .device import Device, DeviceFeature, DeviceTypeEnum, getSupportedFeatures
from .device_data_storage import set_stored_data
from .device_ac_common import getMode, ModeEnum
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

        if DeviceFeature.NUMBER_TARGET_DEGREE in supported_features:
            customEntities.append(
                SetTargetDegreeEntity(
                    hass,
                    coordinator,
                    device,
                    available_fn=lambda device: getMode(device.data.work_mode)
                    == ModeEnum.COOL,
                )
            )

    async_add_entities(customEntities)


class SetTargetTempEntity(TclEntityBase, NumberEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        TclEntityBase.__init__(
            self, coordinator, "SetTargetTempEntity", "Set Target Temperature", device
        )

        self.device_features = getSupportedFeatures(device.device_type)

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
        if (
            DeviceFeature.NUMBER_TARGET_TEMPERATURE_ALLOW_HALF_DIGITS
            in self.device_features
        ):
            self._attr_native_step = 0.5
            self._attr_native_min_value = 16.0
            self._attr_native_max_value = 36.0

        if self.device.device_type == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
            self._attr_native_max_value = 31

    @property
    def device_class(self) -> str:
        return NumberDeviceClass.TEMPERATURE

    @property
    def native_value(self) -> int | float:
        if (
            DeviceFeature.NUMBER_TARGET_TEMPERATURE_ALLOW_HALF_DIGITS
            in self.device_features
        ):
            return float(self.device.data.target_temperature)
        return int(self.device.data.target_temperature)

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""

        value_to_set = int(value)
        if (
            DeviceFeature.NUMBER_TARGET_TEMPERATURE_ALLOW_HALF_DIGITS
            in self.device_features
        ):
            value_to_set = float(value)

        await self.aws_iot.async_set_target_temperature(
            self.device.device_id, self.device.device_type, value_to_set
        )
        self.device.data.target_temperature = int(value)
        self.coordinator.set_device(self.device)
        await self.coordinator.async_refresh()
        self.async_write_ha_state()


class SetTargetDegreeEntity(TclEntityBase, NumberEntity):
    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: IotDeviceCoordinator,
        device: Device,
        available_fn: lambda device: bool,
    ) -> None:
        TclEntityBase.__init__(
            self, coordinator, "SetTargetDegree", "Set Target Temperature", device
        )
        self.hass = hass

        self._attr_available = True
        self.available_fn = available_fn
        self.device_features = getSupportedFeatures(device.device_type)

        self.aws_iot = coordinator.get_aws_iot()

        self._attr_assumed_state = False
        self._attr_device_class = NumberDeviceClass.TEMPERATURE
        self._attr_translation_key = None
        self._attr_mode = NumberMode.BOX
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_native_value = device.data.target_celsius_degree

        self._attr_native_min_value = 18
        self._attr_native_max_value = 32

    @property
    def available(self) -> bool:
        return self.available_fn(self.device)

    @property
    def device_class(self) -> str:
        return NumberDeviceClass.TEMPERATURE

    @property
    def native_value(self) -> int | float:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        return int(self.device.data.target_celsius_degree)

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        _LOGGER.info("Setting target degree to %s", value)
        value_celsius_to_set = int(value)
        value_fahrenheit_to_set = round((value_celsius_to_set * (9 / 5)) + 32)

        if self.device.device_type == DeviceTypeEnum.PORTABLE_AC:
            await set_stored_data(
                self.hass,
                self.device.device_id,
                {
                    "targetCelsiusDegree": value_celsius_to_set,
                    "targetFahrenheitDegree": value_fahrenheit_to_set,
                },
            )

        await self.aws_iot.async_set_target_degree(
            self.device.device_id,
            self.device.device_type,
            value_celsius_to_set,
            value_fahrenheit_to_set,
        )
        self.device.data.target_celsius_degree = int(value)
        self.coordinator.set_device(self.device)
        await self.coordinator.async_refresh()
        self.async_write_ha_state()
