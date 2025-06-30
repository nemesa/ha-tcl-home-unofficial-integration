"""."""

from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import IotDeviceCoordinator
from .device import Device, toDeviceInfo


class TclEntityBase(CoordinatorEntity):
    def __init__(
        self, coordinator: IotDeviceCoordinator, type: str, name: str, device: Device
    ) -> None:
        super().__init__(coordinator)
        self.device = device
        self.type = type
        self._name = name
        self._attr_unique_id = f"{DOMAIN}-{type}-{device.device_id}"

    @callback
    def _handle_coordinator_update(self) -> None:
        self.device = self.coordinator.get_device_by_id(self.device.device_id)
        self.async_write_ha_state()

    @property
    def unique_id(self) -> str:
        return self._attr_unique_id

    @property
    def device_info(self) -> DeviceInfo:
        return toDeviceInfo(self.device)

    @property
    def name(self) -> str:
        return self._name
