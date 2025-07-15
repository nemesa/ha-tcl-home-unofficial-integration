"""Switch setup for our Integration."""

import logging
from typing import Any

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

from .aws_iot import AwsIot
from .config_entry import New_NameConfigEntry
from .coordinator import IotDeviceCoordinator
from .device import (
    Device,
    DeviceTypeEnum,
    TCL_SplitAC_DeviceData_Helper,
    WindSeedEnum,
    ModeEnum,
    UpAndDownAirSupplyVectorEnum,
    LeftAndRightAirSupplyVectorEnum,
)
from .tcl_entity_base import TclEntityBase

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: New_NameConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Binary Sensors."""
    coordinator = config_entry.runtime_data.coordinator

    switches = []
    for device in config_entry.devices:
        if device.device_type == DeviceTypeEnum.SPLIT_AC:
            switches.append(SplitAcClimate(coordinator, device))

    async_add_entities(switches)


def map_mode_to_hvac_mode(mode: ModeEnum) -> HVACMode:
    match mode:
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


class SplitAcClimate(TclEntityBase, ClimateEntity):
    def __init__(self, coordinator: IotDeviceCoordinator, device: Device) -> None:
        TclEntityBase.__init__(self, coordinator, "SplitAc", "Climate", device)

        self.aws_iot = coordinator.get_aws_iot()

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

        self._current_fan_mode = TCL_SplitAC_DeviceData_Helper(
            device.data
        ).getWindSpeed()
        self._fan_modes = [e.value for e in WindSeedEnum]

        self._hvac_mode = map_mode_to_hvac_mode(
            TCL_SplitAC_DeviceData_Helper(device.data).getMode()
        )
        self._hvac_modes = [map_mode_to_hvac_mode(e.value) for e in ModeEnum] + [
            HVACMode.OFF
        ]

        self._current_swing_mode = TCL_SplitAC_DeviceData_Helper(
            device.data
        ).getUpAndDownAirSupplyVector()
        self._swing_modes = [e.value for e in UpAndDownAirSupplyVectorEnum]

        self._current_swing_horizontal_mode = TCL_SplitAC_DeviceData_Helper(
            device.data
        ).getLeftAndRightAirSupplyVector()
        self._swing_horizontal_modes = [
            e.value for e in LeftAndRightAirSupplyVectorEnum
        ]

        self._hvac_action = None
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS

        self._target_temperature = self.device.data.target_temperature
        self._attr_target_temperature_step = 1
        self._attr_min_temp = 16
        self._attr_max_temp = 36

    @property
    def current_temperature(self) -> float:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        return float(self.device.data.current_temperature)

    @property
    def target_temperature(self) -> float | None:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        return float(self.device.data.target_temperature)

    @property
    def hvac_mode(self) -> HVACMode:
        """Return hvac target hvac state."""
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        if self.device.data.power_switch == 0:
            return HVACMode.OFF
        return map_mode_to_hvac_mode(
            TCL_SplitAC_DeviceData_Helper(self.device.data).getMode()
        )

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """Return the list of available operation modes."""
        return self._hvac_modes

    @property
    def fan_mode(self) -> str | None:
        """Return the fan setting."""
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        return TCL_SplitAC_DeviceData_Helper(self.device.data).getWindSpeed()

    @property
    def fan_modes(self) -> list[str]:
        """Return the list of available fan modes."""
        return self._fan_modes

    @property
    def swing_mode(self) -> str | None:
        """Return the swing setting."""
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        return TCL_SplitAC_DeviceData_Helper(
            self.device.data
        ).getUpAndDownAirSupplyVector()

    @property
    def swing_modes(self) -> list[str]:
        """List of available swing modes."""
        return self._swing_modes

    @property
    def swing_horizontal_mode(self) -> str | None:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        return TCL_SplitAC_DeviceData_Helper(
            self.device.data
        ).getLeftAndRightAirSupplyVector()

    @property
    def swing_horizontal_modes(self) -> list[str]:
        """List of available swing modes."""
        return self._swing_horizontal_modes

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperatures."""
        self._target_temperature = kwargs.get(ATTR_TEMPERATURE)
        await self.aws_iot.async_set_target_temperature(
            self.device.device_id, int(self._target_temperature)
        )
        self.device.data.target_temperature = int(self._target_temperature)
        self.coordinator.set_device(self.device)
        await self.coordinator.async_refresh()
        self.async_write_ha_state()

    async def async_set_swing_mode(self, swing_mode: str) -> None:
        await self.coordinator.get_aws_iot().async_set_up_and_down_air_supply_vector(
            self.device.device_id, swing_mode
        )
        await self.coordinator.async_refresh()

    async def async_set_swing_horizontal_mode(self, swing_horizontal_mode: str) -> None:
        await self.coordinator.get_aws_iot().async_set_left_and_right_air_supply_vector(
            self.device.device_id, swing_horizontal_mode
        )
        await self.coordinator.async_refresh()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        await self.coordinator.get_aws_iot().async_set_wind_speed(
            self.device.device_id, fan_mode
        )
        await self.coordinator.async_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.OFF:
            await self.coordinator.get_aws_iot().async_set_power(
                self.device.device_id, 0
            )
        else:
            target_temp = self.device.data.target_temperature
            await self.coordinator.get_aws_iot().async_set_power(
                self.device.device_id, 1
            )
            await self.coordinator.get_aws_iot().async_set_mode(
                self.device.device_id, map_hvac_mode_tcl_mode(hvac_mode)
            )

            if self.coordinator.get_config_data().behavior_keep_target_temperature_at_cliet_mode_change:
                await self.aws_iot.async_set_target_temperature(
                    self.device.device_id, int(target_temp)
                )

        await self.coordinator.async_refresh()
