"""."""

import json
import logging

import boto3
import boto3.session

_LOGGER = logging.getLogger(__name__)


def getTopic(device_id: str) -> str:
    """Get the topic for the device."""
    return f"$aws/things/{device_id}/shadow/update"


class AwsIot:
    """Class to handle AWS IoT operations."""

    def __init__(
        self,
        region_name: str,
        access_key_id: str,
        secret_access_key: str,
        session_token: str,
    ) -> None:
        """Initialize the AWS IoT client."""

        s = boto3.session.Session(
            region_name=region_name,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            aws_session_token=session_token,
        )

        # _LOGGER.info("AwsIot.get_available_services: %s", s.get_available_services())

        self.client = s.client(service_name="iot-data")

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
