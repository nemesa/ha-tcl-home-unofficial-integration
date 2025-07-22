"""."""

import logging

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .config_entry import New_NameConfigEntry
from .coordinator import IotDeviceCoordinator
from .device import (
    Device,
    DeviceFeature,
    DeviceTypeEnum,
    get_device_storage,
    getSupportedFeatures,
)
from .device_ac_common import ModeEnum, getMode
from .device_data_storage import set_stored_data
from .tcl_entity_base import TclEntityBase

_LOGGER = logging.getLogger(__name__)


class DesiredStateHandlerForNumber:
    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: IotDeviceCoordinator,
        deviceFeature: DeviceFeature,
        device: Device,
    ) -> None:
        self.hass = hass
        self.coordinator = coordinator
        self.deviceFeature = deviceFeature
        self.device = device

    def refreshDevice(self, device: Device):
        self.device = device

    def celsius_to_fahrenheit(self, celsius: int | float) -> int | float:
        return round((celsius * (9 / 5)) + 32)

    async def call_set_number(self, value: int | float) -> str:
        match self.deviceFeature:
            case DeviceFeature.NUMBER_TARGET_TEMPERATURE:
                return await self.NUMBER_TARGET_TEMPERATURE(value=value)
            case DeviceFeature.NUMBER_TARGET_DEGREE:
                return await self.NUMBER_TARGET_DEGREE(value=value)

    async def store_target_temp(self, value: int | float):
        stored_data = await get_device_storage(self.hass, self.device)
        mode = getMode(self.device.data.work_mode)
        # _LOGGER.info("Storing target temperature %s for mode %s in device storage %s",value,mode,self.device.device_id)
        match self.deviceFeature:
            case DeviceFeature.NUMBER_TARGET_TEMPERATURE:
                stored_data["target_temperature"][mode] = value
            case DeviceFeature.NUMBER_TARGET_DEGREE:
                stored_data["target_temperature"][mode]["value"] = value
                stored_data["target_temperature"][mode]["targetCelsiusDegree"] = value
                stored_data["target_temperature"][mode]["targetFahrenheitDegree"] = (
                    self.celsius_to_fahrenheit(value)
                )
        self.device.storage = stored_data
        await set_stored_data(self.hass, self.device.device_id, stored_data)

    async def NUMBER_TARGET_TEMPERATURE(self, value: int | float):
        # _LOGGER.info("Setting target temperature to %s %s", value, self.device)
        min_temp = self.device.storage["non_user_config"]["min_celsius_temp"]
        max_temp = self.device.storage["non_user_config"]["max_celsius_temp"]

        if value < min_temp or value > max_temp:
            _LOGGER.error(
                "Invalid target temperature (°C): %s (Min:%s Max:%s)",
                value,
                min_temp,
                max_temp,
            )
            return

        desired_state = {"targetTemperature": value}
        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )

    async def NUMBER_TARGET_DEGREE(self, value: int | float):
        min_temp = self.device.storage["non_user_config"]["min_celsius_temp"]
        max_temp = self.device.storage["non_user_config"]["max_celsius_temp"]

        if value < min_temp or value > max_temp:
            _LOGGER.error(
                "Invalid target temperature (°C): %s (Min:%s Max:%s)",
                value,
                min_temp,
                max_temp,
            )
            return

        value_celsius_to_set = value
        value_fahrenheit_to_set = self.celsius_to_fahrenheit(value)
        desired_state = {
            "targetCelsiusDegree": value_celsius_to_set,
            "targetFahrenheitDegree": value_fahrenheit_to_set,
        }
        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )


def allow_float(supported_features: list[DeviceFeature]) -> bool:
    return (
        DeviceFeature.NUMBER_TARGET_TEMPERATURE_ALLOW_HALF_DIGITS in supported_features
    )


