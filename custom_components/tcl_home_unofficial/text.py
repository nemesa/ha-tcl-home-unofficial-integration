"""Interfaces with the Example api sensors."""

import logging


from homeassistant.components.text import TextEntity, TextMode
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .config_entry import New_NameConfigEntry
from .const import DOMAIN
from .device import Device, DeviceTypeEnum
from .tcl_entity_base import TclNonPollingEntityBase
from .coordinator import IotDeviceCoordinator
from .self_diagnostics import SelfDiagnostics

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: New_NameConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Binary Sensors."""

    coordinator = config_entry.runtime_data.coordinator
    textInputs = []
    for device in config_entry.non_implemented_devices:
        textInputs.append(
            NotImplementedDeviceTextEntity(
                hass=hass,
                coordinator=coordinator,
                type="ManualStateDump",
                name="Manual state dump action",
                device=device,
                enabled=True,
            )
        )

    for device in config_entry.devices:
        textInputs.append(
            NotImplementedDeviceTextEntity(
                hass=hass,
                coordinator=coordinator,
                type="ManualStateDump",
                name="Manual state dump action",
                device=device,
                enabled=True
                if device.device_type is DeviceTypeEnum.SPLIT_AC
                else False,
            )
        )

    async_add_entities(textInputs)


class NotImplementedDeviceTextEntity(TclNonPollingEntityBase, TextEntity):
    _attr_has_entity_name = True
    _attr_name = None
    _attr_should_poll = True
    _attr_force_update = True

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: IotDeviceCoordinator,
        type: str,
        name: str,
        device: Device,
        enabled: bool,
    ) -> None:
        TclNonPollingEntityBase.__init__(self, type, name, device)

        self.hass = hass
        self.coordinator = coordinator
        self._attr_mode = TextMode.TEXT
        self._attr_native_max = 1000
        self._attr_native_min = 0
        self._attr_native_value = "______________________"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self.counter = 0
        self.selfDiagnostics = SelfDiagnostics(hass=hass, device_id=device.device_id)
        self._attr_entity_registry_enabled_default = enabled

    @property
    def native_value(self) -> str | None:
        """Return the value reported by the text."""
        return self._attr_native_value

    async def async_set_value(self, value: str) -> None:
        """Update the value."""
        self.counter += 1
        self._attr_native_value = f"OK - action no:{self.counter} saved"
        aws_thing = await self.coordinator.get_aws_iot().async_get_thing(
            self.device.device_id
        )
        await self.selfDiagnostics.addState(value, aws_thing)
        await self.async_update_ha_state(force_refresh=True)
