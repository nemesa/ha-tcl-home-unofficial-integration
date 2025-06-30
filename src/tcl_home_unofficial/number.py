"""."""

import logging

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .aws_iot import AwsIot
from .config_entry import New_NameConfigEntry
from .const import DOMAIN
from .coordinator import IotDeviceCoordinator
from .device import Device, toDeviceInfo

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: New_NameConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Binary Sensors."""
    coordinator = config_entry.runtime_data.coordinator

    aws_iot = AwsIot(
        hass=hass,
        config_entry=config_entry,
    )
    await aws_iot.async_init()

    customEntities = []
    for device in config_entry.devices:
        customEntities.append(SetTargetTempEntity(coordinator, device, aws_iot))

    async_add_entities(customEntities)


class SetTargetTempEntity(CoordinatorEntity, NumberEntity):
    def __init__(
        self, coordinator: IotDeviceCoordinator, device: Device, aws_iot: AwsIot
    ) -> None:
        super().__init__(coordinator)
        self.device = device
        self.aws_iot = aws_iot

        self._attr_assumed_state = False
        self._attr_device_class = NumberDeviceClass.TEMPERATURE
        self._attr_translation_key = None
        self._attr_mode = NumberMode.SLIDER  # NumberMode.BOX
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_native_value = device.data.target_temperature
        # self._attr_unique_id = f"{DOMAIN}-SetTargetTempEntity-{self.device.device_id}"
        # self._attr_device_info = toDeviceInfo(self.device)

        self._attr_native_min_value = 16
        self._attr_native_max_value = 36
        self._attr_native_step = 1

    @callback
    def _handle_coordinator_update(self) -> None:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        self.async_write_ha_state()

    @property
    def device_class(self) -> str:
        return NumberDeviceClass.TEMPERATURE

    @property
    def unique_id(self) -> str:
        return f"{DOMAIN}-SetTargetTempEntity-{self.device.device_id}"

    @property
    def device_info(self) -> DeviceInfo:
        return toDeviceInfo(self.device)

    @property
    def name(self) -> str:
        return "Set Target Temperature"

    @property
    def native_value(self) -> int | float:
        return float(self.device.data.target_temperature)

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        _LOGGER.info(
            "Setting target temperature for device %s to %s",
            self.device.device_id,
            value,
        )
        await self.aws_iot.async_set_target_temperature(
            self.device.device_id, int(value)
        )
        self.device.data.target_temperature = int(value)
        self.coordinator.set_device(self.device)
        self.async_write_ha_state()
