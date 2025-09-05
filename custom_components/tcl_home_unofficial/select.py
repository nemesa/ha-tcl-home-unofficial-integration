"""."""

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .calculations import celsius_to_fahrenheit
from .config_entry import New_NameConfigEntry
from .coordinator import IotDeviceCoordinator
from .device import Device, get_desired_state_for_mode_change
from .device_features import DeviceFeatureEnum
from .device_types import DeviceTypeEnum
from .device_enums import (
    ModeEnum,
    DehumidifierModeEnum,
    LeftAndRightAirSupplyVectorEnum,
    getLeftAndRightAirSupplyVector,
    SleepModeEnum,
    getSleepMode,
    UpAndDownAirSupplyVectorEnum,
    getUpAndDownAirSupplyVector,
    WindSeed7GearEnum,
    getWindSeed7Gear,
    WindSeedEnum,
    getWindSpeed,
    PortableWindSeedEnum,
    getPortableWindSeed,
    PortableWind4ValueSeedEnum,
    getPortableWind4ValueSeed,
    TemperatureTypeEnum,
    getTemperatureType,
    FreshAirEnum,
    getFreshAir,
    GeneratorModeEnum,
    getGeneratorMode,
    WindFeelingEnum,
    getWindFeeling,
    WindowAcWindSeedEnum,
    getWindowAcWindSeed,
    WindSpeedLowMediumHigh,
    getWindSpeedLowMediumHigh,    
)

from .tcl_entity_base import TclEntityBase
from .data_storage import (
    safe_get_value,
    get_stored_data,
    safe_set_value,
    set_stored_data,
)

_LOGGER = logging.getLogger(__name__)


