"""Interfaces with the Integration 101 Template api sensors."""

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .config_entry import New_NameConfigEntry
from .coordinator import IotDeviceCoordinator
from .device import Device, DeviceTypeEnum, TCL_SplitAC_DeviceData_Helper
from .tcl_entity_base import TclEntityBase

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: New_NameConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Sensors."""

    coordinator = config_entry.runtime_data.coordinator

    sensors = []
    for device in config_entry.devices:
        if device.device_type == DeviceTypeEnum.SPLIT_AC:
            # sensors.append(
            #     TemperatureSensor(
            #         coordinator=coordinator,
            #         device=device,
            #         type="TargetTemperature",
            #         name="Target Temperature",
            #         value_fn=lambda device: device.data.target_temperature,
            #     )
            # )
            sensors.append(
                TemperatureSensor(
                    coordinator=coordinator,
                    device=device,
                    type="CurrentTemperature",
                    name="Current Temperature",
                    value_fn=lambda device: device.data.current_temperature,
                )
            )
            # sensors.append(
            #     EnumSensor(
            #         coordinator=coordinator,
            #         device=device,
            #         type="Mode",
            #         name="Mode",
            #         icon="mdi:set-none",
            #         value_fn=lambda device: TCL_SplitAC_DeviceData_Helper(
            #             device.data
            #         ).getMode(),
            #     )
            # )
            # sensors.append(
            #     EnumSensor(
            #         coordinator=coordinator,
            #         device=device,
            #         type="WindSpeed",
            #         name="Wind Speed",
            #         icon="mdi:weather-windy",
            #         value_fn=lambda device: TCL_SplitAC_DeviceData_Helper(
            #             device.data
            #         ).getWindSpeed(),
            #     )
            # )
            # sensors.append(
            #     EnumSensor(
            #         coordinator=coordinator,
            #         device=device,
            #         type="UpAndDownAirSupplyVector",
            #         name="Up and Down air supply",
            #         icon="mdi:swap-vertical",
            #         value_fn=lambda device: TCL_SplitAC_DeviceData_Helper(
            #             device.data
            #         ).getUpAndDownAirSupplyVector(),
            #     )
            # )
            # sensors.append(
            #     EnumSensor(
            #         coordinator=coordinator,
            #         device=device,
            #         type="LeftAndRightAirSupplyVector",
            #         name="Left and Right air supply",
            #         icon="mdi:swap-horizontal",
            #         value_fn=lambda device: TCL_SplitAC_DeviceData_Helper(
            #             device.data
            #         ).getLeftAndRightAirSupplyVector(),
            #     )
            # )
            # sensors.append(
            #     EnumSensor(
            #         coordinator=coordinator,
            #         device=device,
            #         type="SleepMode",
            #         name="Sleep Mode",
            #         icon="mdi:sleep",
            #         value_fn=lambda device: TCL_SplitAC_DeviceData_Helper(
            #             device.data
            #         ).getSleepMode(),
            #     )
            # )
    async_add_entities(sensors)


class TemperatureSensor(TclEntityBase, SensorEntity):
    def __init__(
        self,
        coordinator: IotDeviceCoordinator,
        device: Device,
        type: str,
        name: str,
        value_fn,
    ) -> None:
        TclEntityBase.__init__(self, coordinator, type, name, device)
        self.value_fn = value_fn

    @property
    def device_class(self) -> str:
        return SensorDeviceClass.TEMPERATURE

    @property
    def native_value(self) -> int | float:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        return float(self.value_fn(self.device))

    @property
    def native_unit_of_measurement(self) -> str | None:
        return UnitOfTemperature.CELSIUS

    @property
    def state_class(self) -> str | None:
        return SensorStateClass.MEASUREMENT


class EnumSensor(TclEntityBase, SensorEntity):
    def __init__(
        self,
        coordinator: IotDeviceCoordinator,
        device: Device,
        type: str,
        name: str,
        icon: str,
        value_fn,
    ) -> None:
        TclEntityBase.__init__(self, coordinator, type, name, device)
        self.icon_name = icon
        self.value_fn = value_fn

    @property
    def device_class(self) -> str:
        return SensorDeviceClass.ENUM

    @property
    def icon(self):
        return self.icon_name

    @property
    def native_value(self) -> int | float:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        return self.value_fn(self.device)

    @property
    def native_unit_of_measurement(self) -> str | None:
        return None
