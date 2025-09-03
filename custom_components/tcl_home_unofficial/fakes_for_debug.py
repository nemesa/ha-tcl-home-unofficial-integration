"""."""
import logging

from homeassistant.core import HomeAssistant
from .data_storage import get_internal_settings, safe_get_value
from .tcl import GetThingsResponse, ConfigGetResponse

_LOGGER = logging.getLogger(__name__)

async def aws_iot_get_all_things(hass: HomeAssistant):
    data={
        "code":200,
        "message":"fake data",
    }
    dataList=[]
    internal_settings = await get_internal_settings(hass)
    
    diganostics = safe_get_value(internal_settings, "fake.data", {})
    if "data" in diganostics:
        counter = 1
        for tcl_thing in diganostics.get("data", {}).get("tcl", {}).get("tcl_things", []):
            _LOGGER.info("aws_iot_get_all_things adding fake device %s", tcl_thing)
            dataList.append({
                "deviceId":tcl_thing.get("device_id", "Fake_device_id_"+str(counter)),
                "nickName": tcl_thing.get("nick_name", "Fake_nick_name_"+str(counter)),
                "deviceName": tcl_thing.get("device_name", "Fake_device_name_"+str(counter)),
                'productKey': tcl_thing.get("product_key", "Fake_product_key_"+str(counter)),
                'platform': tcl_thing.get("platform", "Fake_platform_"+str(counter)),
                "category": tcl_thing.get("category", "Fake_category_"+str(counter)),
                "firmwareVersion": tcl_thing.get("firmware_version", "Fake_firmware_version_"+str(counter)),
                "isOnline": tcl_thing.get("is_online",1),
                "room": tcl_thing.get("room", "Fake_room_"+str(counter)),
                "type": tcl_thing.get("type", 0),
                "deviceType": tcl_thing.get("device_type", "Fake_device_type_"+str(counter)),
                "netType": tcl_thing.get("net_type", 0),
            })
            counter+=1     

    data["data"]=dataList

    return GetThingsResponse(data)

async def aws_iot_get_thing(hass: HomeAssistant, device_id: str):
    _LOGGER.info("aws_iot_get_thing (%s)", device_id)
    data={
        "state":{
            "desired":{},
            "reported":{}
        }
    }
   
    internal_settings = await get_internal_settings(hass)
    
    diganostics = safe_get_value(internal_settings, "fake.data", {})
    if "data" in diganostics:
        counter = 1
        for aws_thing in diganostics.get("data",{}).get("aws_init", {}).get("aws_things", []):
            aws_device_id = aws_thing.get("deviceId", "Fake_device_id_"+str(counter))
            _LOGGER.info("aws_thing - %s", aws_device_id)
            if aws_device_id == device_id:
                _LOGGER.info("aws_iot_get_thing found fake device %s", aws_device_id)
                data["state"]["desired"] = aws_thing.get("reported", {})
                data["state"]["reported"] = aws_thing.get("reported", {})
                break
            counter+=1        
    
    return data


async def device_rn_probe_fetch_and_parse_config(hass, device_id: str):
    _LOGGER.info("device_rn_probe_fetch_and_parse_config (%s)", device_id)
    data={
        "code":200,
        "message":"fake data",
    }
    dataList=[]
   
    internal_settings = await get_internal_settings(hass)
    diganostics = safe_get_value(internal_settings, "fake.data", {})
    if "data" in diganostics:
        counter = 1
        for device_storage in diganostics.get("data", {}).get("device_storages", []):
            storage_device_id = device_storage.get("deviceId", "Fake_device_id_"+str(counter))            
            if storage_device_id == device_id:
                dataList.append(safe_get_value(device_storage,"non_user_config.rn_probe_data.config_data",{}))                
                break
            counter+=1  
    
    data["data"]=dataList    
    return ConfigGetResponse(data)