class DesiredStateHandlerForSelect:
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

    async def call_select_option(self, value: str) -> str:
        match self.deviceFeature:
            case DeviceFeatureEnum.SELECT_SLEEP_MODE:
                return await self.SELECT_SLEEP_MODE(value=value)
            case DeviceFeatureEnum.SELECT_MODE:
                return await self.SELECT_MODE(value=value)
            case DeviceFeatureEnum.SELECT_DEHUMIDIFIER_WIND_SPEED_LOW_MEDIUM_HEIGH:
                return await self.SELECT_DEHUMIDIFIER_WIND_SPEED_LOW_MEDIUM_HEIGH(value=value)
            case DeviceFeatureEnum.SELECT_WIND_SPEED_7_GEAR:
                return await self.SELECT_WIND_SPEED(value=value)
            case DeviceFeatureEnum.SELECT_WIND_SPEED_7_GEAR:
                return await self.SELECT_WIND_SPEED_7_GEAR(value=value)
            case DeviceFeatureEnum.SELECT_PORTABLE_WIND_SPEED:
                return await self.SELECT_PORTABLE_WIND_SPEED(value=value)
            case DeviceFeatureEnum.SELECT_PORTABLE_WIND_4VALUE_SPEED:
                return await self.SELECT_PORTABLE_WIND_4VALUE_SPEED(value=value)
            case DeviceFeatureEnum.SELECT_WINDOW_AS_WIND_SPEED:
                return await self.SELECT_WINDOW_AS_WIND_SPEED(value=value)
            case DeviceFeatureEnum.SELECT_GENERATOR_MODE:
                return await self.SELECT_GENERATOR_MODE(value=value)
            case DeviceFeatureEnum.SELECT_WIND_FEELING:
                return await self.SELECT_WIND_FEELING(value=value)
            case DeviceFeatureEnum.SELECT_VERTICAL_DIRECTION:
                return await self.SELECT_VERTICAL_DIRECTION(value=value)
            case DeviceFeatureEnum.SELECT_HORIZONTAL_DIRECTION:
                return await self.SELECT_HORIZONTAL_DIRECTION(value=value)
            case DeviceFeatureEnum.SELECT_TEMPERATURE_TYPE:
                return await self.SELECT_TEMPERATURE_TYPE(value=value)
            case DeviceFeatureEnum.SELECT_FRESH_AIR:
                return await self.SELECT_FRESH_AIR(value=value)

    def current_state(self) -> str:
        match self.deviceFeature:
            case DeviceFeatureEnum.SELECT_SLEEP_MODE:
                return getSleepMode(self.device.data.sleep)
            case DeviceFeatureEnum.SELECT_MODE:
                if DeviceFeatureEnum.INTERNAL_IS_DEHUMIDIFIER in self.device.supported_features:
                    return self.device.mode_value_to_enum_mapp.get(self.device.data.work_mode,DehumidifierModeEnum.DRY)
                else:
                    default_ac_mode=ModeEnum.AUTO if DeviceFeatureEnum.MODE_AC_AUTO in self.device.supported_features else ModeEnum.COOL
                    return self.device.mode_value_to_enum_mapp.get(self.device.data.work_mode,default_ac_mode)
            case DeviceFeatureEnum.SELECT_WIND_SPEED:
                return getWindSpeed(
                    wind_speed=self.device.data.wind_speed,
                    turbo=self.device.data.turbo,
                    silence_switch=self.device.data.silence_switch,
                )
            case DeviceFeatureEnum.SELECT_DEHUMIDIFIER_WIND_SPEED_LOW_MEDIUM_HEIGH:
                return getWindSpeedLowMediumHigh(self.device.data.wind_speed)
            case DeviceFeatureEnum.SELECT_WIND_SPEED_7_GEAR:
                return getWindSeed7Gear(self.device.data.wind_speed_7_gear)
            case DeviceFeatureEnum.SELECT_WINDOW_AS_WIND_SPEED:
                return getWindowAcWindSeed(self.device.data.wind_speed)
            case DeviceFeatureEnum.SELECT_PORTABLE_WIND_SPEED:
                return getPortableWindSeed(
                    wind_speed=self.device.data.wind_speed,
                    has_auto_mode=(
                        DeviceFeatureEnum.MODE_AC_AUTO in self.device.supported_features
                    ),
                )
            case DeviceFeatureEnum.SELECT_PORTABLE_WIND_4VALUE_SPEED:
                return getPortableWind4ValueSeed(
                    wind_speed=self.device.data.wind_speed,
                    has_auto_mode=(
                        DeviceFeatureEnum.MODE_AC_AUTO in self.device.supported_features
                    ),
                )
            case DeviceFeatureEnum.SELECT_PORTABLE_WIND_4VALUE_SPEED:
                return getPortableWind4ValueSeed(
                    wind_speed=self.device.data.wind_speed,
                    has_auto_mode=(
                        DeviceFeatureEnum.MODE_AC_AUTO in self.device.supported_features
                    ),
                )
            case DeviceFeatureEnum.SELECT_PORTABLE_WIND_4VALUE_SPEED:
                return getPortableWind4ValueSeed(
                    wind_speed=self.device.data.wind_speed,
                    has_auto_mode=(
                        DeviceFeatureEnum.MODE_AC_AUTO in self.device.supported_features
                    ),
                )
            case DeviceFeatureEnum.SELECT_GENERATOR_MODE:
                return getGeneratorMode(self.device.data.generator_mode)
            case DeviceFeatureEnum.SELECT_FRESH_AIR:
                return getFreshAir(self.device.data.new_wind_strength)
            case DeviceFeatureEnum.SELECT_WIND_FEELING:
                return getWindFeeling(self.device.data.soft_wind)
            case DeviceFeatureEnum.SELECT_VERTICAL_DIRECTION:
                return getUpAndDownAirSupplyVector(self.device.data.vertical_direction)
            case DeviceFeatureEnum.SELECT_HORIZONTAL_DIRECTION:
                return getLeftAndRightAirSupplyVector(
                    self.device.data.horizontal_direction
                )
            case DeviceFeatureEnum.SELECT_TEMPERATURE_TYPE:
                return getTemperatureType(self.device.data.temperature_type)

    def options_values(self) -> str:
        match self.deviceFeature:
            case DeviceFeatureEnum.SELECT_SLEEP_MODE:
                return [e.value for e in SleepModeEnum]
            case DeviceFeatureEnum.SELECT_MODE:
                return self.device.get_supported_modes()
            case DeviceFeatureEnum.SELECT_DEHUMIDIFIER_WIND_SPEED_LOW_MEDIUM_HEIGH:
                return [e.value for e in WindSpeedLowMediumHigh]
            case DeviceFeatureEnum.SELECT_WIND_SPEED:
                return [e.value for e in WindSeedEnum]
            case DeviceFeatureEnum.SELECT_WIND_SPEED_7_GEAR:
                return [e.value for e in WindSeed7GearEnum]
            case DeviceFeatureEnum.SELECT_PORTABLE_WIND_SPEED:
                return [e.value for e in PortableWindSeedEnum]
            case DeviceFeatureEnum.SELECT_PORTABLE_WIND_4VALUE_SPEED:
                return [e.value for e in PortableWind4ValueSeedEnum]
            case DeviceFeatureEnum.SELECT_WINDOW_AS_WIND_SPEED:
                return [e.value for e in WindowAcWindSeedEnum]
            case DeviceFeatureEnum.SELECT_GENERATOR_MODE:
                return [e.value for e in GeneratorModeEnum]
            case DeviceFeatureEnum.SELECT_FRESH_AIR:
                return [e.value for e in FreshAirEnum]
            case DeviceFeatureEnum.SELECT_WIND_FEELING:
                return [e.value for e in WindFeelingEnum]
            case DeviceFeatureEnum.SELECT_VERTICAL_DIRECTION:
                return [e.value for e in UpAndDownAirSupplyVectorEnum]
            case DeviceFeatureEnum.SELECT_HORIZONTAL_DIRECTION:
                return [e.value for e in LeftAndRightAirSupplyVectorEnum]
            case DeviceFeatureEnum.SELECT_TEMPERATURE_TYPE:
                return [e.value for e in TemperatureTypeEnum]

    async def SELECT_SLEEP_MODE(self, value: SleepModeEnum):
        desired_state = {}
        match value:
            case SleepModeEnum.STANDARD:
                desired_state = {"sleep": 1}
            case SleepModeEnum.ELDERLY:
                desired_state = {"sleep": 2}
            case SleepModeEnum.CHILD:
                desired_state = {"sleep": 3}
            case SleepModeEnum.OFF:
                desired_state = {"sleep": 0}
        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )

    async def SELECT_TEMPERATURE_TYPE(self, value: TemperatureTypeEnum):
        desired_state = {}
        match value:
            case TemperatureTypeEnum.FAHRENHEIT:
                desired_state = {"temperatureType": 1}
            case TemperatureTypeEnum.CELSIUS:
                desired_state = {"temperatureType": 0}
        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )

    async def SELECT_MODE(self, value: ModeEnum):
        stored_data = await get_stored_data(self.hass, self.device.device_id)
        memorize_temp_by_mode = safe_get_value(
            stored_data, "user_config.behavior.memorize_temp_by_mode", False
        )
        memorize_fan_speed_by_mode = safe_get_value(
            stored_data, "user_config.behavior.memorize_fan_speed_by_mode", False
        )
        memorize_humidity_by_mode = safe_get_value(
            stored_data, "user_config.behavior.memorize_humidity_by_mode", False
        )

        desired_state = {"workMode": self.device.mode_enum_to_value_mapp.get(value, 0)}
        
        desired_state = get_desired_state_for_mode_change(
            device= self.device,
            stored_data=stored_data,
            value=value,
        )

        if memorize_temp_by_mode:
            saved_target_temperature = stored_data["target_temperature"][value]["value"]
            desired_state["targetTemperature"] = saved_target_temperature
                
        if memorize_humidity_by_mode:
            saved_humidity = stored_data["humidity"][value]["value"]
            desired_state["Humidity"] = saved_humidity

        if memorize_fan_speed_by_mode:
            saved_fan_speed = stored_data["fan_speed"][value]["value"]

            desired_state_override = {}
            if DeviceFeatureEnum.SELECT_WIND_SPEED in self.device.supported_features:
                desired_state_override = self.desired_state_SELECT_WIND_SPEED(
                    saved_fan_speed
                )
            if (DeviceFeatureEnum.SELECT_PORTABLE_WIND_SPEED in self.device.supported_features):
                desired_state_override = self.desired_state_SELECT_PORTABLE_WIND_SPEED(
                    saved_fan_speed
                )
            if (DeviceFeatureEnum.SELECT_PORTABLE_WIND_4VALUE_SPEED in self.device.supported_features):
                desired_state_override = self.desired_state_SELECT_PORTABLE_WIND_4VALUE_SPEED(
                    saved_fan_speed
                )
            if (DeviceFeatureEnum.SELECT_WIND_SPEED_7_GEAR in self.device.supported_features):
                desired_state_override = self.desired_state_SELECT_WIND_SPEED_7_GEAR(
                    saved_fan_speed
                )
            if (DeviceFeatureEnum.SELECT_WINDOW_AS_WIND_SPEED in self.device.supported_features):
                desired_state_override = self.desired_state_SELECT_WINDOW_AS_WIND_SPEED(
                    saved_fan_speed
                )

            desired_state = {**desired_state, **desired_state_override}
        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )

    def desired_state_SELECT_WIND_SPEED(self, value: WindSeedEnum):
        desired_state = {}
        match value:
            case WindSeedEnum.STRONG:
                desired_state = {
                    "highTemperatureWind": 0,
                    "turbo": 1,
                    "silenceSwitch": 0,
                    "windSpeed": 6,
                }
            case WindSeedEnum.HIGH:
                desired_state = {
                    "highTemperatureWind": 0,
                    "turbo": 0,
                    "silenceSwitch": 0,
                    "windSpeed": 6,
                }
            case WindSeedEnum.MID_HIGH:
                desired_state = {
                    "highTemperatureWind": 0,
                    "turbo": 0,
                    "silenceSwitch": 0,
                    "windSpeed": 5,
                }
            case WindSeedEnum.MEDIUM:
                desired_state = {
                    "highTemperatureWind": 0,
                    "turbo": 0,
                    "silenceSwitch": 0,
                    "windSpeed": 4,
                }
            case WindSeedEnum.MID_LOW:
                desired_state = {
                    "highTemperatureWind": 0,
                    "turbo": 0,
                    "silenceSwitch": 0,
                    "windSpeed": 3,
                }
            case WindSeedEnum.LOW:
                desired_state = {
                    "highTemperatureWind": 0,
                    "turbo": 0,
                    "silenceSwitch": 0,
                    "windSpeed": 2,
                }
            case WindSeedEnum.MUTE:
                desired_state = {
                    "highTemperatureWind": 0,
                    "turbo": 0,
                    "silenceSwitch": 1,
                    "windSpeed": 2,
                }
            case WindSeedEnum.AUTO:
                desired_state = {
                    "highTemperatureWind": 0,
                    "turbo": 0,
                    "silenceSwitch": 0,
                    "windSpeed": 0,
                }
        return desired_state

    async def SELECT_WIND_SPEED(self, value: WindSeedEnum):
        stored_data = await get_stored_data(self.hass, self.device.device_id)
        mode = self.device.mode_value_to_enum_mapp.get(
            self.device.data.work_mode, ModeEnum.AUTO
        )
        stored_data, need_save = safe_set_value(
            stored_data, "fan_speed." + mode + ".value", value, overwrite_if_exists=True
        )
        if need_save:
            await set_stored_data(self.hass, self.device.device_id, stored_data)

        desired_state = self.desired_state_SELECT_WIND_SPEED(value)
        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )

    def desired_state_SELECT_WIND_SPEED_7_GEAR(self, value: WindSeed7GearEnum):
        desired_state = {}
        match value:
            case WindSeed7GearEnum.AUTO:
                desired_state = {"windSpeedAutoSwitch": 1, "windSpeed7Gear": 0}
            case WindSeed7GearEnum.TURBO:
                desired_state = {"windSpeedAutoSwitch": 0, "windSpeed7Gear": 7}
            case WindSeed7GearEnum.SPEED_1:
                desired_state = {"windSpeedAutoSwitch": 0, "windSpeed7Gear": 1}
            case WindSeed7GearEnum.SPEED_2:
                desired_state = {"windSpeedAutoSwitch": 0, "windSpeed7Gear": 2}
            case WindSeed7GearEnum.SPEED_3:
                desired_state = {"windSpeedAutoSwitch": 0, "windSpeed7Gear": 3}
            case WindSeed7GearEnum.SPEED_4:
                desired_state = {"windSpeedAutoSwitch": 0, "windSpeed7Gear": 4}
            case WindSeed7GearEnum.SPEED_5:
                desired_state = {"windSpeedAutoSwitch": 0, "windSpeed7Gear": 5}
            case WindSeed7GearEnum.SPEED_6:
                desired_state = {"windSpeedAutoSwitch": 0, "windSpeed7Gear": 6}
        return desired_state

    async def SELECT_WIND_SPEED_7_GEAR(self, value: WindSeed7GearEnum):
        stored_data = await get_stored_data(self.hass, self.device.device_id)
        mode = self.device.mode_value_to_enum_mapp.get(
            self.device.data.work_mode, ModeEnum.AUTO
        )
        stored_data, need_save = safe_set_value(
            stored_data, "fan_speed." + mode + ".value", value, overwrite_if_exists=True
        )
        if need_save:
            await set_stored_data(self.hass, self.device.device_id, stored_data)

        desired_state = self.desired_state_SELECT_WIND_SPEED_7_GEAR(value)
        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )


    def desired_state_SELECT_DEHUMIDIFIER_WIND_SPEED_LOW_MEDIUM_HEIGH(self, value: WindSpeedLowMediumHigh):
        desired_state = {}
        match value:
            case WindSpeedLowMediumHigh.LOW:
                desired_state = {"windSpeed": 0}
            case WindSpeedLowMediumHigh.MEDIUM:
                desired_state = {"windSpeed": 1}
            case WindSpeedLowMediumHigh.HIGH:
                desired_state = {"windSpeed": 2}
        return desired_state

    async def SELECT_DEHUMIDIFIER_WIND_SPEED_LOW_MEDIUM_HEIGH(self, value: WindSpeedLowMediumHigh):
        stored_data = await get_stored_data(self.hass, self.device.device_id)
        mode = self.device.mode_value_to_enum_mapp.get(
            self.device.data.work_mode, ModeEnum.AUTO
        )
        stored_data, need_save = safe_set_value(
            stored_data, "fan_speed." + mode + ".value", value, overwrite_if_exists=True
        )
        if need_save:
            await set_stored_data(self.hass, self.device.device_id, stored_data)

        desired_state = self.desired_state_SELECT_DEHUMIDIFIER_WIND_SPEED_LOW_MEDIUM_HEIGH(value)
        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )

    def desired_state_SELECT_PORTABLE_WIND_SPEED(self, value: PortableWindSeedEnum):
        desired_state = {}
        if DeviceFeatureEnum.MODE_AC_AUTO in self.device.supported_features:
            match value:
                case PortableWindSeedEnum.AUTO:
                    desired_state = {"windSpeed": 0}
                case PortableWindSeedEnum.LOW:
                    desired_state = {"windSpeed": 1}
                case PortableWindSeedEnum.HIGH:
                    desired_state = {"windSpeed": 2}
        else:
            match value:
                case PortableWindSeedEnum.LOW:
                    desired_state = {"windSpeed": 0}
                case PortableWindSeedEnum.HIGH:
                    desired_state = {"windSpeed": 1}

        return desired_state

    async def SELECT_PORTABLE_WIND_SPEED(self, value: PortableWindSeedEnum):
        stored_data = await get_stored_data(self.hass, self.device.device_id)
        mode = self.device.mode_value_to_enum_mapp.get(
            self.device.data.work_mode,
            (
                ModeEnum.AUTO
                if DeviceFeatureEnum.MODE_AC_AUTO in self.device.supported_features
                else ModeEnum.COOL
            ),
        )
        stored_data, need_save = safe_set_value(
            stored_data, "fan_speed." + mode + ".value", value, overwrite_if_exists=True
        )
        if need_save:
            await set_stored_data(self.hass, self.device.device_id, stored_data)
        desired_state = self.desired_state_SELECT_PORTABLE_WIND_SPEED(value)
        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )
    
    
    def desired_state_SELECT_PORTABLE_WIND_4VALUE_SPEED(self, value: PortableWind4ValueSeedEnum):
        desired_state = {}
        if DeviceFeatureEnum.MODE_AC_AUTO in self.device.supported_features:
            match value:
                case PortableWind4ValueSeedEnum.AUTO:
                    desired_state = {"windSpeed": 0}
                case PortableWind4ValueSeedEnum.LOW:
                    desired_state = {"windSpeed": 1}
                case PortableWind4ValueSeedEnum.MEDIUM:
                    desired_state = {"windSpeed": 2}
                case PortableWind4ValueSeedEnum.HIGH:
                    desired_state = {"windSpeed": 3}
        else:
            match value:
                case PortableWind4ValueSeedEnum.LOW:
                    desired_state = {"windSpeed": 0}
                case PortableWind4ValueSeedEnum.MEDIUM:
                    desired_state = {"windSpeed": 1}
                case PortableWind4ValueSeedEnum.HIGH:
                    desired_state = {"windSpeed": 2}

        return desired_state

    async def SELECT_PORTABLE_WIND_4VALUE_SPEED(self, value: PortableWind4ValueSeedEnum):
        stored_data = await get_stored_data(self.hass, self.device.device_id)
        mode = self.device.mode_value_to_enum_mapp.get(
            self.device.data.work_mode,
            (
                ModeEnum.AUTO
                if DeviceFeatureEnum.MODE_AC_AUTO in self.device.supported_features
                else ModeEnum.COOL
            ),
        )
        stored_data, need_save = safe_set_value(
            stored_data, "fan_speed." + mode + ".value", value, overwrite_if_exists=True
        )
        if need_save:
            await set_stored_data(self.hass, self.device.device_id, stored_data)
        desired_state = self.desired_state_SELECT_PORTABLE_WIND_4VALUE_SPEED(value)
        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )

    def desired_state_SELECT_WINDOW_AS_WIND_SPEED(self, value: WindowAcWindSeedEnum):
        desired_state = {}
        match value:
            case WindowAcWindSeedEnum.AUTO:
                desired_state = {"windSpeed": 0}
            case WindowAcWindSeedEnum.SPEED_1:
                desired_state = {"windSpeed": 2}
            case WindowAcWindSeedEnum.SPEED_2:
                desired_state = {"windSpeed": 4}
            case WindowAcWindSeedEnum.SPEED_3:
                desired_state = {"windSpeed": 6}

        return desired_state

    async def SELECT_WINDOW_AS_WIND_SPEED(self, value: PortableWindSeedEnum):
        stored_data = await get_stored_data(self.hass, self.device.device_id)
        mode = self.device.mode_value_to_enum_mapp.get(
            self.device.data.work_mode,
            (ModeEnum.AUTO),
        )
        stored_data, need_save = safe_set_value(
            stored_data, "fan_speed." + mode + ".value", value, overwrite_if_exists=True
        )
        if need_save:
            await set_stored_data(self.hass, self.device.device_id, stored_data)
        desired_state = self.desired_state_SELECT_WINDOW_AS_WIND_SPEED(value)
        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )

    async def SELECT_GENERATOR_MODE(self, value: GeneratorModeEnum):
        desired_state = {}
        match value:
            case GeneratorModeEnum.NONE:
                desired_state = {"generatorMode": 0}
            case GeneratorModeEnum.L1:
                desired_state = {"generatorMode": 1}
            case GeneratorModeEnum.L2:
                desired_state = {"generatorMode": 2}
            case GeneratorModeEnum.L3:
                desired_state = {"generatorMode": 3}
        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )

    async def SELECT_FRESH_AIR(self, value: FreshAirEnum):
        desired_state = {}
        match value:
            case FreshAirEnum.AUTO:
                desired_state = {"newWindAutoSwitch": 1, "newWindStrength": 0}
            case FreshAirEnum.STRENGTH_1:
                desired_state = {"newWindAutoSwitch": 0, "newWindStrength": 1}
            case FreshAirEnum.STRENGTH_2:
                desired_state = {"newWindAutoSwitch": 0, "newWindStrength": 2}
            case FreshAirEnum.STRENGTH_3:
                desired_state = {"newWindAutoSwitch": 0, "newWindStrength": 3}
        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )

    async def SELECT_WIND_FEELING(self, value: WindFeelingEnum):
        desired_state = {}
        match value:
            case WindFeelingEnum.NONE:
                desired_state = {"softWind": 0}
            case WindFeelingEnum.SOFT:
                desired_state = {"horizontalDirection": 8, "softWind": 1}
            case WindFeelingEnum.SHOWER:
                desired_state = {
                    "horizontalDirection": 8,
                    "softWind": 2,
                    "verticalDirection": 9,
                }
            case WindFeelingEnum.CARPET:
                desired_state = {
                    "horizontalDirection": 8,
                    "softWind": 3,
                    "verticalDirection": 13,
                }
            case WindFeelingEnum.SURROUND:
                desired_state = {"softWind": 4, "verticalDirection": 8}
        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )

    async def SELECT_VERTICAL_DIRECTION(self, value: UpAndDownAirSupplyVectorEnum):
        desired_state = {}
        has_swing_switch = (
            DeviceFeatureEnum.INTERNAL_HAS_SWING_SWITCH
            in self.device.supported_features
        )

        match value:
            case UpAndDownAirSupplyVectorEnum.UP_AND_DOWN_SWING:
                desired_state = {"verticalDirection": 1}
                if has_swing_switch:
                    desired_state["verticalSwitch"] = 1
            case UpAndDownAirSupplyVectorEnum.UPWARDS_SWING:
                desired_state = {"verticalDirection": 2}
                if has_swing_switch:
                    desired_state["verticalSwitch"] = 1
            case UpAndDownAirSupplyVectorEnum.DOWNWARDS_SWING:
                desired_state = {"verticalDirection": 3}
                if has_swing_switch:
                    desired_state["verticalSwitch"] = 1
            case UpAndDownAirSupplyVectorEnum.TOP_FIX:
                desired_state = {"verticalDirection": 9}
                if has_swing_switch:
                    desired_state["verticalSwitch"] = 0
            case UpAndDownAirSupplyVectorEnum.UPPER_FIX:
                desired_state = {"verticalDirection": 10}
                if has_swing_switch:
                    desired_state["verticalSwitch"] = 0
            case UpAndDownAirSupplyVectorEnum.MIDDLE_FIX:
                desired_state = {"verticalDirection": 11}
                if has_swing_switch:
                    desired_state["verticalSwitch"] = 0
            case UpAndDownAirSupplyVectorEnum.LOWER_FIX:
                desired_state = {"verticalDirection": 12}
                if has_swing_switch:
                    desired_state["verticalSwitch"] = 0
            case UpAndDownAirSupplyVectorEnum.BOTTOM_FIX:
                desired_state = {"verticalDirection": 13}
                if has_swing_switch:
                    desired_state["verticalSwitch"] = 0
            case UpAndDownAirSupplyVectorEnum.NOT_SET:
                desired_state = {"verticalDirection": 8}
                if has_swing_switch:
                    desired_state["verticalSwitch"] = 0
        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )

    async def SELECT_HORIZONTAL_DIRECTION(self, value: LeftAndRightAirSupplyVectorEnum):
        desired_state = {}
        has_swing_switch = (
            DeviceFeatureEnum.INTERNAL_HAS_SWING_SWITCH
            in self.device.supported_features
        )

        match value:
            case LeftAndRightAirSupplyVectorEnum.LEFT_AND_RIGHT_SWING:
                desired_state = {"horizontalDirection": 1}
                if has_swing_switch:
                    desired_state["horizontalSwitch"] = 1
            case LeftAndRightAirSupplyVectorEnum.LEFT_SWING:
                desired_state = {"horizontalDirection": 2}
                if has_swing_switch:
                    desired_state["horizontalSwitch"] = 1
            case LeftAndRightAirSupplyVectorEnum.MIDDLE_SWING:
                desired_state = {"horizontalDirection": 3}
                if has_swing_switch:
                    desired_state["horizontalSwitch"] = 1
            case LeftAndRightAirSupplyVectorEnum.RIGHT_SWING:
                desired_state = {"horizontalDirection": 4}
                if has_swing_switch:
                    desired_state["horizontalSwitch"] = 1
            case LeftAndRightAirSupplyVectorEnum.LEFT_FIX:
                desired_state = {"horizontalDirection": 9}
                if has_swing_switch:
                    desired_state["horizontalSwitch"] = 0
            case LeftAndRightAirSupplyVectorEnum.CENTER_LEFT_FIX:
                desired_state = {"horizontalDirection": 10}
                if has_swing_switch:
                    desired_state["horizontalSwitch"] = 0
            case LeftAndRightAirSupplyVectorEnum.MIDDLE_FIX:
                desired_state = {"horizontalDirection": 11}
                if has_swing_switch:
                    desired_state["horizontalSwitch"] = 0
            case LeftAndRightAirSupplyVectorEnum.CENTER_RIGHT_FIX:
                desired_state = {"horizontalDirection": 12}
                if has_swing_switch:
                    desired_state["horizontalSwitch"] = 0
            case LeftAndRightAirSupplyVectorEnum.RIGHT_FIX:
                desired_state = {"horizontalDirection": 13}
                if has_swing_switch:
                    desired_state["horizontalSwitch"] = 0
            case LeftAndRightAirSupplyVectorEnum.NOT_SET:
                desired_state = {"horizontalDirection": 8}
                if has_swing_switch:
                    desired_state["horizontalSwitch"] = 0
        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )


