"""Diagnostics for tcl_home_unofficial integration."""

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry

from .aws_iot import AwsIot
from .config_entry import New_NameConfigEntry
from .data_storage import get_stored_data
from .self_diagnostics import SelfDiagnostics
from .config_entry import (
    New_NameConfigEntry,
    asDict,
    convertToConfigData,
    sanitizeConfigData,
)


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: New_NameConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""

    data= await get_diagnosics_data(hass, entry,None)
    return data


async def async_get_device_diagnostics(
    hass: HomeAssistant, entry: New_NameConfigEntry, device: DeviceEntry
) -> dict[str, Any]:
    """Return diagnostics for a device."""

    device_id = next(
        identifier[1]
        for identifier in device.identifiers
        if identifier[0] == "tcl_home_unofficial"
    ).split("-")[1]
    

    data= await get_diagnosics_data(hass, entry,device_id)
    return data

async def get_diagnosics_data(hass: HomeAssistant, entry: New_NameConfigEntry, device_id:str | None) -> dict[str, Any]:
    configData = asDict(sanitizeConfigData(convertToConfigData(entry)))

    aws_iot = AwsIot(
        hass=hass,
        config_entry=entry,
    )

    aws_iot_init_success = False
    aws_iot_init_error = None

    try:
        await aws_iot.async_init()
        aws_iot_init_success = True
    except Exception as e:
        aws_iot_init_error = {"error": str(e)}

    user_country_abbr = ""
    cloud_urls = {}

    if aws_iot_init_success:
        session_manager = aws_iot.get_session_manager()
        authResult = await session_manager.async_get_auth_data(allowInvalid=True)
        if authResult is not None and authResult.user is not None:
            user_country_abbr = authResult.user.country_abbr
        cloudUrls = await session_manager.async_force_cloud_urls()
        if cloudUrls is not None and cloudUrls.data is not None:
            cloud_urls = {
                "sso_region": cloudUrls.data.sso_region,
                "cloud_region": cloudUrls.data.cloud_region,
                "sso_url": cloudUrls.data.sso_url,
                "cloud_url": cloudUrls.data.cloud_url,
                "icon_resource_url": cloudUrls.data.icon_resource_url,
                "identity_pool_id": cloudUrls.data.identity_pool_id,
                "upload_web_url": cloudUrls.data.upload_web_url,
                "device_url": cloudUrls.data.device_url,
                "cloud_url_emq": cloudUrls.data.cloud_url_emq,
            }
            cloudUrls.data

    tcl_things = []
    tcl_things_response_code = 0
    tcl_things_response_message = 0
    deviceIds = []
    try:
        all_things_response = await aws_iot.get_all_things()
        tcl_things_response_code = all_things_response.code
        tcl_things_response_message = all_things_response.message
        for thing in all_things_response.data:
            if device_id is None or thing.device_id == device_id:
                deviceIds.append(thing.device_id)
                tcl_things.append(
                    {
                        "device_id": thing.device_id,
                        "product_key": thing.product_key,
                        "platform": thing.platform,
                        "nick_name": thing.nick_name,
                        "device_name": thing.device_name,
                        "category": thing.category,
                        "type": thing.type,
                        "device_type": thing.device_type,
                        "firmware_version": thing.firmware_version,
                        "net_type": thing.net_type,
                        "is_online": thing.is_online,
                        "room": thing.room,
                    }
                )
    except Exception as e:
        tcl_things = {"error": str(e)}

    aws_things = []
    try:
        for deviceId in deviceIds:            
            if device_id is None or deviceId == device_id:
                aws_thing = await aws_iot.async_get_thing(deviceId)
                aws_things.append({"deviceId":deviceId,"reported":aws_thing.get("state", {}).get("reported", {})})
    except Exception as e:
        aws_things = {"error": str(e)}
    
    device_storages = []
    manual_state_dump_data = {}
    try:
        for deviceId in deviceIds:
            if device_id is None or deviceId == device_id:
                device_storage = await try_get_stored_data(hass, deviceId)
                device_storage["deviceId"]=deviceId
                device_storages.append(device_storage)
    except Exception as e:
        device_storages = {"error": str(e)}

    if device_id is not None:
        self_diagnostics = SelfDiagnostics(hass=hass, device_id=device_id)
        manual_state_dump_data = await self_diagnostics.get_stored_data()
        

    return {
        "configData": configData,
        "regionData": {
            "user_country_abbr": user_country_abbr,
            "cloud_urls": cloud_urls,
        },
        "aws_init": {
            "init_success": aws_iot_init_success,
            "init_error": aws_iot_init_error,
            "aws_things": aws_things,
        },
        "tcl": {
            "things_response_code": tcl_things_response_code,
            "things_response_message": tcl_things_response_message,
            "tcl_things": tcl_things,
        },
        "device_storages": device_storages,
        "manual_state_dump_data": manual_state_dump_data,
    }

async def try_get_stored_data(hass: HomeAssistant, device_id: str):    
    try:
        data = await get_stored_data(hass, device_id)
        return data

    except Exception as e:
        return {"error": str(e)}
