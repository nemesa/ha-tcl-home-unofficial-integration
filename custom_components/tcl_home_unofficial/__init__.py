"""The TCL Home - Unofficial integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .aws_iot import AwsIot
from .config_entry import (
    New_NameConfigEntry,
    RuntimeData,
    convertToConfigData,
    sanitizeConfigData,
)
from .coordinator import IotDeviceCoordinator
from .device import Device, get_device_storage, store_rn_prode_data
from .device_types import is_implemented_by_integration
from .device_rn_probe import fetch_and_parse_config
from .data_storage import get_internal_settings, safe_set_value, set_internal_settings, safe_get_value, set_stored_data

_PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.SELECT,
    Platform.NUMBER,
    Platform.BUTTON,
    Platform.REMOTE,
    Platform.CLIMATE,
    Platform.HUMIDIFIER,
    Platform.TEXT,
]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config_entry: New_NameConfigEntry
) -> bool:
    """Set up TCL Home - Unofficial from a config entry."""
    configData = convertToConfigData(config_entry)

    if configData.verbose_setup_logging:
        _LOGGER.info("Setup.async_setup_entry %s",sanitizeConfigData(configData))

    config_entry.devices = []
    config_entry.non_implemented_devices = []

    internal_settings = await internal_settings_setup(hass)
    if configData.verbose_setup_logging:
        _LOGGER.info("Setup.internal_settings %s",internal_settings)    

    aws_iot = AwsIot(
        hass=hass,
        config_entry=config_entry,
        use_fakes=safe_get_value(internal_settings, "fake.use_fake_data", False)
    )
    if configData.verbose_setup_logging:
        _LOGGER.info("Setup.async_setup_entry session_manager.clear_storage")
    await aws_iot.get_session_manager().clear_storage()

    if configData.verbose_setup_logging:
        _LOGGER.info("Setup.async_setup_entry aws_iot.async_init")
    await aws_iot.async_init()

    if configData.verbose_setup_logging:
        _LOGGER.info("Setup.async_setup_entry aws_iot.get_all_things")

    things = await aws_iot.get_all_things()

    if configData.verbose_setup_logging:
        _LOGGER.info("Setup.async_setup_entry aws_iot.get_all_things result %s", things)

    for thing in things.data:
        is_implemented = is_implemented_by_integration(thing.device_name)

        if thing.is_online and is_implemented:
            if configData.verbose_setup_logging:
                _LOGGER.info("Setup.async_setup_entry aws_iot.async_get_thing deviceName:%s id:%s",thing.device_name,thing.device_id,)
            aws_thing = await aws_iot.async_get_thing(thing.device_id)
        else:
            aws_thing = None
            if thing.is_online:
                _LOGGER.warning("Setup.async_setup_entry device is not implemented by this integration: %s",thing)
            else:
                _LOGGER.warning("Setup.async_setup_entry device is not online or not implemented by this integration (is_implemented:%s): %s",is_implemented,thing)

        device_id = thing.device_id

        probe_result = await fetch_and_parse_config(
            hass= hass, 
            session_manager= aws_iot.get_session_manager(), 
            device_id= device_id, 
            product_key=thing.product_key,
            use_fakes=safe_get_value(internal_settings, "fake.use_fake_data", False)
        )
        storage_data = await store_rn_prode_data(hass, device_id, probe_result)
        
        power_consumption_init_done= safe_get_value(storage_data, "non_user_config.power_consumption.init_done", False)
        if configData.verbose_setup_logging:
            _LOGGER.info("_init_.power_consumption_init_done - %s",power_consumption_init_done)
        if not power_consumption_init_done:
            response = await aws_iot.get_last_two_today_energy_consumption(device_id)
            if configData.verbose_setup_logging:
                _LOGGER.info("_init_.power_consumption check - %s",response.message)
                        
            storage_data, need_save = safe_set_value(storage_data, "non_user_config.power_consumption.init_done", True,True)
            storage_data, need_save = safe_set_value(storage_data, "non_user_config.power_consumption.enabled", True if response.code==0 else False, True)
            if need_save:
                storage_data=await set_stored_data(hass, device_id, storage_data)
            
        
        work_time_init_done= safe_get_value(storage_data, "non_user_config.work_time.init_done", False)
        if configData.verbose_setup_logging:
            _LOGGER.info("_init_.work_time_init_done - %s",work_time_init_done)
        if not work_time_init_done:
            response = await aws_iot.get_last_two_today_work_time(device_id)
            if configData.verbose_setup_logging:
                _LOGGER.info("_init_.work_time_data_enabled check - %s",response.message)
                
            storage_data, need_save = safe_set_value(storage_data, "non_user_config.work_time.init_done", True,True)
            storage_data, need_save = safe_set_value(storage_data, "non_user_config.work_time.enabled", True if response.code==0 else False, True)
            if need_save:
                storage_data= await set_stored_data(hass, device_id, storage_data)

        extra_tcl_data = await aws_iot.get_extra_tcl_data(storage_data,device_id)

        device = Device(
            tcl_thing=thing,
            aws_thing=aws_thing,
            device_storage=storage_data,
            extra_tcl_data=extra_tcl_data
        )
        if configData.verbose_setup_logging:
            _LOGGER.info("_init_.device:%s", device.print_data())
            
        if device.device_type is not None:
            if configData.verbose_setup_logging:
                _LOGGER.info("Setup.async_setup_entry found device:%s", device)
            device.storage = await get_device_storage(hass, device)
            config_entry.devices.append(device)
        else:
            config_entry.non_implemented_devices.append(device)

    # Initialise a listener for config flow options changes.
    cancel_update_listener = config_entry.async_on_unload(
        config_entry.add_update_listener(_async_update_listener)
    )

    coordinator = IotDeviceCoordinator(hass, config_entry, aws_iot)
    await coordinator.async_config_entry_first_refresh()
    config_entry.runtime_data = RuntimeData(coordinator, cancel_update_listener)

    await hass.config_entries.async_forward_entry_setups(config_entry, _PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: New_NameConfigEntry) -> bool:
    """Unload a config entry."""
    # TODO: cleanup the device storega data
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)


async def _async_update_listener(hass: HomeAssistant, config_entry: ConfigEntry):
    """Handle config options update.

    Reload the integration when the options change.
    Called from our listener created above.
    """
    configData = convertToConfigData(config_entry)

    if configData.verbose_setup_logging:
        _LOGGER.info(
            "Setup._async_update_listener %s",
            sanitizeConfigData(configData),
        )
    await hass.config_entries.async_reload(config_entry.entry_id)

async def internal_settings_setup(hass: HomeAssistant):
    need_save = False
    stored_data = await get_internal_settings(hass)
    if stored_data is None:
        stored_data = {}
        need_save = True

    stored_data, need_save = safe_set_value(stored_data, "fake.use_fake_data", False, overwrite_if_exists=False)
    stored_data, need_save = safe_set_value(stored_data, "fake.data", {}, overwrite_if_exists=False)    
    if need_save:
        await set_internal_settings(hass, stored_data)
    return stored_data


"""
{
  "version": 1,
  "minor_version": 1,
  "key": "tcl_home_unofficial.internal_settings_storage",
  "data": {
    "fake": {
      "use_fake_data": false,
      "data": {}
    }
  }
}
"""