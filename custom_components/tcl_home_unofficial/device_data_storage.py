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


def safe_setup_path(data: dict[str, any] | None, path: str):
    needs_save = False
    if data is None:
        data = {}
        needs_save = True

    keys = path.split(".")
    current = data

    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
            needs_save = True
        current = current[key]

    last_key = keys[-1]
    if last_key not in current:
        current[last_key] = {}
        needs_save = True
    if current[last_key] != current.get(last_key, {}):
        needs_save = True
    current[last_key] = current.get(last_key, {})

    return data, needs_save


def safe_set_value(
    data: dict[str, any] | None,
    path: str,
    value: any,
    overwrite_if_exists: bool = False,
) -> tuple[dict[str, any], bool]:
    needs_save = False
    data_safe, needs_save = safe_setup_path(data, path)
    pointer = data_safe
    parts = path.split(".")
    for index, part in enumerate(parts):
        is_last_item = True if index == parts.__len__() - 1 else False
        if is_last_item:
            if pointer[part] == {}:
                pointer[part] = value
                needs_save = True
            else:
                if value != pointer[part] and overwrite_if_exists:
                    pointer[part] = value
                    needs_save = True
        else:
            pointer = pointer[part]
    return data_safe, needs_save


def safe_get_value(data: dict[str, any] | None, path: str, defaul_value: any) -> any:
    return_value = defaul_value
    if data is None:
        return defaul_value

    pointer = data
    parts = path.split(".")

    for index, part in enumerate(parts):
        is_last_item = True if index == parts.__len__() - 1 else False
        if part not in pointer:
            if is_last_item:
                return defaul_value
        else:
            if is_last_item:
                return_value = pointer[part]
            else:
                pointer = pointer[part]

    return return_value