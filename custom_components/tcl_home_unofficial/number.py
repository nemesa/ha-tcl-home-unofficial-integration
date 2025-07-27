"""."""

import logging

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .calculations import celsius_to_fahrenheit
from .config_entry import New_NameConfigEntry
from .coordinator import IotDeviceCoordinator
from .device import Device
from .device_features import DeviceFeatureEnum
from .device_types import DeviceTypeEnum
from .device_enums import ModeEnum, getMode
from .device_data_storage import set_stored_data,get_stored_data
from .tcl_entity_base import TclEntityBase

_LOGGER = logging.getLogger(__name__)


class DesiredStateHandlerForNumber:
    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: IotDeviceCoordinator,
        deviceFeature: DeviceFeatureEnum,
        device: Device,
    ) -> None:
        self.hass = hass
        self.coordinator = coordinator
        self.deviceFeature = deviceFeature
        self.device = device

    def refreshDevice(self, device: Device):
        self.device = device

    async def call_set_number(self, value: int | float) -> str:
        match self.deviceFeature:
            case DeviceFeatureEnum.NUMBER_TARGET_TEMPERATURE:
                return await self.NUMBER_TARGET_TEMPERATURE(value=value)
            case DeviceFeatureEnum.NUMBER_TARGET_DEGREE:
                return await self.NUMBER_TARGET_DEGREE(value=value)

    async def store_target_temp(self, value: int | float):
        stored_data = await get_stored_data(self.hass, self.device.device_id)
        mode = getMode(self.device.data.work_mode)
        # _LOGGER.info("Storing target temperature %s for mode %s in device storage %s",value,mode,self.device.device_id)
        stored_data["target_temperature"][mode]["value"] = value       
        self.device.storage = stored_data
        await set_stored_data(self.hass, self.device.device_id, stored_data)

    async def NUMBER_TARGET_TEMPERATURE(self, value: int | float):
        # _LOGGER.info("Setting target temperature to %s %s", value, self.device)
        min_temp = self.device.data.lower_temperature_limit
        max_temp = self.device.data.upper_temperature_limit

        if value < min_temp or value > max_temp:
            _LOGGER.error(
                "Invalid target temperature (°C): %s (Min:%s Max:%s)",
                value,
                min_temp,
                max_temp,
            )
            return
        
        desired_state = {"targetTemperature": value}
        if DeviceFeatureEnum.INTERNAL_SET_TFT_WITH_TT in self.device.supported_features:
            value_fahrenheit_to_set = celsius_to_fahrenheit(value)
            desired_state["targetFahrenheitTemp"] = value_fahrenheit_to_set
        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )

    async def NUMBER_TARGET_DEGREE(self, value: int | float):
        min_temp = self.device.data.lower_temperature_limit
        max_temp = self.device.data.upper_temperature_limit

        if value < min_temp or value > max_temp:
            _LOGGER.error(
                "Invalid target temperature (°C): %s (Min:%s Max:%s)",
                value,
                min_temp,
                max_temp,
            )
            return

        value_celsius_to_set = value
        value_fahrenheit_to_set = celsius_to_fahrenheit(value)
        desired_state = {
            "targetCelsiusDegree": value_celsius_to_set,
            "targetFahrenheitDegree": value_fahrenheit_to_set,
        }
        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )

def is_allowed(device: Device) -> bool:
    if device.device_type == DeviceTypeEnum.PORTABLE_AC:
        return getMode(device.data.work_mode) == ModeEnum.COOL
    else:
        if DeviceFeatureEnum.SWITCH_8_C_HEATING in device.supported_features:
            if device.data.eight_add_hot == 1:
                return False
        return True


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: New_NameConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Binary Sensors."""
    coordinator = config_entry.runtime_data.coordinator

    customEntities = []
    for device in config_entry.devices:

        if DeviceFeatureEnum.NUMBER_TARGET_TEMPERATURE in device.supported_features:
            customEntities.append(
                TemperatureHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.NUMBER_TARGET_TEMPERATURE,
                    name="Set Target Temperature",
                    type="SetTargetTemperature",
                    available_fn=lambda device: is_allowed(device),
                    current_value_fn=lambda device: float(
                        device.data.target_temperature
                    )
                    if DeviceFeatureEnum.NUMBER_TARGET_TEMPERATURE_ALLOW_HALF_DIGITS in device.supported_features
                    else int(device.data.target_temperature),
                )
            )

        if DeviceFeatureEnum.NUMBER_TARGET_DEGREE in device.supported_features:
            customEntities.append(
                TemperatureHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.NUMBER_TARGET_DEGREE,
                    name="Set Target Temperature",
                    type="SetTargetDegree",
                    available_fn=lambda device: is_allowed(device),
                    current_value_fn=lambda device: float(
                        device.data.target_temperature
                    )
                    if DeviceFeatureEnum.NUMBER_TARGET_TEMPERATURE_ALLOW_HALF_DIGITS in device.supported_features
                    else int(device.data.target_temperature),
                )
            )

    async_add_entities(customEntities)


class TemperatureHandler(TclEntityBase, NumberEntity):
    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: IotDeviceCoordinator,
        device: Device,
        type: str,
        name: str,
        deviceFeature: DeviceFeatureEnum,
        current_value_fn: lambda device: bool | None,
        available_fn: lambda device: bool,
    ) -> None:
        TclEntityBase.__init__(self, coordinator, type, name, device)
        self.hass = hass

        self.iot_handler = DesiredStateHandlerForNumber(
            hass=hass,
            coordinator=coordinator,
            deviceFeature=deviceFeature,
            device=self.device,
        )
        self.current_value_fn = current_value_fn
        self.available_fn = available_fn
        self._attr_available = True

        self._attr_assumed_state = False
        self._attr_device_class = NumberDeviceClass.TEMPERATURE
        self._attr_translation_key = None
        self._attr_mode = NumberMode.BOX
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_native_value = self.current_value_fn(self.device)

        self._attr_native_min_value = self.device.data.lower_temperature_limit
        self._attr_native_max_value = self.device.data.upper_temperature_limit        
        self._attr_native_step = self.device.storage["non_user_config"]["native_temp_step"]

    @property
    def available(self) -> bool:
        return self.available_fn(self.device)

    @property
    def device_class(self) -> str:
        return NumberDeviceClass.TEMPERATURE

    @property
    def native_value(self) -> int | float:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        self.iot_handler.refreshDevice(self.device)
        return self.current_value_fn(self.device)

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        self.iot_handler.refreshDevice(self.device)
        await self.iot_handler.call_set_number(value)
        await self.iot_handler.store_target_temp(value)
        await self.coordinator.async_refresh()
        self.async_write_ha_state()