def get_SELECT_VERTICAL_DIRECTION_name(device: Device) -> str:
    if device.device_type == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
        return "Air flow"
    return "Up and Down air supply"

def get_SELECT_HORIZONTAL_DIRECTION_name(device: Device) -> str:
    if device.device_type == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
        return "Horizontal Air flow"
    return "Left and Right air supply"

def get_SELECT_PORTABLE_WIND_SPEED_options(device: Device) -> list[str] | None:
    all = [PortableWindSeedEnum.LOW, PortableWindSeedEnum.HIGH]
    if DeviceFeatureEnum.MODE_AC_AUTO in device.supported_features:
        all.append(PortableWindSeedEnum.AUTO)

    current_mode = device.mode_value_to_enum_mapp.get(
        device.data.work_mode, ModeEnum.COOL
    )
    if current_mode == ModeEnum.DEHUMIDIFICATION:
        if DeviceFeatureEnum.MODE_AC_AUTO in device.supported_features:
            return [PortableWindSeedEnum.AUTO]
        return []

    if current_mode == ModeEnum.FAN:
        return [PortableWindSeedEnum.LOW, PortableWindSeedEnum.HIGH]

    return all

def get_SELECT_PORTABLE_WIND_4VALUE_SPEED_options(device: Device) -> list[str] | None:
    all = [PortableWind4ValueSeedEnum.LOW, PortableWind4ValueSeedEnum.MEDIUM, PortableWind4ValueSeedEnum.HIGH]
    if DeviceFeatureEnum.MODE_AC_AUTO in device.supported_features:
        all.append(PortableWind4ValueSeedEnum.AUTO)

    current_mode = device.mode_value_to_enum_mapp.get(
        device.data.work_mode, ModeEnum.COOL
    )
    if current_mode == ModeEnum.DEHUMIDIFICATION:
        if DeviceFeatureEnum.MODE_AC_AUTO in device.supported_features:
            return [PortableWind4ValueSeedEnum.AUTO]
        return []

    if current_mode == ModeEnum.FAN:
        return [PortableWind4ValueSeedEnum.LOW, PortableWind4ValueSeedEnum.MEDIUM, PortableWind4ValueSeedEnum.HIGH]

    return all