def is_allowed(device: Device) -> bool:
    if device.device_type == DeviceTypeEnum.PORTABLE_AC:
        return getMode(device.data.work_mode) == ModeEnum.COOL
    else:
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
        supported_features = getSupportedFeatures(device.device_type)

        if DeviceFeature.NUMBER_TARGET_TEMPERATURE in supported_features:
            customEntities.append(
                TemperatureHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeature.NUMBER_TARGET_TEMPERATURE,
                    name="Set Target Temperature",
                    type="SetTargetTemperature",
                    available_fn=lambda device: is_allowed(device),
                    current_value_fn=lambda device: float(
                        device.data.target_temperature
                    )
                    if allow_float(supported_features)
                    else int(device.data.target_temperature),
                )
            )

        if DeviceFeature.NUMBER_TARGET_DEGREE in supported_features:
            customEntities.append(
                TemperatureHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeature.NUMBER_TARGET_DEGREE,
                    name="Set Target Temperature",
                    type="SetTargetDegree",
                    available_fn=lambda device: is_allowed(device),
                    current_value_fn=lambda device: float(
                        device.data.target_temperature
                    )
                    if allow_float(supported_features)
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
        deviceFeature: DeviceFeature,
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

        self._attr_native_min_value = self.device.storage["non_user_config"][
            "min_celsius_temp"
        ]
        self._attr_native_max_value = self.device.storage["non_user_config"][
            "max_celsius_temp"
        ]
        self._attr_native_step = self.device.storage["non_user_config"][
            "native_temp_step"
        ]

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


# class SetTargetTempEntity(TclEntityBase, NumberEntity):
#     def __init__(
#         self, hass: HomeAssistant, coordinator: IotDeviceCoordinator, device: Device
#     ) -> None:
#         TclEntityBase.__init__(
#             self, coordinator, "SetTargetTempEntity", "Set Target Temperature", device
#         )
#         self.hass = hass

#         self.device_features = getSupportedFeatures(device.device_type)

#         self.aws_iot = coordinator.get_aws_iot()

#         self._attr_assumed_state = False
#         self._attr_device_class = NumberDeviceClass.TEMPERATURE
#         self._attr_translation_key = None
#         self._attr_mode = NumberMode.BOX
#         self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
#         self._attr_native_value = device.data.target_temperature

#         self._attr_native_min_value = 16
#         self._attr_native_max_value = 36
#         self._attr_native_step = 1
#         if (
#             DeviceFeature.NUMBER_TARGET_TEMPERATURE_ALLOW_HALF_DIGITS
#             in self.device_features
#         ):
#             self._attr_native_step = 0.5
#             self._attr_native_min_value = 16.0
#             self._attr_native_max_value = 36.0

#         if self.device.device_type == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
#             self._attr_native_max_value = 31

#     @property
#     def device_class(self) -> str:
#         return NumberDeviceClass.TEMPERATURE

#     @property
#     def native_value(self) -> int | float:
#         if (
#             DeviceFeature.NUMBER_TARGET_TEMPERATURE_ALLOW_HALF_DIGITS
#             in self.device_features
#         ):
#             return float(self.device.data.target_temperature)
#         return int(self.device.data.target_temperature)

#     async def async_set_native_value(self, value: float) -> None:
#         """Update the current value."""

#         value_to_set = int(value)
#         if (
#             DeviceFeature.NUMBER_TARGET_TEMPERATURE_ALLOW_HALF_DIGITS
#             in self.device_features
#         ):
#             value_to_set = float(value)

#         data_to_store = None
#         mode = getMode(self.device.data.work_mode)
#         if self.device.device_type == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
#             data_to_store = await get_stored_spit_ac_fresh_data(
#                 self.hass, self.device.device_id
#             )
#         if self.device.device_type == DeviceTypeEnum.SPLIT_AC_TYPE_1:
#             data_to_store = await get_stored_spit_ac_type1_data(
#                 self.hass, self.device.device_id
#             )
#         data_to_store["target_temperature"][mode] = value_to_set

#         await set_stored_data(
#             self.hass,
#             self.device.device_id,
#             data_to_store,
#         )

#         await self.aws_iot.async_set_target_temperature(
#             self.device.device_id, self.device.device_type, value_to_set
#         )
#         self.device.data.target_temperature = int(value)
#         self.coordinator.set_device(self.device)
#         await self.coordinator.async_refresh()
#         self.async_write_ha_state()


# class SetTargetDegreeEntity(TclEntityBase, NumberEntity):
#     def __init__(
#         self,
#         hass: HomeAssistant,
#         coordinator: IotDeviceCoordinator,
#         device: Device,
#         available_fn: lambda device: bool,
#     ) -> None:
#         TclEntityBase.__init__(
#             self, coordinator, "SetTargetDegree", "Set Target Temperature", device
#         )
#         self.hass = hass

#         self._attr_available = True
#         self.available_fn = available_fn
#         self.device_features = getSupportedFeatures(device.device_type)

#         self.aws_iot = coordinator.get_aws_iot()

#         self._attr_assumed_state = False
#         self._attr_device_class = NumberDeviceClass.TEMPERATURE
#         self._attr_translation_key = None
#         self._attr_mode = NumberMode.BOX
#         self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
#         self._attr_native_value = device.data.target_celsius_degree

#         self._attr_native_min_value = 18
#         self._attr_native_max_value = 32

#     @property
#     def available(self) -> bool:
#         return self.available_fn(self.device)

#     @property
#     def device_class(self) -> str:
#         return NumberDeviceClass.TEMPERATURE

#     @property
#     def native_value(self) -> int | float:
#         self.device = self.coordinator.get_device_by_id(self.device.device_id)
#         return int(self.device.data.target_celsius_degree)

#     async def async_set_native_value(self, value: float) -> None:
#         """Update the current value."""
#         _LOGGER.info("Setting target degree to %s", value)
#         value_celsius_to_set = int(value)
#         value_fahrenheit_to_set = round((value_celsius_to_set * (9 / 5)) + 32)

#         if self.device.device_type == DeviceTypeEnum.PORTABLE_AC:
#             data_to_store = await get_stored_portable_ac_data(
#                 self.hass, self.device.device_id
#             )
#             data_to_store["target_temperature"]["Cool"]["targetCelsiusDegree"] = (
#                 value_celsius_to_set
#             )
#             data_to_store["target_temperature"]["Cool"]["targetFahrenheitDegree"] = (
#                 value_fahrenheit_to_set
#             )

#             await set_stored_data(self.hass, self.device.device_id, data_to_store)

#         await self.aws_iot.async_set_target_degree(
#             self.device.device_id,
#             self.device.device_type,
#             value_celsius_to_set,
#             value_fahrenheit_to_set,
#         )
#         self.device.data.target_celsius_degree = int(value)
#         self.coordinator.set_device(self.device)
#         await self.coordinator.async_refresh()
#         self.async_write_ha_state()
