"""."""

import datetime
from functools import partial
import json
import logging

import boto3
import boto3.session

from homeassistant.core import HomeAssistant

from .config_entry import New_NameConfigEntry
from .device_data_storage import get_stored_data
from .session_manager import SessionManager
from .tcl import GetThingsResponse, get_things

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
    ) -> None:
        """Initialize the AWS IoT client."""
        self.hass = hass
        self.session_manager = SessionManager(hass=hass, config_entry=config_entry)
        self.client = None

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
            stored_data = await get_stored_data(self.hass, device_id)
            _LOGGER.info(
                "AwsIot.async_get_thing.stored_data (%s): %s", device_id, stored_data
            )
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
        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)
