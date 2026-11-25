"""."""

import logging

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.const import EntityCategory
from homeassistant.const import UnitOfTemperature, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .calculations import celsius_to_fahrenheit
from .config_entry import New_NameConfigEntry
from .coordinator import IotDeviceCoordinator
from .device import Device
from .device_features import DeviceFeatureEnum
from .device_types import DeviceTypeEnum
from .device_enums import ModeEnum, DehumidifierModeEnum
from .data_storage import get_stored_data, safe_get_value, safe_set_value,set_stored_data
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
            case DeviceFeatureEnum.NUMBER_DEHUMIDIFIER_HUMIDITY:
                return await self.NUMBER_DEHUMIDIFIER_HUMIDITY(value=value)
            case DeviceFeatureEnum.NUMBER_ATW_HEAT_Z1_TARGET:
                return await self.coordinator.get_aws_iot().async_set_desired_state(
                    self.device.device_id, {"htWtTWd1": int(value)}
                )
            case DeviceFeatureEnum.NUMBER_ATW_ROOM_Z1_TARGET:
                return await self.coordinator.get_aws_iot().async_set_desired_state(
                    self.device.device_id, {"htEvTGd1": int(value)}
                )
            case DeviceFeatureEnum.NUMBER_ATW_DHW_TARGET:
                return await self.coordinator.get_aws_iot().async_set_desired_state(
                    self.device.device_id, {"lvHWtT": int(value)}
                )
            case DeviceFeatureEnum.NUMBER_ATW_HEATING_CURVE_1:
                return await self.coordinator.get_aws_iot().async_set_desired_state(
                    self.device.device_id, {"htWthCtl1": int(value)}
                )
            case DeviceFeatureEnum.NUMBER_ATW_COOLING_CURVE_1:
                return await self.coordinator.get_aws_iot().async_set_desired_state(
                    self.device.device_id, {"clWthCtl1": int(value)}
                )

    async def store_target_temp(self, value: int | float):
        if self.device.device_type == DeviceTypeEnum.ATW_HEAT_PUMP:
            return
        stored_data = await get_stored_data(self.hass, self.device.device_id)
        mode = self.device.mode_value_to_enum_mapp.get(
            self.device.data.work_mode, ModeEnum.AUTO
        )
        # _LOGGER.info("Storing target temperature %s for mode %s in device storage %s",value,mode,self.device.device_id)
        stored_data["target_temperature"][mode]["value"] = value
        self.device.storage = stored_data
        await set_stored_data(self.hass, self.device.device_id, stored_data)


    async def store_humidity(self, value: int | float):
        stored_data = await get_stored_data(self.hass, self.device.device_id)
        mode = self.device.mode_value_to_enum_mapp.get(
            self.device.data.work_mode, DehumidifierModeEnum.DRY
        )
        # _LOGGER.info("Storing target temperature %s for mode %s in device storage %s",value,mode,self.device.device_id)
        stored_data["humidity"][mode]["value"] = value
        self.device.storage = stored_data
        await set_stored_data(self.hass, self.device.device_id, stored_data)

    async def NUMBER_TARGET_TEMPERATURE(self, value: int | float):
        # _LOGGER.info("Setting target temperature to %s %s", value, self.device)        

        min_temp = safe_get_value(self.device.storage,"user_config.settings.min_temp",18)
        max_temp = safe_get_value(self.device.storage,"user_config.settings.max_temp",36)

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
        min_temp = safe_get_value(self.device.storage,"user_config.settings.min_temp",18)
        max_temp = safe_get_value(self.device.storage,"user_config.settings.max_temp",36)                  

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
        
    async def NUMBER_DEHUMIDIFIER_HUMIDITY(self, value: int | float):
        min_temp = 1
        max_temp = 99

        if value < min_temp or value > max_temp:
            _LOGGER.error(
                "Invalid target humidity (%): %s (Min:%s Max:%s)",
                value,
                min_temp,
                max_temp,
            )
            return

        desired_state = {"Humidity": value}
        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )


def is_allowed(device: Device) -> bool:
    if device.device_type == DeviceTypeEnum.PORTABLE_AC:
        return (
            device.mode_value_to_enum_mapp.get(device.data.work_mode, ModeEnum.AUTO)
            == ModeEnum.COOL
        )
    else:
        if DeviceFeatureEnum.SWITCH_8_C_HEATING in device.supported_features:
            if device and device.data and device.data.eight_add_hot == 1:
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
                    if DeviceFeatureEnum.NUMBER_TARGET_TEMPERATURE_ALLOW_HALF_DIGITS
                    in device.supported_features
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
                    current_value_fn=lambda device: float(device.data.target_temperature) if DeviceFeatureEnum.NUMBER_TARGET_TEMPERATURE_ALLOW_HALF_DIGITS in device.supported_features else int(device.data.target_temperature),
                )
            )
            
        if DeviceFeatureEnum.NUMBER_DEHUMIDIFIER_HUMIDITY in device.supported_features:
            customEntities.append(
                HumidityHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.NUMBER_DEHUMIDIFIER_HUMIDITY,
                    name="Set Target Humidity",
                    type="SetDehumidifierHumidity",
                    available_fn=lambda device: is_allowed(device),
                    current_value_fn=lambda device: device.data.humidity
                )
            )
        
        if (DeviceFeatureEnum.USER_CONFIG_SETTINGS_NATIVE_TEMP_STEP in device.supported_features):
            customEntities.append(
                ConfigTempNumberHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    config_path="user_config.settings.native_temp_step",
                    name="Set Temp. Step",
                    min=0.5,
                    max=1,
                    step=0.5
                )
            )
        
        if (DeviceFeatureEnum.USER_CONFIG_SETTINGS_MAX_TEMP in device.supported_features):
            customEntities.append(
                ConfigTempNumberHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    config_path="user_config.settings.max_temp",
                    name="Max Temp.",
                    min=10,
                    max=40,
                    step=1
                )
            )
        
        if (DeviceFeatureEnum.USER_CONFIG_SETTINGS_MIN_TEMP in device.supported_features):
            customEntities.append(
                ConfigTempNumberHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    config_path="user_config.settings.min_temp",
                    name="Min Temp.",
                    min=10,
                    max=40,
                    step=1
                )
            )

        if DeviceFeatureEnum.NUMBER_ATW_HEAT_Z1_TARGET in device.supported_features:
            z1_handler = TemperatureHandler(
                hass=hass,
                coordinator=coordinator,
                device=device,
                deviceFeature=DeviceFeatureEnum.NUMBER_ATW_HEAT_Z1_TARGET,
                name="Set Heating Water Temp Zone 1",
                type="SetATWHeatZ1Target",
                available_fn=lambda device: True,
                current_value_fn=lambda device: int(device.data.target_temp_heat_z1),
            )
            z1_handler._attr_native_min_value = 20
            z1_handler._attr_native_max_value = 65
            z1_handler._attr_native_step = 1
            customEntities.append(z1_handler)

        if DeviceFeatureEnum.NUMBER_ATW_ROOM_Z1_TARGET in device.supported_features:
            room_handler = TemperatureHandler(
                hass=hass,
                coordinator=coordinator,
                device=device,
                deviceFeature=DeviceFeatureEnum.NUMBER_ATW_ROOM_Z1_TARGET,
                name="Set Room Temp Zone 1",
                type="SetATWRoomZ1Target",
                available_fn=lambda device: True,
                current_value_fn=lambda device: int(device.data.target_temp_room_z1),
            )
            room_handler._attr_native_min_value = 16
            room_handler._attr_native_max_value = 32
            room_handler._attr_native_step = 1
            customEntities.append(room_handler)

        if DeviceFeatureEnum.NUMBER_ATW_DHW_TARGET in device.supported_features:
            dhw_handler = TemperatureHandler(
                hass=hass,
                coordinator=coordinator,
                device=device,
                deviceFeature=DeviceFeatureEnum.NUMBER_ATW_DHW_TARGET,
                name="Set Domestic Hot Water Temp",
                type="SetATWDHWTarget",
                available_fn=lambda device: True,
                current_value_fn=lambda device: int(device.data.target_temp_domestic),
            )
            dhw_handler._attr_native_min_value = 30
            dhw_handler._attr_native_max_value = 60
            dhw_handler._attr_native_step = 1
            customEntities.append(dhw_handler)

        if DeviceFeatureEnum.NUMBER_ATW_HEATING_CURVE_1 in device.supported_features:
            customEntities.append(
                CurveNumberHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.NUMBER_ATW_HEATING_CURVE_1,
                    name="Heating Weather Curve Zone 1",
                    type="SetATWHeatingCurve1",
                    current_value_fn=lambda device: int(device.data.heating_curve_1),
                    min_val=1,
                    max_val=18,
                )
            )

        if DeviceFeatureEnum.NUMBER_ATW_COOLING_CURVE_1 in device.supported_features:
            customEntities.append(
                CurveNumberHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.NUMBER_ATW_COOLING_CURVE_1,
                    name="Cooling Weather Curve Zone 1",
                    type="SetATWCoolingCurve1",
                    current_value_fn=lambda device: int(device.data.cooling_curve_1),
                    min_val=1,
                    max_val=8,
                )
            )

    async_add_entities(customEntities)


