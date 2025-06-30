"""."""

import datetime
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
        _LOGGER.debug("AwsIot.getThing: %s", payload)
        return json.loads(payload)

    async def async_turnOn(self, device_id: str) -> dict:
        return await self.hass.async_add_executor_job(self.turnOn, device_id)

    def turnOn(self, device_id: str) -> None:
        """Turn on the device."""
        payload = json.dumps(
            {
                "state": {"desired": {"powerSwitch": 1}},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )

        self.client.publish(
            topic=getTopic(device_id),
            qos=1,
            payload=payload,
        )

    async def async_turnOff(self, device_id: str) -> dict:
        return await self.hass.async_add_executor_job(self.turnOff, device_id)

    def turnOff(self, device_id: str) -> None:
        """Turn off the device."""

        payload = json.dumps(
            {
                "state": {"desired": {"beepSwitch": 0, "powerSwitch": 0}},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )

        self.client.publish(
            topic=getTopic(device_id),
            qos=1,
            payload=payload,
        )

    async def async_beepModeOn(self, device_id: str) -> dict:
        return await self.hass.async_add_executor_job(self.beepModeOn, device_id)

    def beepModeOn(self, device_id: str) -> None:
        """Turn on the device."""
        payload = json.dumps(
            {
                "state": {"desired": {"beepSwitch": 1}},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )

        self.client.publish(
            topic=getTopic(device_id),
            qos=1,
            payload=payload,
        )

    async def async_beepModeOff(self, device_id: str) -> dict:
        return await self.hass.async_add_executor_job(self.beepModeOff, device_id)

    def beepModeOff(self, device_id: str) -> None:
        """Turn on the device."""
        payload = json.dumps(
            {
                "state": {"desired": {"beepSwitch": 0}},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )

        self.client.publish(
            topic=getTopic(device_id),
            qos=1,
            payload=payload,
        )

    async def async_set_target_temperature(self, device_id: str, value: int) -> dict:
        return await self.hass.async_add_executor_job(
            self.set_target_temperature, device_id, value
        )

    def set_target_temperature(self, device_id: str, value: int) -> None:
        """target_temperature"""

        if value < 16 or value > 36:
            _LOGGER.error("Invalid target temperature: %s (Min:16 Max:36)", value)
            return

        payload = json.dumps(
            {
                "state": {"desired": {"targetTemperature": value}},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )

        self.client.publish(
            topic=getTopic(device_id),
            qos=1,
            payload=payload,
        )


"""
Set temp:
{"state":{"desired":{"targetTemperature":24}},"clientToken":"mobile_1751204074276"}

Mode:
    Heat:               {"state":{"desired":{"ECO":0,"sleep":0,"eightAddHot":0,"highTemperatureWind":0,"workMode":4,"horizontalSwitch":0,"healthy":0,"turbo":0,"antiMoldew":0,"verticalSwitch":0,"silenceSwitch":0,"windSpeed":0,"targetTemperature":26}},"clientToken":"mobile_1751204153486"}
    Cool:               {"state":{"desired":{"ECO":0,"sleep":0,"eightAddHot":0,"highTemperatureWind":0,"workMode":1,"horizontalSwitch":0,"healthy":0,"turbo":0,"antiMoldew":0,"verticalSwitch":0,"silenceSwitch":0,"windSpeed":0,"targetTemperature":24}},"clientToken":"mobile_1751204177597"}
    Dehumidification:   {"state":{"desired":{"ECO":0,"sleep":0,"eightAddHot":0,"highTemperatureWind":0,"workMode":2,"horizontalSwitch":0,"healthy":0,"turbo":0,"antiMoldew":0,"verticalSwitch":0,"silenceSwitch":0,"windSpeed":2}},"clientToken":"mobile_1751204217632"}
    Fan:                {"state":{"desired":{"ECO":0,"sleep":0,"eightAddHot":0,"highTemperatureWind":0,"workMode":3,"horizontalSwitch":0,"healthy":0,"turbo":0,"antiMoldew":0,"verticalSwitch":0,"silenceSwitch":0,"windSpeed":0}},"clientToken":"mobile_1751204240310"}
    Auto:               {"state":{"desired":{"ECO":0,"sleep":0,"eightAddHot":0,"highTemperatureWind":0,"workMode":0,"horizontalSwitch":0,"healthy":0,"turbo":0,"antiMoldew":0,"verticalSwitch":0,"silenceSwitch":0,"windSpeed":0}},"clientToken":"mobile_1751204294720"}


ECO
    off:    {"state":{"desired":{"ECO":0}},"clientToken":"mobile_1751204342594"}
    on:     {"state":{"desired":{"ECO":1,"highTemperatureWind":0,"turbo":0,"silenceSwitch":0,"windSpeed":0}},"clientToken":"mobile_1751204352037"}


Wind speed
    Strong:     {"state":{"desired":{"highTemperatureWind":0,"turbo":1,"silenceSwitch":0,"windSpeed":6}},"clientToken":"mobile_1751204651154"}
    High:       {"state":{"desired":{"highTemperatureWind":0,"turbo":0,"silenceSwitch":0,"windSpeed":6}},"clientToken":"mobile_1751204631338"}
    Mid-heigh:  {"state":{"desired":{"highTemperatureWind":0,"turbo":0,"silenceSwitch":0,"windSpeed":5}},"clientToken":"mobile_1751204672229"}
    Medium:     {"state":{"desired":{"highTemperatureWind":0,"turbo":0,"silenceSwitch":0,"windSpeed":4}},"clientToken":"mobile_1751204690883"}
    Meid-low:   {"state":{"desired":{"highTemperatureWind":0,"turbo":0,"silenceSwitch":0,"windSpeed":3}},"clientToken":"mobile_1751204700777"}
    Low:        {"state":{"desired":{"highTemperatureWind":0,"turbo":0,"silenceSwitch":0,"windSpeed":2}},"clientToken":"mobile_1751204730849"}
    Mute:       {"state":{"desired":{"highTemperatureWind":0,"turbo":0,"silenceSwitch":1,"windSpeed":2}},"clientToken":"mobile_1751204605846"}
    Auto:       {"state":{"desired":{"highTemperatureWind":0,"turbo":0,"silenceSwitch":0,"windSpeed":0}},"clientToken":"mobile_1751204747959"}

Vector air suply
    Up and down air supply:
       Up and down swing:   {"state":{"desired":{"verticalSwitch":1,"verticalDirection":1}},"clientToken":"mobile_1751204861067"}
       Upwards swing:       {"state":{"desired":{"verticalSwitch":1,"verticalDirection":2}},"clientToken":"mobile_1751205332778"}
       Downwards swing:     {"state":{"desired":{"verticalSwitch":1,"verticalDirection":3}},"clientToken":"mobile_1751205314705"}
       Top fix:             {"state":{"desired":{"verticalSwitch":0,"verticalDirection":9}},"clientToken":"mobile_1751205304708"}
       Upper fix:           {"state":{"desired":{"verticalSwitch":0,"verticalDirection":10}},"clientToken":"mobile_1751205290466"}
       Middle fix:          {"state":{"desired":{"verticalSwitch":0,"verticalDirection":11}},"clientToken":"mobile_1751205282178"}
       Lower fix:           {"state":{"desired":{"verticalSwitch":0,"verticalDirection":12}},"clientToken":"mobile_1751205271681"}
       Bottom fix:          {"state":{"desired":{"verticalSwitch":0,"verticalDirection":13}},"clientToken":"mobile_1751205257810"}

    Left and right air supply:
       Left and right swing:    {"state":{"desired":{"horizontalDirection":1,"horizontalSwitch":1}},"clientToken":"mobile_1751205419975"}
       Left swing:              {"state":{"desired":{"horizontalDirection":2,"horizontalSwitch":1}},"clientToken":"mobile_1751205412750"}
       Middle swing:            {"state":{"desired":{"horizontalDirection":3,"horizontalSwitch":1}},"clientToken":"mobile_1751205425043"}
       Right swing:             {"state":{"desired":{"horizontalDirection":4,"horizontalSwitch":1}},"clientToken":"mobile_1751205430446"}
       Left fix:                {"state":{"desired":{"horizontalDirection":9,"horizontalSwitch":0}},"clientToken":"mobile_1751205438845"}
       Center-left fix:         {"state":{"desired":{"horizontalDirection":10,"horizontalSwitch":0}},"clientToken":"mobile_1751205447260"}
       Middle fix:              {"state":{"desired":{"horizontalDirection":11,"horizontalSwitch":0}},"clientToken":"mobile_1751205453333"}
       Center-right fix:        {"state":{"desired":{"horizontalDirection":12,"horizontalSwitch":0}},"clientToken":"mobile_1751205459761"}
       Right fix:               {"state":{"desired":{"horizontalDirection":13,"horizontalSwitch":0}},"clientToken":"mobile_1751205466193"}


Sleep mode:
    Standard:   {"state":{"desired":{"sleep":1}},"clientToken":"mobile_1751205551124"}
    Elderly:    {"state":{"desired":{"sleep":2}},"clientToken":"mobile_1751205561522"}
    Child:      {"state":{"desired":{"sleep":3}},"clientToken":"mobile_1751205567750"}
    OFF:        {"state":{"desired":{"sleep":0}},"clientToken":"mobile_1751205583040"}


Helath mode:
    OFF:        {"state":{"desired":{"healthy":0}},"clientToken":"mobile_1751205631269"}
    ON:         {"state":{"desired":{"healthy":1}},"clientToken":"mobile_1751205600761"}

drying:
    ON: {"state":{"desired":{"antiMoldew":1}},"clientToken":"mobile_1751205646706"}
    OFF {"state":{"desired":{"antiMoldew":1}},"clientToken":"mobile_1751205646706"}

"""
