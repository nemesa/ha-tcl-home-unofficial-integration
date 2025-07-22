"""Switch setup for our Integration."""

import logging
from typing import Any
# import asyncio

from homeassistant.components.climate import (
    ATTR_HVAC_MODE,
    ATTR_TARGET_TEMP_HIGH,
    ATTR_TARGET_TEMP_LOW,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .config_entry import New_NameConfigEntry
from .coordinator import IotDeviceCoordinator
from .device import (
    Device,
    DeviceFeature,
    DeviceTypeEnum,
    getSupportedFeatures,
    get_supported_modes,
)
from .device_ac_common import (
    LeftAndRightAirSupplyVectorEnum,
    ModeEnum,
    UpAndDownAirSupplyVectorEnum,
    getMode,
)
from .device_spit_ac_type1 import TCL_SplitAC_Type1_DeviceData_Helper, WindSeedEnum
from .device_spit_ac_fresh_air import (
    TCL_SplitAC_Fresh_Air_DeviceData_Helper,
    WindSeed7GearEnum,
)
from .tcl_entity_base import TclEntityBase
from .select import DesiredStateHandlerForSelect
from .number import DesiredStateHandlerForNumber

_LOGGER = logging.getLogger(__name__)


def SWITCH_POWER_fn(
    coordinator: IotDeviceCoordinator, device: Device, value: int
) -> str:
    # turnOffBeep = coordinator.get_config_data().behavior_mute_beep_on_power_on
    desired_state = {"powerSwitch": value}
    # if turnOffBeep and value == 1:
    #    desired_state["beepSwitch"] = 0

    return coordinator.get_aws_iot().async_set_desired_state(
        device.device_id, desired_state
    )


def get_fan_seepd_feature(device: Device) -> str:
    supported_features = getSupportedFeatures(device.device_type)
    if DeviceFeature.SELECT_WIND_SPEED_7_GEAR in supported_features:
        return DeviceFeature.SELECT_WIND_SPEED_7_GEAR
    return DeviceFeature.SELECT_WIND_SPEED


def get_current_fan_speed_fn(device: Device) -> str:
    supported_features = getSupportedFeatures(device.device_type)
    if DeviceFeature.SELECT_WIND_SPEED_7_GEAR in supported_features:
        return TCL_SplitAC_Fresh_Air_DeviceData_Helper(device.data).getWindSeed7Gear()
    return TCL_SplitAC_Type1_DeviceData_Helper(device.data).getWindSpeed()


def get_options_fan_speed(device: Device) -> list[str]:
    supported_features = getSupportedFeatures(device.device_type)
    if DeviceFeature.SELECT_WIND_SPEED_7_GEAR in supported_features:
        return [e.value for e in WindSeed7GearEnum]
    return [e.value for e in WindSeedEnum]


def get_current_mode_fn(device: Device) -> str:
    if device.data.power_switch == 0:
        return "OFF"
    return getMode(device.data.work_mode)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: New_NameConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Binary Sensors."""
    coordinator = config_entry.runtime_data.coordinator

    climates = []
    for device in config_entry.devices:
        supported_features = getSupportedFeatures(device.device_type)

        if DeviceFeature.CLIMATE in supported_features:
            climates.append(
                ClimateHandler(
                    hass=hass,
                    coordinator=coordinator,
                    device=device,
                    type="ClimateControll"
                    if device.device_type == DeviceTypeEnum.SPLIT_AC_FRESH_AIR
                    else "SplitAc",
                    name="Climate",
                    mode_select_feature=DeviceFeature.SELECT_MODE,
                    temperature_set_feature=DeviceFeature.NUMBER_TARGET_TEMPERATURE,
                    vertical_air_direction_select_feature=DeviceFeature.SELECT_VERTICAL_DIRECTION,
                    horizontal_air_direction_select_feature=DeviceFeature.SELECT_HORIZONTAL_DIRECTION,
                    fan_speed_select_feature=get_fan_seepd_feature(device),
                    current_fan_speed_fn=lambda device: get_current_fan_speed_fn(
                        device
                    ),
                    current_mode_fn=lambda device: map_mode_to_hvac_mode(
                        get_current_mode_fn(device)
                    ),
                    current_vertical_air_direction_fn=lambda device: TCL_SplitAC_Fresh_Air_DeviceData_Helper(
                        device.data
                    ).getUpAndDownAirSupplyVector(),
                    current_horizontal_air_direction_fn=lambda device: TCL_SplitAC_Fresh_Air_DeviceData_Helper(
                        device.data
                    ).getLeftAndRightAirSupplyVector(),
                    options_fan_speed=get_options_fan_speed(device),
                    options_mode=[
                        map_mode_to_hvac_mode(e) for e in get_supported_modes(device)
                    ],
                    options_vertical_air_direction=[
                        e.value for e in UpAndDownAirSupplyVectorEnum
                    ],
                    options_horizontal_air_direction=[
                        e.value for e in LeftAndRightAirSupplyVectorEnum
                    ],
                    current_target_temp_fn=lambda device: device.data.target_temperature,
                    current_temp_fn=lambda device: device.data.current_temperature,
                )
            )

    async_add_entities(climates)


def map_mode_to_hvac_mode(mode: ModeEnum) -> HVACMode:
    match mode:
        case "OFF":
            return HVACMode.OFF
        case ModeEnum.AUTO:
            return HVACMode.AUTO
        case ModeEnum.COOL:
            return HVACMode.COOL
        case ModeEnum.DEHUMIDIFICATION:
            return HVACMode.DRY
        case ModeEnum.FAN:
            return HVACMode.FAN_ONLY
        case ModeEnum.HEAT:
            return HVACMode.HEAT
        case _:
            return HVACMode.AUTO


def map_hvac_mode_tcl_mode(mode: HVACMode) -> ModeEnum:
    match mode:
        case HVACMode.AUTO:
            return ModeEnum.AUTO
        case HVACMode.COOL:
            return ModeEnum.COOL
        case HVACMode.DRY:
            return ModeEnum.DEHUMIDIFICATION
        case HVACMode.FAN_ONLY:
            return ModeEnum.FAN
        case HVACMode.HEAT:
            return ModeEnum.HEAT
        case _:
            return ModeEnum.AUTO


class ClimateHandler(TclEntityBase, ClimateEntity):
    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: IotDeviceCoordinator,
        device: Device,
        type: str,
        name: str,
        mode_select_feature: str,
        vertical_air_direction_select_feature: str,
        horizontal_air_direction_select_feature: str,
        fan_speed_select_feature: str,
        temperature_set_feature: str,
        current_target_temp_fn=lambda device: int | float,
        current_temp_fn=lambda device: int | float,
        current_fan_speed_fn=lambda device: str,
        current_mode_fn=lambda device: str,
        current_vertical_air_direction_fn=lambda device: str,
        current_horizontal_air_direction_fn=lambda device: str,
        options_fan_speed=list[str],
        options_vertical_air_direction=list[str],
        options_horizontal_air_direction=list[str],
        options_mode=list[str],
    ) -> None:
        TclEntityBase.__init__(self, coordinator, type, name, device)

        self.current_target_temp_fn = current_target_temp_fn
        self.current_temp_fn = current_temp_fn
        self.current_fan_speed_fn = current_fan_speed_fn
        self.current_mode_fn = current_mode_fn
        self.current_vertical_air_direction_fn = current_vertical_air_direction_fn
        self.current_horizontal_air_direction_fn = current_horizontal_air_direction_fn

        self.iot_handler_mode = DesiredStateHandlerForSelect(
            hass=hass,
            coordinator=coordinator,
            device=device,
            deviceFeature=mode_select_feature,
        )

        self.iot_handler_temp = DesiredStateHandlerForNumber(
            hass=hass,
            coordinator=coordinator,
            device=device,
            deviceFeature=temperature_set_feature,
        )

        self.iot_handler_vertical_air_direction = DesiredStateHandlerForSelect(
            hass=hass,
            coordinator=coordinator,
            device=device,
            deviceFeature=vertical_air_direction_select_feature,
        )

        self.iot_handler_horizontal_air_direction = DesiredStateHandlerForSelect(
            hass=hass,
            coordinator=coordinator,
            device=device,
            deviceFeature=horizontal_air_direction_select_feature,
        )

        self.iot_handler_wind_speed = DesiredStateHandlerForSelect(
            hass=hass,
            coordinator=coordinator,
            device=device,
            deviceFeature=fan_speed_select_feature,
        )

        self._attr_supported_features = ClimateEntityFeature(0)
        self._attr_supported_features |= ClimateEntityFeature.TARGET_TEMPERATURE
        self._attr_supported_features |= ClimateEntityFeature.FAN_MODE
        self._attr_supported_features |= ClimateEntityFeature.SWING_MODE
        self._attr_supported_features |= ClimateEntityFeature.SWING_HORIZONTAL_MODE
        self._attr_supported_features |= (
            ClimateEntityFeature.TURN_OFF | ClimateEntityFeature.TURN_ON
        )

        self._target_humidity = None
        self._unit_of_measurement = UnitOfTemperature.CELSIUS
        self._preset = None
        self._preset_modes = None
        self._current_humidity = None

        self._current_fan_mode = self.current_fan_speed_fn(device)
        self._fan_modes = options_fan_speed

        self._hvac_mode = self.current_mode_fn(device)
        self._hvac_modes = options_mode + [HVACMode.OFF]

        self._current_swing_mode = self.current_vertical_air_direction_fn(device)
        self._swing_modes = options_vertical_air_direction

        self._current_swing_horizontal_mode = self.current_horizontal_air_direction_fn(
            device
        )
        self._swing_horizontal_modes = options_horizontal_air_direction

        self._hvac_action = None
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS

        self._target_temperature = self.current_target_temp_fn(device)
        self._attr_min_temp = self.device.storage["non_user_config"]["min_celsius_temp"]
        self._attr_max_temp = self.device.storage["non_user_config"]["max_celsius_temp"]
        self._attr_target_temperature_step = self.device.storage["non_user_config"][
            "native_temp_step"
        ]

    def refresh_device(self) -> None:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        self.iot_handler_mode.refreshDevice(self.device)
        self.iot_handler_temp.refreshDevice(self.device)
        self.iot_handler_vertical_air_direction.refreshDevice(self.device)
        self.iot_handler_horizontal_air_direction.refreshDevice(self.device)
        self.iot_handler_wind_speed.refreshDevice(self.device)

    @property
    def current_temperature(self) -> float:
        self.refresh_device()
        return float(self.current_temp_fn(self.device))

    @property
    def target_temperature(self) -> float | None:
        self.refresh_device()
        return float(self.current_target_temp_fn(self.device))

    @property
    def hvac_mode(self) -> HVACMode:
        self.refresh_device()
        return self.current_mode_fn(self.device)

    @property
    def hvac_modes(self) -> list[HVACMode]:
        return self._hvac_modes

    @property
    def fan_mode(self) -> str | None:
        self.refresh_device()
        return self.current_fan_speed_fn(self.device)

    @property
    def fan_modes(self) -> list[str]:
        return self._fan_modes

    @property
    def swing_mode(self) -> str | None:
        self.refresh_device()
        return self.current_vertical_air_direction_fn(self.device)

    @property
    def swing_modes(self) -> list[str]:
        return self._swing_modes

    @property
    def swing_horizontal_mode(self) -> str | None:
        self.refresh_device()
        return self.current_horizontal_air_direction_fn(self.device)

    @property
    def swing_horizontal_modes(self) -> list[str]:
        return self._swing_horizontal_modes

    async def async_set_temperature(self, **kwargs: Any) -> None:
        self.refresh_device()

        value = kwargs.get(ATTR_TEMPERATURE)
        await self.iot_handler_temp.call_set_number(value)
        await self.iot_handler_temp.store_target_temp(value)
        await self.coordinator.async_refresh()
        self.async_write_ha_state()

    async def async_set_swing_mode(self, swing_mode: str) -> None:
        await self.iot_handler_vertical_air_direction.call_select_option(swing_mode)
        await self.coordinator.async_refresh()

    async def async_set_swing_horizontal_mode(self, swing_horizontal_mode: str) -> None:
        await self.iot_handler_horizontal_air_direction.call_select_option(
            swing_horizontal_mode
        )
        await self.coordinator.async_refresh()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        await self.iot_handler_wind_speed.call_select_option(fan_mode)
        await self.coordinator.async_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.OFF:
            await SWITCH_POWER_fn(self.coordinator, self.device, 0)
        else:
            target_temp = self.device.data.target_temperature
            await SWITCH_POWER_fn(self.coordinator, self.device, 1)
            await self.iot_handler_mode.call_select_option(
                map_hvac_mode_tcl_mode(hvac_mode)
            )

            if self.coordinator.get_config_data().behavior_keep_target_temperature_at_cliet_mode_change:
                await self.iot_handler_temp.call_set_number(target_temp)

        await self.coordinator.async_refresh()

    async def async_turn_on(self) -> None:
        await SWITCH_POWER_fn(self.coordinator, self.device, 1)
        await self.coordinator.async_refresh()

    async def async_turn_off(self) -> None:
        await SWITCH_POWER_fn(self.coordinator, self.device, 0)
        await self.coordinator.async_refresh()
