"""."""

from homeassistant.core import HomeAssistant
import logging
from homeassistant.helpers import storage
from .const import get_device_data_storege_key


_LOGGER = logging.getLogger(__name__)


async def get_stored_data(hass: HomeAssistant, device_id: str) -> dict[str, any] | None:
    """Get stored data for a device."""
    key = get_device_data_storege_key(device_id)
    data_storage: storage.Store[dict] = storage.Store(hass=hass, version=1, key=key)

    data = await data_storage.async_load()
    _LOGGER.debug("device_data_storage.get_stored_data %s - %s", key, data)

    return data


async def set_stored_data(
    hass: HomeAssistant, device_id: str, data_to_set: dict[str, any]
) -> dict[str, any] | None:
    """Set the stored data for a device. This will merge the values with the existing data."""
    key = get_device_data_storege_key(device_id)
    data_storage: storage.Store[dict] = storage.Store(hass=hass, version=1, key=key)
    data = await data_storage.async_load()

    data_to_store = {**data, **data_to_set} if data is not None else data_to_set

    _LOGGER.debug(
        "device_data_storage.set_stored_data %s - %s + %s", key, data, data_to_set
    )
    await data_storage.async_save(data=data_to_store)

    return data_to_store


async def delete_stored_data(hass: HomeAssistant, device_id: str) -> None:
    """Delete the stored data for a device."""
    key = get_device_data_storege_key(device_id)
    data_storage: storage.Store[dict] = storage.Store(hass=hass, version=1, key=key)

    _LOGGER.debug("device_data_storage.delete_stored_data %s", key)
    await data_storage.async_save(data=None)
