"""."""

import datetime
from functools import partial
import json
import logging

import boto3
import boto3.session

from homeassistant.core import HomeAssistant

from .config_entry import New_NameConfigEntry
from .data_storage import safe_get_value, safe_set_value, set_stored_data
from .session_manager import SessionManager
from .tcl import (
    GetThingsResponse, 
    GetWorkTimeResponse,
    GetEnergyConsumptioneResponse, 
    get_things,
    get_energy_consumption, 
    get_work_time, 
    get_day_for_filer,
    get_day_for_data
)
from .fakes_for_debug import aws_iot_get_all_things, aws_iot_get_thing

_LOGGER = logging.getLogger(__name__)


def getTopic(device_id: str) -> str:
    """Get the topic for the device."""
    return f"$aws/things/{device_id}/shadow/update"


class AwsIot:
    """Class to handle AWS IoT operations."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: New_NameConfigEntry | None = None,
        use_fakes: bool = False,
    ) -> None:
        """Initialize the AWS IoT client."""
        self.hass = hass
        self.session_manager = SessionManager(hass=hass, config_entry=config_entry)
        self.client = None
        self.use_fakes = use_fakes

    async def async_setup_client(self) -> None:
        aws_region = await self.session_manager.get_aws_region()
        awsCred = await self.session_manager.async_aws_credentials()

        boto3Session = boto3.session.Session(
            region_name=aws_region,
            aws_access_key_id=awsCred.Credentials.access_key_id,
            aws_secret_access_key=awsCred.Credentials.secret_key,
            aws_session_token=awsCred.Credentials.session_token,
        )

        self.client = await self.hass.async_add_executor_job(
            partial(boto3Session.client, service_name="iot-data")
        )
        # self.client = boto3Session.client(service_name="iot-data")

    async def async_init(self) -> None:
        await self.session_manager.async_load()
        await self.async_setup_client()

    def get_session_manager(self) -> SessionManager:
        return self.session_manager

    async def get_all_things(self) -> GetThingsResponse:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info("AwsIot.get_all_things")
        if self.use_fakes:
            _LOGGER.warning("AwsIot.get_all_things.FAKES_ENABLED")
            fake_things = await aws_iot_get_all_things(self.hass)
            return fake_things
        authResult = await self.session_manager.async_get_auth_data()
        refreshTokensResult = await self.session_manager.async_refresh_tokens()
        saas_token = refreshTokensResult.data.saas_token

        clud_urls = await self.session_manager.async_aws_cloud_urls()

        things = await get_things(
            hass=self.hass,
            device_url=clud_urls.data.device_url,
            saas_token=saas_token,
            country_abbr=authResult.user.country_abbr,
            verbose_logging=self.session_manager.is_verbose_device_logging(),
        )

        return things
    
    async def get_last_two_today_energy_consumption(self,device_id: str) -> GetEnergyConsumptioneResponse:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info("AwsIot.get_energy_consumption")  
        if self.use_fakes:
            _LOGGER.warning("AwsIot.get_energy_consumption.FAKES_ENABLED")            
            return GetEnergyConsumptioneResponse({"code":10003,"message":"FAKES_ENABLED","data":{}})
        refreshTokensResult = await self.session_manager.async_refresh_tokens()
        saas_token = refreshTokensResult.data.saas_token

        clud_urls = await self.session_manager.async_aws_cloud_urls()

        response = await get_energy_consumption(
            hass=self.hass,
            device_url=clud_urls.data.device_url,
            saas_token=saas_token,
            deviceId=device_id,
            date_filter= f"?week={get_day_for_filer(-1)}-{get_day_for_filer()}",
            verbose_logging=self.session_manager.is_verbose_device_logging(),
        )

        return response

    
    async def get_last_two_today_work_time(self,device_id: str) -> GetWorkTimeResponse:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info("AwsIot.get_work_time")
        if self.use_fakes:
            _LOGGER.warning("AwsIot.get_work_time.FAKES_ENABLED")            
            return GetWorkTimeResponse({"code":10003,"message":"FAKES_ENABLED","data":{}})               
        refreshTokensResult = await self.session_manager.async_refresh_tokens()
        saas_token = refreshTokensResult.data.saas_token

        clud_urls = await self.session_manager.async_aws_cloud_urls()

        response = await get_work_time(
            hass=self.hass,
            device_url=clud_urls.data.device_url,
            saas_token=saas_token,
            deviceId=device_id,
            date_filter= f"?week={get_day_for_filer(-1)}-{get_day_for_filer()}",
            verbose_logging=self.session_manager.is_verbose_device_logging(),
        )

        return response


    async def get_extra_tcl_data(self,device_storage: dict, device_id: str) -> dict:
        now_timestamp=int(datetime.datetime.now().timestamp())
        today_total_electricity=0    
        yesterday_total_electricity=0    
        need_save=False
        stored_data=device_storage
        power_consumption_data_enabled= safe_get_value(device_storage, "non_user_config.power_consumption.enabled", False)
        if power_consumption_data_enabled:
            power_consumption_polling_interval= safe_get_value(device_storage, "non_user_config.power_consumption.polling_interval_in_minutes", 60)
            power_consumption_last_time= safe_get_value(device_storage, "non_user_config.power_consumption.last_response.timestamp", 1759400000)
            response= GetEnergyConsumptioneResponse(safe_get_value(device_storage, "non_user_config.power_consumption.last_response.data", {"code":-1,"message":"NO_DATA","data":{}}))
            delta=int((now_timestamp-power_consumption_last_time)/60)            
            if delta>=power_consumption_polling_interval:
                response = await self.get_last_two_today_energy_consumption(device_id)
                if response.code==0:                        
                    stored_data, need_save = safe_set_value(stored_data, "non_user_config.power_consumption.last_response.timestamp", now_timestamp, True)
                    stored_data, need_save = safe_set_value(stored_data, "non_user_config.power_consumption.last_response.data", response, True)  
            if response.code==0:
                for day in response.data.consumption_details:
                    if day.date==get_day_for_data():
                        today_total_electricity=day.consumption
                    if day.date==get_day_for_data(-1):
                        yesterday_total_electricity=day.consumption

        today_work_time=0
        yesterday_work_time=0
        work_time_data_enabled= safe_get_value(device_storage, "non_user_config.work_time.enabled", False)
        if work_time_data_enabled:
            work_time_polling_interval= safe_get_value(device_storage, "non_user_config.work_time.polling_interval_in_minutes", 60)
            work_time_last_time= safe_get_value(device_storage, "non_user_config.work_time.last_response.timestamp", 1759400000)
            response= GetWorkTimeResponse(safe_get_value(device_storage, "non_user_config.work_time.last_response.data", {"code":-1,"message":"NO_DATA","data":{}}))
            delta=int((now_timestamp-work_time_last_time)/60)            
            if delta>=work_time_polling_interval:
                response = await self.get_last_two_today_work_time(device_id)
                if response.code==0:
                    stored_data, need_save = safe_set_value(stored_data, "non_user_config.work_time.last_response.timestamp", now_timestamp, True)
                    stored_data, need_save = safe_set_value(stored_data, "non_user_config.work_time.last_response.data", response, True)              
            if response.code==0:    
                for day in response.data.work_time_details:
                    if day.date==get_day_for_data():
                        today_work_time=day.work_time
                    if day.date==get_day_for_data(-1):
                        yesterday_work_time=day.work_time                        

        if need_save:
            await set_stored_data(self.hass, device_id, stored_data)

        return {
            "today_total_electricity": today_total_electricity,
            "yesterday_total_electricity": yesterday_total_electricity,
            "today_work_time":today_work_time,
            "yesterday_work_time":yesterday_work_time
        }

    async def execute_and_re_try_call_with_device_id(
        self,
        function,
        device_id: str,
        fromException: bool = False,
    ):
        try:
            return await self.hass.async_add_executor_job(function, device_id)
        except Exception as e:
            # re-try if the error is due to expired credentials
            if not fromException:
                self.client.close()
                await self.async_setup_client()
                return await self.execute_and_re_try_call_with_device_id(
                    function=function,
                    device_id=device_id,
                    fromException=True,
                )
            _LOGGER.error(
                "Aws_iot - Error execute_and_re_try_call_with_device_id %s: %s",
                device_id,
                e,
            )
            raise e

    async def execute_and_re_try_call_with_device_id_and_desired_state(
        self,
        function,
        device_id: str,
        desired_state: dict[str, any],
        fromException: bool = False,
    ):
        try:
            return await self.hass.async_add_executor_job(
                function, device_id, desired_state
            )
        except Exception as e:
            # re-try if the error is due to expired credentials
            if not fromException:
                self.client.close()
                await self.async_setup_client()
                return (
                    await self.execute_and_re_try_call_with_device_id_and_desired_state(
                        function=function,
                        device_id=device_id,
                        desired_state=desired_state,
                        fromException=True,
                    )
                )
            _LOGGER.error(
                "Aws_iot - Error execute_and_re_try_call_with_device_id_and_desired_state %s - %s | %s",
                device_id,
                desired_state,
                e,
            )
            raise e

    async def async_get_thing(
        self, device_id: str, fromException: bool = False
    ) -> dict:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info("AwsIot.async_get_thing (%s)", device_id)
        if self.use_fakes:
            _LOGGER.warning("AwsIot.async_get_thing (%s) FAKES_ENABLED", device_id)
            fake_thing = await aws_iot_get_thing(self.hass, device_id)
            return fake_thing

        return await self.execute_and_re_try_call_with_device_id(
            self.get_thing, device_id, fromException
        )

    def get_thing(self, device_id: str) -> dict:
        """List all things in AWS IoT."""
        response = self.client.get_thing_shadow(thingName=device_id)
        payload = response["payload"].read().decode("utf-8")
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info("AwsIot.get_thing (%s): %s", device_id, payload)
        return json.loads(payload)

    async def async_set_desired_state(
        self,
        device_id: str,
        desired_state: dict[str, any],
        fromException: bool = False,
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_desired_state(
            self.set_desired_state, device_id, desired_state, fromException
        )

    def set_desired_state(self, device_id: str, desired_state: dict[str, any]) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info("AwsIot.set_desired_state: (%s) %s", device_id, desired_state)
        payload = json.dumps(
            {
                "state": {"desired": desired_state},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )
        
        if self.use_fakes:
            _LOGGER.warning("AwsIot.set_desired_state (%s) FAKES_ENABLED", device_id)
            _LOGGER.info("AwsIot.set_desired_state (%s) payload: %s", device_id, payload)
            return
        
        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)

