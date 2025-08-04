"""Interfaces with the Integration 101 Template api sensors."""

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
    SensorEntityDescription,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .config_entry import New_NameConfigEntry
from .coordinator import IotDeviceCoordinator
from .device import Device
from .device_features import DeviceFeatureEnum
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

        if DeviceFeatureEnum.SENSOR_CURRENT_TEMPERATURE in device.supported_features:
            sensors.append(
                TemperatureSensor(
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SENSOR_CURRENT_TEMPERATURE,
                    type="CurrentTemperature",
                    name="Current Temperature",
                    value_fn=lambda device: device.data.current_temperature,
                )
            )

        if DeviceFeatureEnum.SENSOR_INTERNAL_UNIT_COIL_TEMPERATURE in device.supported_features:
            sensors.append(
                TemperatureSensor(
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SENSOR_INTERNAL_UNIT_COIL_TEMPERATURE,
                    type="InternalUnitCoilTemperature",
                    name="Internal Unit Coil Temperature",
                    value_fn=lambda device: device.data.internal_unit_coil_temperature,
                )
            )

        if DeviceFeatureEnum.SENSOR_EXTERNAL_UNIT_COIL_TEMPERATURE in device.supported_features:
            sensors.append(
                TemperatureSensor(
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SENSOR_EXTERNAL_UNIT_COIL_TEMPERATURE,
                    type="ExternalUnitCoilTemperature",
                    name="External Unit Coil Temperature",
                    value_fn=lambda device: device.data.external_unit_coil_temperature,
                )
            )

        if DeviceFeatureEnum.SENSOR_EXTERNAL_UNIT_TEMPERATURE in device.supported_features:
            sensors.append(
                TemperatureSensor(
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SENSOR_EXTERNAL_UNIT_TEMPERATURE,
                    type="ExternalUnitTemperature",
                    name="External Unit Temperature",
                    value_fn=lambda device: device.data.external_unit_temperature,
                )
            )

        if DeviceFeatureEnum.SENSOR_EXTERNAL_UNIT_EXHAUST_TEMPERATURE in device.supported_features:
            sensors.append(
                TemperatureSensor(
                    coordinator=coordinator,
                    device=device,
                    deviceFeature=DeviceFeatureEnum.SENSOR_EXTERNAL_UNIT_EXHAUST_TEMPERATURE,
                    type="ExternalUnitExhaustTemperature",
                    name="External Unit Exhaust Temperature",
                    value_fn=lambda device: device.data.external_unit_exhaust_temperature,
                )
            )

    async_add_entities(sensors)


class TemperatureSensor(TclEntityBase, SensorEntity):
    def __init__(
        self,
        coordinator: IotDeviceCoordinator,
        device: Device,
        type: str,
        name: str,
        deviceFeature: DeviceFeatureEnum,
        value_fn,
    ) -> None:
        TclEntityBase.__init__(self, coordinator, type, name, device)
        self.value_fn = value_fn
        self.entity_description = SensorEntityDescription(
            key=deviceFeature,
            translation_key=deviceFeature,
        )

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
