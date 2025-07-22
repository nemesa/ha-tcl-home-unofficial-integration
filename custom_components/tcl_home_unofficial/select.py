"""Switch setup for our Integration."""

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .config_entry import New_NameConfigEntry
from .coordinator import IotDeviceCoordinator
from .device import (
    Device,
    DeviceFeature,
    DeviceTypeEnum,
    get_supported_modes,
    getSupportedFeatures,
)
from .device_ac_common import (
    LeftAndRightAirSupplyVectorEnum,
    SleepModeEnum,
    UpAndDownAirSupplyVectorEnum,
    ModeEnum,
    getMode,
    WindSeed7GearEnum,
    getWindSeed7Gear,
)
from .device_portable_ac import (
    PortableWindSeedEnum,
    TCL_PortableAC_DeviceData_Helper,
    TemperatureTypeEnum,
)
from .device_spit_ac_type1 import TCL_SplitAC_Type1_DeviceData_Helper, WindSeedEnum
from .device_spit_ac_fresh_air import (
    FreshAirEnum,
    GeneratorModeEnum,
    TCL_SplitAC_Fresh_Air_DeviceData_Helper,
    WindFeelingEnum,
)
from .tcl_entity_base import TclEntityBase
from .device_data_storage import (
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
        deviceFeature: DeviceFeature,
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
            case DeviceFeature.SELECT_SLEEP_MODE:
                return await self.SELECT_SLEEP_MODE(value=value)
            case DeviceFeature.SELECT_MODE:
                return await self.SELECT_MODE(value=value)
            case DeviceFeature.SELECT_WIND_SPEED:
                return await self.SELECT_WIND_SPEED(value=value)
            case DeviceFeature.SELECT_WIND_SPEED_7_GEAR:
                return await self.SELECT_WIND_SPEED_7_GEAR(value=value)
            case DeviceFeature.SELECT_PORTABLE_WIND_SEED:
                return await self.SELECT_PORTABLE_WIND_SEED(value=value)
            case DeviceFeature.SELECT_GENERATOR_MODE:
                return await self.SELECT_GENERATOR_MODE(value=value)
            case DeviceFeature.SELECT_WIND_FEELING:
                return await self.SELECT_WIND_FEELING(value=value)
            case DeviceFeature.SELECT_VERTICAL_DIRECTION:
                return await self.SELECT_VERTICAL_DIRECTION(value=value)
            case DeviceFeature.SELECT_HORIZONTAL_DIRECTION:
                return await self.SELECT_HORIZONTAL_DIRECTION(value=value)
            case DeviceFeature.SELECT_TEMPERATURE_TYPE:
                return await self.SELECT_TEMPERATURE_TYPE(value=value)

    def current_state(self) -> str:
        match self.deviceFeature:
            case DeviceFeature.SELECT_SLEEP_MODE:
                return TCL_SplitAC_Type1_DeviceData_Helper(
                    self.device.data
                ).getSleepMode()
            case DeviceFeature.SELECT_MODE:
                return TCL_SplitAC_Type1_DeviceData_Helper(self.device.data).getMode()
            case DeviceFeature.SELECT_WIND_SPEED:
                return TCL_SplitAC_Type1_DeviceData_Helper(
                    self.device.data
                ).getWindSpeed()
            case DeviceFeature.SELECT_WIND_SPEED_7_GEAR:
                return getWindSeed7Gear(self.device.data.wind_speed_7_gear)
            case DeviceFeature.SELECT_PORTABLE_WIND_SEED:
                return TCL_PortableAC_DeviceData_Helper(self.device.data).getWindSpeed()
            case DeviceFeature.SELECT_GENERATOR_MODE:
                return TCL_SplitAC_Fresh_Air_DeviceData_Helper(
                    self.device.data
                ).getGeneratorMode()
            case DeviceFeature.SELECT_FRESH_AIR:
                return TCL_SplitAC_Fresh_Air_DeviceData_Helper(
                    self.device.data
                ).getFreshAir()
            case DeviceFeature.SELECT_WIND_FEELING:
                return TCL_SplitAC_Fresh_Air_DeviceData_Helper(
                    self.device.data
                ).getWindFeeling()
            case DeviceFeature.SELECT_VERTICAL_DIRECTION:
                return TCL_SplitAC_Type1_DeviceData_Helper(
                    self.device.data
                ).getUpAndDownAirSupplyVector()
            case DeviceFeature.SELECT_HORIZONTAL_DIRECTION:
                return TCL_SplitAC_Type1_DeviceData_Helper(
                    self.device.data
                ).getLeftAndRightAirSupplyVector()
            case DeviceFeature.SELECT_TEMPERATURE_TYPE:
                return TCL_PortableAC_DeviceData_Helper(
                    self.device.data
                ).getTemperatureType()

    def options_values(self) -> str:
        match self.deviceFeature:
            case DeviceFeature.SELECT_SLEEP_MODE:
                return [e.value for e in SleepModeEnum]
            case DeviceFeature.SELECT_MODE:
                return get_supported_modes(self.device)
            case DeviceFeature.SELECT_WIND_SPEED:
                return [e.value for e in WindSeedEnum]
            case DeviceFeature.SELECT_WIND_SPEED_7_GEAR:
                return [e.value for e in WindSeed7GearEnum]
            case DeviceFeature.SELECT_PORTABLE_WIND_SEED:
                return [e.value for e in PortableWindSeedEnum]
            case DeviceFeature.SELECT_GENERATOR_MODE:
                return [e.value for e in GeneratorModeEnum]
            case DeviceFeature.SELECT_FRESH_AIR:
                return [e.value for e in FreshAirEnum]
            case DeviceFeature.SELECT_WIND_FEELING:
                return [e.value for e in WindFeelingEnum]
            case DeviceFeature.SELECT_VERTICAL_DIRECTION:
                return [e.value for e in UpAndDownAirSupplyVectorEnum]
            case DeviceFeature.SELECT_HORIZONTAL_DIRECTION:
                return [e.value for e in LeftAndRightAirSupplyVectorEnum]
            case DeviceFeature.SELECT_TEMPERATURE_TYPE:
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

        desired_state = {}
        match value:
            case ModeEnum.AUTO:
                if self.device.device_type == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired_state = {
                        "windSpeedAutoSwitch": 1,
                        "workMode": 0,
                        "windSpeed7Gear": 0,
                    }
                elif self.device.device_type == DeviceTypeEnum.PORTABLE_AC:
                    desired_state = {"sleep": 0, "workMode": 0, "windSpeed": 0}
                elif self.device.device_type == DeviceTypeEnum.SPLIT_AC_TYPE_2:
                    desired_state = {
                        "eightAddHot": 0,
                        "workMode": 0,
                        "windSpeed7Gear": 0,
                    }
                else:
                    desired_state = {
                        "ECO": 0,
                        "sleep": 0,
                        "eightAddHot": 0,
                        "highTemperatureWind": 0,
                        "workMode": 0,
                        "horizontalSwitch": 0,
                        "healthy": 0,
                        "turbo": 0,
                        "antiMoldew": 0,
                        "verticalSwitch": 0,
                        "silenceSwitch": 0,
                        "windSpeed": 0,
                    }
            case ModeEnum.COOL:
                if self.device.device_type == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired_state = {
                        "windSpeedAutoSwitch": 0,
                        "workMode": 1,
                        "windSpeed7Gear": 6,
                    }
                elif self.device.device_type == DeviceTypeEnum.PORTABLE_AC:
                    targetCelsiusDegree = stored_data["target_temperature"][
                        ModeEnum.COOL
                    ]["targetCelsiusDegree"]
                    targetFahrenheitDegree = stored_data["target_temperature"][
                        ModeEnum.COOL
                    ]["targetFahrenheitDegree"]

                    desired_state = {
                        "sleep": 0,
                        "workMode": 1,
                        "windSpeed": 2,
                        "targetCelsiusDegree": targetCelsiusDegree,
                        "targetFahrenheitDegree": targetFahrenheitDegree,
                    }
                elif self.device.device_type == DeviceTypeEnum.SPLIT_AC_TYPE_2:
                    desired_state = {
                        "eightAddHot": 0,
                        "workMode": 1,
                    }
                else:
                    desired_state = {
                        "ECO": 0,
                        "sleep": 0,
                        "eightAddHot": 0,
                        "highTemperatureWind": 0,
                        "workMode": 1,
                        "horizontalSwitch": 0,
                        "healthy": 0,
                        "turbo": 0,
                        "antiMoldew": 0,
                        "verticalSwitch": 0,
                        "silenceSwitch": 0,
                        "windSpeed": 0,
                        "targetTemperature": 24,
                    }
            case ModeEnum.DEHUMIDIFICATION:
                if self.device.device_type == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired_state = {
                        "windSpeedAutoSwitch": 0,
                        "workMode": 2,
                        "windSpeed7Gear": 2,
                    }
                elif self.device.device_type == DeviceTypeEnum.PORTABLE_AC:
                    desired_state = {"sleep": 0, "workMode": 2, "windSpeed": 0}
                elif self.device.device_type == DeviceTypeEnum.SPLIT_AC_TYPE_2:
                    desired_state = {
                        "eightAddHot": 0,
                        "workMode": 2,
                    }
                else:
                    desired_state = {
                        "ECO": 0,
                        "sleep": 0,
                        "eightAddHot": 0,
                        "highTemperatureWind": 0,
                        "workMode": 2,
                        "horizontalSwitch": 0,
                        "healthy": 0,
                        "turbo": 0,
                        "antiMoldew": 0,
                        "verticalSwitch": 0,
                        "silenceSwitch": 0,
                        "windSpeed": 2,
                    }
            case ModeEnum.FAN:
                if self.device.device_type == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired_state = {
                        "windSpeedAutoSwitch": 1,
                        "workMode": 3,
                        "windSpeed7Gear": 0,
                    }
                elif self.device.device_type == DeviceTypeEnum.PORTABLE_AC:
                    desired_state = {"sleep": 0, "workMode": 3, "windSpeed": 1}
                elif self.device.device_type == DeviceTypeEnum.SPLIT_AC_TYPE_2:
                    desired_state = {
                        "eightAddHot": 0,
                        "workMode": 3,
                    }
                else:
                    desired_state = {
                        "ECO": 0,
                        "sleep": 0,
                        "eightAddHot": 0,
                        "highTemperatureWind": 0,
                        "workMode": 3,
                        "horizontalSwitch": 0,
                        "healthy": 0,
                        "turbo": 0,
                        "antiMoldew": 0,
                        "verticalSwitch": 0,
                        "silenceSwitch": 0,
                        "windSpeed": 0,
                    }
            case ModeEnum.HEAT:
                if self.device.device_type == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired_state = {
                        "windSpeedAutoSwitch": 1,
                        "workMode": 4,
                        "windSpeed7Gear": 0,
                    }
                elif self.device.device_type == DeviceTypeEnum.SPLIT_AC_TYPE_2:
                    desired_state = {
                        "eightAddHot": 0,
                        "workMode": 4,
                    }
                else:
                    desired_state = {
                        "ECO": 0,
                        "sleep": 0,
                        "eightAddHot": 0,
                        "highTemperatureWind": 0,
                        "workMode": 4,
                        "horizontalSwitch": 0,
                        "healthy": 0,
                        "turbo": 0,
                        "antiMoldew": 0,
                        "verticalSwitch": 0,
                        "silenceSwitch": 0,
                        "windSpeed": 0,
                        "targetTemperature": 26,
                    }

        if memorize_temp_by_mode:
            saved_target_temperature = stored_data["target_temperature"][value]["value"]
            desired_state["targetTemperature"] = saved_target_temperature

        if memorize_fan_speed_by_mode:
            saved_fan_speed = stored_data["fan_speed"][value]["value"]
            match self.device.device_type:
                case DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired_state = {
                        **desired_state,
                        **self.desired_state_SELECT_WIND_SPEED_7_GEAR(saved_fan_speed),
                    }
                case DeviceTypeEnum.SPLIT_AC_TYPE_2:
                    desired_state = {
                        **desired_state,
                        **self.desired_state_SELECT_WIND_SPEED_7_GEAR(saved_fan_speed),
                    }
                case DeviceTypeEnum.SPLIT_AC_TYPE_1:
                    new_ds = self.desired_state_SELECT_WIND_SPEED(saved_fan_speed)
                    desired_state = {
                        **desired_state,
                        **new_ds,
                    }
                case DeviceTypeEnum.PORTABLE_AC:
                    desired_state = {
                        **desired_state,
                        **self.desired_state_SELECT_PORTABLE_WIND_SEED(saved_fan_speed),
                    }
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
            case WindSeedEnum.HEIGH:
                desired_state = {
                    "highTemperatureWind": 0,
                    "turbo": 0,
                    "silenceSwitch": 0,
                    "windSpeed": 6,
                }
            case WindSeedEnum.MID_HEIGH:
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
        mode = getMode(self.device.data.work_mode)
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
        mode = getMode(self.device.data.work_mode)
        stored_data, need_save = safe_set_value(
            stored_data, "fan_speed." + mode + ".value", value, overwrite_if_exists=True
        )
        if need_save:
            await set_stored_data(self.hass, self.device.device_id, stored_data)

        desired_state = self.desired_state_SELECT_WIND_SPEED_7_GEAR(value)
        return await self.coordinator.get_aws_iot().async_set_desired_state(
            self.device.device_id, desired_state
        )

    def desired_state_SELECT_PORTABLE_WIND_SEED(self, value: PortableWindSeedEnum):
        desired_state = {}
        match value:
            case PortableWindSeedEnum.AUTO:
                desired_state = {"windSpeed": 0}
            case PortableWindSeedEnum.LOW:
                desired_state = {"windSpeed": 1}
            case PortableWindSeedEnum.HEIGH:
                desired_state = {"windSpeed": 2}
        return desired_state

    async def SELECT_PORTABLE_WIND_SEED(self, value: PortableWindSeedEnum):
        stored_data = await get_stored_data(self.hass, self.device.device_id)
        mode = getMode(self.device.data.work_mode)
        stored_data, need_save = safe_set_value(
            stored_data, "fan_speed." + mode + ".value", value, overwrite_if_exists=True
        )
        if need_save:
            await set_stored_data(self.hass, self.device.device_id, stored_data)
        desired_state = self.desired_state_SELECT_PORTABLE_WIND_SEED(value)
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
            case FreshAirEnum.OFF:
                desired_state = {"newWindSwitch": 0}
            case FreshAirEnum.ON:
                desired_state = {"newWindSwitch": 1, "selfClean": 0}
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
        supported_features = getSupportedFeatures(self.device.device_type)
        has_swing_switch = DeviceFeature.INTERNAL_HAS_SWING_SWITCH in supported_features

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
        supported_features = getSupportedFeatures(self.device.device_type)
        has_swing_switch = DeviceFeature.INTERNAL_HAS_SWING_SWITCH in supported_features

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


def get_portable_ac_wind_speed_options(device: Device) -> list[str] | None:
    current_mode = getMode(device.data.work_mode)
    if current_mode == ModeEnum.DEHUMIDIFICATION:
        return [PortableWindSeedEnum.AUTO]

    if current_mode == ModeEnum.FAN:
        return [PortableWindSeedEnum.LOW, PortableWindSeedEnum.HEIGH]

    return [e.value for e in PortableWindSeedEnum]


def get_SELECT_SLEEP_MODE_available_fn(device: Device) -> str:
    mode = getMode(device.data.work_mode)
    if (
        mode == ModeEnum.DEHUMIDIFICATION
        or mode == ModeEnum.FAN
        or mode == ModeEnum.AUTO
    ):
        return False
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: New_NameConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Binary Sensors."""
    coordinator = config_entry.runtime_data.coordinator

    switches = []
    for device in config_entry.devices:
        supported_features = getSupportedFeatures(device.device_type)

        if DeviceFeature.SELECT_MODE in supported_features:
            switches.append(
                SelectHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeature.SELECT_MODE,
                    type="Mode",
                    name="Mode",
                    icon_fn=lambda device: "mdi:set-none",
                )
            )

        if DeviceFeature.SELECT_WIND_SPEED in supported_features:
            switches.append(
                DynamicSelectHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeature.SELECT_WIND_SPEED,
                    type="WindSpeed",
                    name="Wind Speed",
                    icon_fn=lambda device: "mdi:weather-windy",
                    options_values_fn=lambda device: [e.value for e in WindSeedEnum],
                    available_fn=lambda device: getMode(device.data.work_mode)
                    != ModeEnum.DEHUMIDIFICATION,
                )
            )

        if DeviceFeature.SELECT_WIND_SPEED_7_GEAR in supported_features:
            switches.append(
                SelectHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeature.SELECT_WIND_SPEED_7_GEAR,
                    type="WindSpeed7Gear",
                    name="Wind Speed",
                    icon_fn=lambda device: "mdi:weather-windy",
                )
            )

        if DeviceFeature.SELECT_PORTABLE_WIND_SEED in supported_features:
            switches.append(
                DynamicSelectHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeature.SELECT_PORTABLE_WIND_SEED,
                    type="PortableWindSpeed",
                    name="Wind Speed",
                    icon_fn=lambda device: "mdi:weather-windy",
                    options_values_fn=lambda device: get_portable_ac_wind_speed_options(
                        device
                    ),
                    available_fn=lambda device: device.data.sleep != 1,
                )
            )

        if DeviceFeature.SELECT_GENERATOR_MODE in supported_features:
            switches.append(
                SelectHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeature.SELECT_GENERATOR_MODE,
                    type="GeneratorMode",
                    name="Generator Mode",
                    icon_fn=lambda device: "mdi:generator-portable",
                )
            )

        if DeviceFeature.SELECT_FRESH_AIR in supported_features:
            switches.append(
                SelectHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeature.SELECT_FRESH_AIR,
                    type="FreshAir",
                    name="Fresh Air",
                    icon_fn=lambda device: "mdi:window-open-variant",
                )
            )

        if DeviceFeature.SELECT_WIND_FEELING in supported_features:
            switches.append(
                SelectHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeature.SELECT_WIND_FEELING,
                    type="WindFeeling",
                    name="Wind Feeling",
                    icon_fn=lambda device: "mdi:weather-dust",
                )
            )

        if DeviceFeature.SELECT_VERTICAL_DIRECTION in supported_features:
            switches.append(
                SelectHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeature.SELECT_VERTICAL_DIRECTION,
                    type="UpAndDownAirSupplyVector",
                    name=get_SELECT_VERTICAL_DIRECTION_name(device),
                    icon_fn=lambda device: "mdi:swap-vertical",
                )
            )

        if DeviceFeature.SELECT_HORIZONTAL_DIRECTION in supported_features:
            switches.append(
                SelectHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeature.SELECT_HORIZONTAL_DIRECTION,
                    type="LeftAndRightAirSupplyVector",
                    name=get_SELECT_HORIZONTAL_DIRECTION_name(device),
                    icon_fn=lambda device: "mdi:swap-horizontal",
                )
            )

        if DeviceFeature.SELECT_SLEEP_MODE in supported_features:
            switches.append(
                DynamicSelectHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeature.SELECT_SLEEP_MODE,
                    type="SleepMode",
                    name="Sleep Mode",
                    icon_fn=lambda device: "mdi:sleep",
                    options_values_fn=lambda device: [e.value for e in SleepModeEnum],
                    available_fn=lambda device: get_SELECT_SLEEP_MODE_available_fn(
                        device
                    ),
                )
            )

        if DeviceFeature.SELECT_TEMPERATURE_TYPE in supported_features:
            switches.append(
                SelectHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeature.SELECT_TEMPERATURE_TYPE,
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
        deviceFeature: DeviceFeature,
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
        deviceFeature: DeviceFeature,
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
        return self.available_fn(self.device)