def get_SELECT_SLEEP_MODE_available_fn(device: Device) -> str:
    mode = device.mode_value_to_enum_mapp.get(
        device.data.work_mode,
        (
            ModeEnum.AUTO
            if DeviceFeatureEnum.MODE_AC_AUTO in device.supported_features
            else ModeEnum.COOL
        ),
    )
    if (
        mode == ModeEnum.DEHUMIDIFICATION
        or mode == ModeEnum.FAN
        or mode == ModeEnum.AUTO
    ):
        return False
    return True

def get_SELECT_FRESH_AIR_available_fn(device: Device) -> str:
    if device.data.new_wind_switch == 1:
        return True
    return False

def get_SELECT_WIND_SPEED_available_fn(device: Device) -> str:
    mode = device.mode_value_to_enum_mapp.get(device.data.work_mode, ModeEnum.AUTO)
    return mode != ModeEnum.DEHUMIDIFICATION

def get_SELECT_PORTABLE_WIND_SPEED_available_fn(device: Device) -> str:
    if DeviceFeatureEnum.MODE_AC_AUTO in device.supported_features:
        return device.data.sleep != 1
    else:
        current_mode = device.mode_value_to_enum_mapp.get(
            device.data.work_mode, ModeEnum.COOL
        )
        if current_mode == ModeEnum.DEHUMIDIFICATION:
            return False
        return device.data.sleep != 1

