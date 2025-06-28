"""."""

import json
import logging

import boto3
import boto3.session

from homeassistant.core import HomeAssistant

from .config_entry import New_NameConfigEntry
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
        self.config_entry = config_entry
        self.region_name = config_entry.data["aws_region"]
        self.session_manager = SessionManager(hass=hass, config_entry=config_entry)
        self.client = None

    async def async_init(self) -> None:
        await self.session_manager.async_load()

        awsCred = await self.session_manager.async_aws_credentials()

        boto3Session = boto3.session.Session(
            region_name=self.region_name,
            aws_access_key_id=awsCred.Credentials.access_key_id,
            aws_secret_access_key=awsCred.Credentials.secret_key,
            aws_session_token=awsCred.Credentials.session_token,
        )

        # _LOGGER.info("AwsIot.get_available_services: %s", s.get_available_services())

        self.client = boto3Session.client(service_name="iot-data")

    async def get_all_things(self) -> GetThingsResponse:
        authResult = await self.session_manager.async_get_auth_data()
        refreshTokensResult = await self.session_manager.async_refresh_tokens()
        saas_token = refreshTokensResult.data.saas_token

        things = await get_things(saas_token, authResult.user.country_abbr)

        return things

    async def async_getThing(self, device_id: str) -> dict:
        return await self.hass.async_add_executor_job(self.getThing, device_id)

    def getThing(self, device_id: str) -> dict:
        """List all things in AWS IoT."""
        response = self.client.get_thing_shadow(thingName=device_id)
        payload = response["payload"].read().decode("utf-8")
        return json.loads(payload)

    def turnOn(self, device_id: str) -> None:
        """Turn on the device."""
        payload = json.dumps(
            {"state": {"desired": {"beepSwitch": 0, "powerSwitch": 1}}}
        )

        self.client.publish(
            topic=getTopic(device_id),
            qos=1,
            payload=payload,
        )

    def turnOff(self, device_id: str) -> None:
        """Turn off the device."""
        payload = json.dumps(
            {"state": {"desired": {"beepSwitch": 0, "powerSwitch": 0}}}
        )

        self.client.publish(
            topic=getTopic(device_id),
            qos=1,
            payload=payload,
        )
