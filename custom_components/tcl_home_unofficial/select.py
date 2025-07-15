"""Switch setup for our Integration."""

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .config_entry import New_NameConfigEntry
from .coordinator import IotDeviceCoordinator
from .device_spit_ac import TCL_SplitAC_DeviceData_Helper
from .device_ac_common import (
    LeftAndRightAirSupplyVectorEnum,
    UpAndDownAirSupplyVectorEnum,
    ModeEnum,
    SleepModeEnum,
    WindSeedEnum,
)
from .device import (
    Device,
    getSupportedFeatures,
    DeviceFeature
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
        supported_features = getSupportedFeatures(device.device_type)
                
        if DeviceFeature.SELECT_MODE in supported_features:
            switches.append(
                Select(
                    coordinator=coordinator,
                    device=device,
                    type="Mode",
                    name="Mode",
                    icon_fn=lambda device: "mdi:set-none",
                    current_state_fn=lambda device: TCL_SplitAC_DeviceData_Helper(
                        device.data
                    ).getMode(),
                    options_values=[e.value for e in ModeEnum],
                    select_option_fn=lambda device,
                    option: coordinator.get_aws_iot().async_set_mode(
                        device.device_id, option
                    ),
                )
            )
            
        if DeviceFeature.SELECT_WIND_SPEED in supported_features:
            switches.append(
                Select(
                    coordinator=coordinator,
                    device=device,
                    type="WindSpeed",
                    name="Wind Speed",
                    icon_fn=lambda device: "mdi:weather-windy",
                    current_state_fn=lambda device: TCL_SplitAC_DeviceData_Helper(
                        device.data
                    ).getWindSpeed(),
                    options_values=[e.value for e in WindSeedEnum],
                    select_option_fn=lambda device,
                    option: coordinator.get_aws_iot().async_set_wind_speed(
                        device.device_id, option
                    ),
                )
            )
            
        if DeviceFeature.SELECT_VERTICAL_DIRECTION in supported_features:
            switches.append(
                Select(
                    coordinator=coordinator,
                    device=device,
                    type="UpAndDownAirSupplyVector",
                    name="Up and Down air supply",
                    icon_fn=lambda device: "mdi:swap-vertical",
                    current_state_fn=lambda device: TCL_SplitAC_DeviceData_Helper(
                        device.data
                    ).getUpAndDownAirSupplyVector(),
                    options_values=[e.value for e in UpAndDownAirSupplyVectorEnum],
                    select_option_fn=lambda device,
                    option: coordinator.get_aws_iot().async_set_up_and_down_air_supply_vector(
                        device.device_id, option
                    ),
                )
            )
            
        if DeviceFeature.SELECT_HORIZONTAL_DIRECTION in supported_features:
            switches.append(
                Select(
                    coordinator=coordinator,
                    device=device,
                    type="LeftAndRightAirSupplyVector",
                    name="Left and Right air supply",
                    icon_fn=lambda device: "mdi:swap-horizontal",
                    current_state_fn=lambda device: TCL_SplitAC_DeviceData_Helper(
                        device.data
                    ).getLeftAndRightAirSupplyVector(),
                    options_values=[e.value for e in LeftAndRightAirSupplyVectorEnum],
                    select_option_fn=lambda device,
                    option: coordinator.get_aws_iot().async_set_left_and_right_air_supply_vector(
                        device.device_id, option
                    ),
                )
            )
            
        if DeviceFeature.SELECT_SLEEP_MODE in supported_features:
            switches.append(
                Select(
                    coordinator=coordinator,
                    device=device,
                    type="SleepMode",
                    name="Sleep Mode",
                    icon_fn=lambda device: "mdi:sleep",
                    current_state_fn=lambda device: TCL_SplitAC_DeviceData_Helper(
                        device.data
                    ).getSleepMode(),
                    options_values=[e.value for e in SleepModeEnum],
                    select_option_fn=lambda device,
                    option: coordinator.get_aws_iot().async_set_sleep_mode(
                        device.device_id, option
                    ),
                )
            )

    async_add_entities(switches)


class Select(TclEntityBase, SelectEntity):
    def __init__(
        self,
        coordinator: IotDeviceCoordinator,
        device: Device,
        type: str,
        name: str,
        icon_fn: lambda device: str,
        current_state_fn: lambda device: str,
        options_values: list[str] | None,
        select_option_fn: lambda device, option: None,
    ) -> None:
        TclEntityBase.__init__(self, coordinator, type, name, device)

        self.icon_fn = icon_fn
        self.select_option_fn = select_option_fn
        self.current_state_fn = current_state_fn

        self._attr_current_option = self.current_state_fn(device)
        self._attr_options = options_values

    @property
    def icon(self):
        return self.icon_fn(self.device)

    @property
    def state(self):
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        return self.current_state_fn(self.device)

    async def async_select_option(self, option: str) -> None:
        await self.select_option_fn(self.device, option)
        await self.coordinator.async_refresh()