def get_SELECT_PORTABLE_WIND_4VALUE_SPEED_available_fn(device: Device) -> str:
    if DeviceFeatureEnum.MODE_AC_AUTO in device.supported_features:
        return device.data.sleep != 1
    else:
        current_mode = device.mode_value_to_enum_mapp.get(
            device.data.work_mode, ModeEnum.COOL
        )
        if current_mode == ModeEnum.DEHUMIDIFICATION:
            return False
        return device.data.sleep != 1

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: New_NameConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Binary Sensors."""
    coordinator = config_entry.runtime_data.coordinator

    switches = []
    for device in config_entry.devices:
        if DeviceFeatureEnum.SELECT_MODE in device.supported_features:
            switches.append(
                SelectHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SELECT_MODE,
                    type="Mode",
                    name="Mode",
                    icon_fn=lambda device: "mdi:set-none",
                )
            )

        if DeviceFeatureEnum.SELECT_WIND_SPEED in device.supported_features:
            switches.append(
                DynamicSelectHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SELECT_WIND_SPEED,
                    type="WindSpeed",
                    name="Wind Speed",
                    icon_fn=lambda device: "mdi:weather-windy",
                    options_values_fn=lambda device: [e.value for e in WindSeedEnum],
                    available_fn=lambda device: get_SELECT_WIND_SPEED_available_fn(
                        device
                    ),
                )
            )
            
        if DeviceFeatureEnum.SELECT_WINDOW_AS_WIND_SPEED in device.supported_features:
            switches.append(
                SelectHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SELECT_WINDOW_AS_WIND_SPEED,
                    type="WindowAcWindSpeed",
                    name="Wind Speed",
                    icon_fn=lambda device: "mdi:weather-windy",
                )
            )

        if DeviceFeatureEnum.SELECT_DEHUMIDIFIER_WIND_SPEED_LOW_MEDIUM_HEIGH in device.supported_features:
            switches.append(
                SelectHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SELECT_DEHUMIDIFIER_WIND_SPEED_LOW_MEDIUM_HEIGH,
                    type="Dehumidifier.WindSpeed.LowMediumHeigh",
                    name="Wind Speed",
                    icon_fn=lambda device: "mdi:weather-windy",
                )
            )

        if DeviceFeatureEnum.SELECT_WIND_SPEED_7_GEAR in device.supported_features:
            switches.append(
                SelectHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SELECT_WIND_SPEED_7_GEAR,
                    type="WindSpeed7Gear",
                    name="Wind Speed",
                    icon_fn=lambda device: "mdi:weather-windy",
                )
            )

        if DeviceFeatureEnum.SELECT_PORTABLE_WIND_SPEED in device.supported_features:
            switches.append(
                DynamicSelectHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SELECT_PORTABLE_WIND_SPEED,
                    type="PortableWindSpeed",
                    name="Wind Speed",
                    icon_fn=lambda device: "mdi:weather-windy",
                    options_values_fn=lambda device: get_SELECT_PORTABLE_WIND_SPEED_options(
                        device
                    ),
                    available_fn=lambda device: get_SELECT_PORTABLE_WIND_SPEED_available_fn(
                        device
                    ),
                )
            )

        if DeviceFeatureEnum.SELECT_PORTABLE_WIND_4VALUE_SPEED in device.supported_features:
            switches.append(
                DynamicSelectHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SELECT_PORTABLE_WIND_4VALUE_SPEED,
                    type="PortableWind4ValueSpeed",
                    name="Wind Speed",
                    icon_fn=lambda device: "mdi:weather-windy",
                    options_values_fn=lambda device: get_SELECT_PORTABLE_WIND_4VALUE_SPEED_options(
                        device
                    ),
                    available_fn=lambda device: get_SELECT_PORTABLE_WIND_4VALUE_SPEED_available_fn(
                        device
                    ),
                )
            )

        if DeviceFeatureEnum.SELECT_GENERATOR_MODE in device.supported_features:
            switches.append(
                SelectHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SELECT_GENERATOR_MODE,
                    type="GeneratorMode",
                    name="Generator Mode",
                    icon_fn=lambda device: "mdi:generator-portable",
                )
            )

        if DeviceFeatureEnum.SELECT_FRESH_AIR in device.supported_features:
            switches.append(
                DynamicSelectHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SELECT_FRESH_AIR,
                    type="FreshAir",
                    name="Fresh Air Strength",
                    icon_fn=lambda device: "mdi:window-open-variant",
                    options_values_fn=lambda device: [e.value for e in FreshAirEnum],
                    available_fn=lambda device: get_SELECT_FRESH_AIR_available_fn(
                        device
                    ),
                )
            )

        if DeviceFeatureEnum.SELECT_WIND_FEELING in device.supported_features:
            switches.append(
                SelectHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SELECT_WIND_FEELING,
                    type="WindFeeling",
                    name="Wind Feeling",
                    icon_fn=lambda device: "mdi:weather-dust",
                )
            )

        if DeviceFeatureEnum.SELECT_VERTICAL_DIRECTION in device.supported_features:
            switches.append(
                SelectHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SELECT_VERTICAL_DIRECTION,
                    type="UpAndDownAirSupplyVector",
                    name=get_SELECT_VERTICAL_DIRECTION_name(device),
                    icon_fn=lambda device: "mdi:swap-vertical",
                )
            )

        if DeviceFeatureEnum.SELECT_HORIZONTAL_DIRECTION in device.supported_features:
            switches.append(
                SelectHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SELECT_HORIZONTAL_DIRECTION,
                    type="LeftAndRightAirSupplyVector",
                    name=get_SELECT_HORIZONTAL_DIRECTION_name(device),
                    icon_fn=lambda device: "mdi:swap-horizontal",
                )
            )

        if DeviceFeatureEnum.SELECT_SLEEP_MODE in device.supported_features:
            switches.append(
                DynamicSelectHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SELECT_SLEEP_MODE,
                    type="SleepMode",
                    name="Sleep Mode",
                    icon_fn=lambda device: "mdi:sleep",
                    options_values_fn=lambda device: [e.value for e in SleepModeEnum],
                    available_fn=lambda device: get_SELECT_SLEEP_MODE_available_fn(
                        device
                    ),
                )
            )

        if DeviceFeatureEnum.SELECT_TEMPERATURE_TYPE in device.supported_features:
            switches.append(
                SelectHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SELECT_TEMPERATURE_TYPE,
                    type="TemperatureType",
                    name="Temperature Type",
                    icon_fn=lambda device: "mdi:home-thermometer",
                )
            )

    async_add_entities(switches)


class SelectHandler(TclEntityBase, SelectEntity):
    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: IotDeviceCoordinator,
        device: Device,
        type: str,
        name: str,
        deviceFeature: DeviceFeatureEnum,
        icon_fn: lambda device: str,
    ) -> None:
        TclEntityBase.__init__(self, coordinator, type, name, device)

        self.icon_fn = icon_fn
        self.iot_handler = DesiredStateHandlerForSelect(
            hass=hass,
            coordinator=coordinator,
            deviceFeature=deviceFeature,
            device=self.device,
        )

        self._attr_current_option = self.iot_handler.current_state()
        self._attr_options = self.iot_handler.options_values()

    @property
    def icon(self):
        return self.icon_fn(self.device)

    @property
    def state(self):
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        self.iot_handler.refreshDevice(self.device)
        return self.iot_handler.current_state()

    async def async_select_option(self, option: str) -> None:
        await self.iot_handler.call_select_option(option)
        await self.coordinator.async_refresh()


class DynamicSelectHandler(SelectHandler, SelectEntity):
    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: IotDeviceCoordinator,
        device: Device,
        type: str,
        name: str,
        deviceFeature: DeviceFeatureEnum,
        icon_fn: lambda device: str,
        options_values_fn: lambda device: list[str] | None,
        available_fn: lambda device: bool,
    ) -> None:
        SelectHandler.__init__(
            self,
            coordinator=coordinator,
            device=device,
            type=type,
            name=name,
            deviceFeature=deviceFeature,
            hass=hass,
            icon_fn=icon_fn,
        )

        self.available_fn = available_fn
        self.options_values_fn = options_values_fn

    @property
    def options(self) -> list[str]:
        return self.options_values_fn(self.device)

    @property
    def available(self) -> bool:
        if self.device.is_online:
            return self.available_fn(self.device)
        return False