class CurveNumberHandler(TclEntityBase, NumberEntity):
    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: IotDeviceCoordinator,
        device: Device,
        type: str,
        name: str,
        deviceFeature: DeviceFeatureEnum,
        current_value_fn: lambda device: int,
        min_val: int = 1,
        max_val: int = 9,
    ) -> None:
        TclEntityBase.__init__(self, coordinator, type, name, device)
        self.hass = hass
        self.device = device
        self.iot_handler = DesiredStateHandlerForNumber(
            hass=hass,
            coordinator=coordinator,
            deviceFeature=deviceFeature,
            device=self.device,
        )
        self.current_value_fn = current_value_fn
        self._attr_available = True
        self._attr_assumed_state = False
        self._attr_mode = NumberMode.BOX
        self._attr_native_min_value = min_val
        self._attr_native_max_value = max_val
        self._attr_native_step = 1

    @property
    def icon(self):
        return "mdi:chart-bell-curve"

    @property
    def native_value(self) -> int:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        self.iot_handler.refreshDevice(self.device)
        return self.current_value_fn(self.device)

    async def async_set_native_value(self, value: float) -> None:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        self.iot_handler.refreshDevice(self.device)
        await self.iot_handler.call_set_number(int(value))
        await self.coordinator.async_refresh()
        self.async_write_ha_state()


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

        self._attr_native_min_value = safe_get_value(self.device.storage,"user_config.settings.min_temp",18)
        self._attr_native_max_value = safe_get_value(self.device.storage,"user_config.settings.max_temp",36)  
        self._attr_native_step = safe_get_value(self.device.storage,"user_config.settings.native_temp_step",1)          

    @property
    def available(self) -> bool:
        if self.device.is_online:
            return self.available_fn(self.device)
        return False

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

class HumidityHandler(TclEntityBase, NumberEntity):
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
        self._attr_device_class = NumberDeviceClass.HUMIDITY
        self._attr_translation_key = None
        self._attr_mode = NumberMode.BOX
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_native_value = self.current_value_fn(self.device)

        self._attr_native_min_value = 1
        self._attr_native_max_value = 99
        self._attr_native_step = 1

    @property
    def available(self) -> bool:
        if self.device.is_online:
            return self.available_fn(self.device)
        return False

    @property
    def device_class(self) -> str:
        return NumberDeviceClass.HUMIDITY

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
        await self.iot_handler.store_humidity(value)
        await self.coordinator.async_refresh()
        self.async_write_ha_state()

class ConfigTempNumberHandler(TclEntityBase, NumberEntity):
    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: IotDeviceCoordinator,
        device: Device,
        name: str,
        config_path: str,
        min:float,
        max:float,
        step:float
    ) -> None:
        TclEntityBase.__init__(self, coordinator, config_path, name, device)
        self.hass = hass
        self.device = device
       
        self.config_path = config_path
        self._attr_entity_category = EntityCategory.CONFIG


        self._attr_native_min_value = min
        self._attr_native_max_value = max
        self._attr_native_step = step
        self._attr_mode=NumberMode.BOX

    @property
    def icon(self):
        return "mdi:cog"

    @property
    def device_class(self) -> str:
        return NumberDeviceClass.TEMPERATURE

    @property
    def native_value(self) -> int | float:
        # self.device = self.coordinator.get_device_by_id(self.device.device_id)
        # stored_data=await get_device_storage(self.hass,self.device)
        if self.config_path=="user_config.settings.min_temp":
            return safe_get_value(self.device.storage, self.config_path, 18)
        if self.config_path=="user_config.settings.max_temp":
            return safe_get_value(self.device.storage, self.config_path, 36)
        if self.config_path=="user_config.settings.native_temp_step":
            return safe_get_value(self.device.storage, self.config_path, 1)
        return safe_get_value(self.device.storage, self.config_path, 20)

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        self.device = self.coordinator.get_device_by_id(self.device.device_id)

        storage_data, need_save = safe_set_value(
            self.device.storage, self.config_path, value, overwrite_if_exists=True
        )

        if need_save:
            await set_stored_data(self.hass, self.device.device_id, storage_data)
        await self.coordinator.async_refresh()        