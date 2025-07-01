"""."""

import datetime
import json
import logging

import boto3
import boto3.session
from botocore.utils import SSOTokenLoader

from homeassistant.core import HomeAssistant

from .config_entry import New_NameConfigEntry
from .device import (
    LeftAndRightAirSupplyVectorEnum,
    ModeEnum,
    SleepModeEnum,
    UpAndDownAirSupplyVectorEnum,
    WindSeedEnum,
)
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

    async def async_setup_client(self) -> None:
        awsCred = await self.session_manager.async_aws_credentials()

        boto3Session = boto3.session.Session(
            region_name=self.region_name,
            aws_access_key_id=awsCred.Credentials.access_key_id,
            aws_secret_access_key=awsCred.Credentials.secret_key,
            aws_session_token=awsCred.Credentials.session_token,
        )

        # credentials = boto3Session.get_credentials().get_frozen_credentials()
        # _LOGGER.info("Aws:iot - credentials:%s", credentials)
        # SSOTokenLoader.load(

        # token = boto3Session.get_auth_token()
        # _LOGGER.info("Aws:iot - token:%s", token)

        self.client = boto3Session.client(service_name="iot-data")

    async def async_init(self) -> None:
        await self.session_manager.async_load()
        await self.async_setup_client()

    async def get_all_things(self) -> GetThingsResponse:
        authResult = await self.session_manager.async_get_auth_data()
        refreshTokensResult = await self.session_manager.async_refresh_tokens()
        saas_token = refreshTokensResult.data.saas_token

        things = await get_things(saas_token, authResult.user.country_abbr)

        return things

    async def async_get_thing(
        self, device_id: str, fromException: bool = False
    ) -> dict:
        try:
            return await self.hass.async_add_executor_job(self.get_thing, device_id)
        except Exception as e:
            _LOGGER.error("Aws_iot - Error getting thing %s: %s", device_id, e)
            if not fromException:
                self.client.close()
                await self.async_setup_client()
                return await self.async_get_thing(device_id, True)
            raise e

    def get_thing(self, device_id: str) -> dict:
        """List all things in AWS IoT."""
        response = self.client.get_thing_shadow(thingName=device_id)
        payload = response["payload"].read().decode("utf-8")
        _LOGGER.debug("AwsIot.getThing: %s", payload)
        return json.loads(payload)

    async def async_turn_on(self, device_id: str) -> None:
        await self.hass.async_add_executor_job(self.turn_on, device_id)

    def turn_on(self, device_id: str) -> None:
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

    async def async_turn_off(self, device_id: str) -> None:
        await self.hass.async_add_executor_job(self.turn_off, device_id)

    def turn_off(self, device_id: str) -> None:
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

    async def async_beep_mode_on(self, device_id: str) -> None:
        await self.hass.async_add_executor_job(self.beep_mode_on, device_id)

    def beep_mode_on(self, device_id: str) -> None:
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

    async def async_beep_mode_off(self, device_id: str) -> None:
        await self.hass.async_add_executor_job(self.beep_mode_off, device_id)

    def beep_mode_off(self, device_id: str) -> None:
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

    async def async_set_target_temperature(self, device_id: str, value: int) -> None:
        await self.hass.async_add_executor_job(
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

    async def async_set_mode(self, device_id: str, value: ModeEnum) -> None:
        await self.hass.async_add_executor_job(self.set_mode, device_id, value)

    def set_mode(self, device_id: str, value: ModeEnum) -> None:
        """target_temperature"""

        desired = {}
        match value:
            case ModeEnum.AUTO:
                desired = {
                    "ECO": 0,
                    "sleep": 0,
                    "eightAddHot": 0,
                    "highTemperatureWind": 0,
                    "workMode": 0,
                    "horizontalSwitch": 0,
                    "healthy": 0,
                    "turbo": 0,
                    "antiMoldew": 0,
                    "verticalSwitch": 0,
                    "silenceSwitch": 0,
                    "windSpeed": 0,
                }
            case ModeEnum.COOL:
                desired = {
                    "ECO": 0,
                    "sleep": 0,
                    "eightAddHot": 0,
                    "highTemperatureWind": 0,
                    "workMode": 1,
                    "horizontalSwitch": 0,
                    "healthy": 0,
                    "turbo": 0,
                    "antiMoldew": 0,
                    "verticalSwitch": 0,
                    "silenceSwitch": 0,
                    "windSpeed": 0,
                    "targetTemperature": 24,
                }
            case ModeEnum.DEHUMIDIFICATION:
                desired = {
                    "ECO": 0,
                    "sleep": 0,
                    "eightAddHot": 0,
                    "highTemperatureWind": 0,
                    "workMode": 2,
                    "horizontalSwitch": 0,
                    "healthy": 0,
                    "turbo": 0,
                    "antiMoldew": 0,
                    "verticalSwitch": 0,
                    "silenceSwitch": 0,
                    "windSpeed": 2,
                }
            case ModeEnum.FAN:
                desired = {
                    "ECO": 0,
                    "sleep": 0,
                    "eightAddHot": 0,
                    "highTemperatureWind": 0,
                    "workMode": 3,
                    "horizontalSwitch": 0,
                    "healthy": 0,
                    "turbo": 0,
                    "antiMoldew": 0,
                    "verticalSwitch": 0,
                    "silenceSwitch": 0,
                    "windSpeed": 0,
                }
            case ModeEnum.HEAT:
                desired = {
                    "ECO": 0,
                    "sleep": 0,
                    "eightAddHot": 0,
                    "highTemperatureWind": 0,
                    "workMode": 4,
                    "horizontalSwitch": 0,
                    "healthy": 0,
                    "turbo": 0,
                    "antiMoldew": 0,
                    "verticalSwitch": 0,
                    "silenceSwitch": 0,
                    "windSpeed": 0,
                    "targetTemperature": 26,
                }

        payload = json.dumps(
            {
                "state": {"desired": desired},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )

        self.client.publish(
            topic=getTopic(device_id),
            qos=1,
            payload=payload,
        )

    async def async_set_wind_speed(self, device_id: str, value: WindSeedEnum) -> None:
        await self.hass.async_add_executor_job(self.set_wind_speed, device_id, value)

    def set_wind_speed(self, device_id: str, value: WindSeedEnum) -> None:
        """target_temperature"""

        desired = {}
        match value:
            case WindSeedEnum.STRONG:
                desired = {
                    "highTemperatureWind": 0,
                    "turbo": 1,
                    "silenceSwitch": 0,
                    "windSpeed": 6,
                }
            case WindSeedEnum.HEIGH:
                desired = {
                    "highTemperatureWind": 0,
                    "turbo": 0,
                    "silenceSwitch": 0,
                    "windSpeed": 6,
                }
            case WindSeedEnum.MID_HEIGH:
                desired = {
                    "highTemperatureWind": 0,
                    "turbo": 0,
                    "silenceSwitch": 0,
                    "windSpeed": 5,
                }
            case WindSeedEnum.MEDIUM:
                desired = {
                    "highTemperatureWind": 0,
                    "turbo": 0,
                    "silenceSwitch": 0,
                    "windSpeed": 4,
                }
            case WindSeedEnum.MID_LOW:
                desired = {
                    "highTemperatureWind": 0,
                    "turbo": 0,
                    "silenceSwitch": 0,
                    "windSpeed": 3,
                }
            case WindSeedEnum.LOW:
                desired = {
                    "highTemperatureWind": 0,
                    "turbo": 0,
                    "silenceSwitch": 0,
                    "windSpeed": 2,
                }
            case WindSeedEnum.MUTE:
                desired = {
                    "highTemperatureWind": 0,
                    "turbo": 0,
                    "silenceSwitch": 1,
                    "windSpeed": 2,
                }
            case WindSeedEnum.AUTO:
                desired = {
                    "highTemperatureWind": 0,
                    "turbo": 0,
                    "silenceSwitch": 0,
                    "windSpeed": 0,
                }

        payload = json.dumps(
            {
                "state": {"desired": desired},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )

        self.client.publish(
            topic=getTopic(device_id),
            qos=1,
            payload=payload,
        )

    async def async_eco_turn_on(self, device_id: str) -> None:
        await self.hass.async_add_executor_job(self.eco_turn_on, device_id)

    def eco_turn_on(self, device_id: str) -> None:
        payload = json.dumps(
            {
                "state": {
                    "desired": {
                        "ECO": 1,
                        "highTemperatureWind": 0,
                        "turbo": 0,
                        "silenceSwitch": 0,
                        "windSpeed": 0,
                    }
                },
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )

        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)

    async def async_eco_turn_off(self, device_id: str) -> None:
        await self.hass.async_add_executor_job(self.eco_turn_off, device_id)

    def eco_turn_off(self, device_id: str) -> None:
        payload = json.dumps(
            {
                "state": {"desired": {"ECO": 0}},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )

        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)

    async def async_healthy_turn_on(self, device_id: str) -> None:
        await self.hass.async_add_executor_job(self.healthy_turn_on, device_id)

    def healthy_turn_on(self, device_id: str) -> None:
        payload = json.dumps(
            {
                "state": {"desired": {"healthy": 1}},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )

        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)

    async def async_healthy_turn_off(self, device_id: str) -> None:
        await self.hass.async_add_executor_job(self.healthy_turn_off, device_id)

    def healthy_turn_off(self, device_id: str) -> None:
        payload = json.dumps(
            {
                "state": {"desired": {"healthy": 0}},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )

        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)

    async def async_drying_turn_on(self, device_id: str) -> None:
        await self.hass.async_add_executor_job(self.drying_turn_on, device_id)

    def drying_turn_on(self, device_id: str) -> None:
        payload = json.dumps(
            {
                "state": {"desired": {"antiMoldew": 1}},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )

        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)

    async def async_drying_turn_off(self, device_id: str) -> None:
        await self.hass.async_add_executor_job(self.drying_turn_off, device_id)

    def drying_turn_off(self, device_id: str) -> None:
        payload = json.dumps(
            {
                "state": {"desired": {"antiMoldew": 0}},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )

        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)

    async def async_set_up_and_down_air_supply_vector(
        self, device_id: str, value: UpAndDownAirSupplyVectorEnum
    ) -> None:
        await self.hass.async_add_executor_job(
            self.set_up_and_down_air_supply_vector, device_id, value
        )

    def set_up_and_down_air_supply_vector(
        self, device_id: str, value: UpAndDownAirSupplyVectorEnum
    ) -> None:
        desired = {}
        match value:
            case UpAndDownAirSupplyVectorEnum.UP_AND_DOWN_SWING:
                desired = {"verticalSwitch": 1, "verticalDirection": 1}
            case UpAndDownAirSupplyVectorEnum.UPWARDS_SWING:
                desired = {"verticalSwitch": 1, "verticalDirection": 2}
            case UpAndDownAirSupplyVectorEnum.DOWNWARDS_SWING:
                desired = {"verticalSwitch": 1, "verticalDirection": 3}
            case UpAndDownAirSupplyVectorEnum.TOP_FIX:
                desired = {"verticalSwitch": 0, "verticalDirection": 9}
            case UpAndDownAirSupplyVectorEnum.UPPER_FIX:
                desired = {"verticalSwitch": 0, "verticalDirection": 10}
            case UpAndDownAirSupplyVectorEnum.MIDDLE_FIX:
                desired = {"verticalSwitch": 0, "verticalDirection": 11}
            case UpAndDownAirSupplyVectorEnum.LOWER_FIX:
                desired = {"verticalSwitch": 0, "verticalDirection": 12}
            case UpAndDownAirSupplyVectorEnum.BOTTOM_FIX:
                desired = {"verticalSwitch": 0, "verticalDirection": 13}
            case UpAndDownAirSupplyVectorEnum.NOT_SET:
                desired = {"verticalSwitch": 0, "verticalDirection": 8}

        payload = json.dumps(
            {
                "state": {"desired": desired},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )

        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)

    async def async_set_left_and_right_air_supply_vector(
        self, device_id: str, value: LeftAndRightAirSupplyVectorEnum
    ) -> None:
        await self.hass.async_add_executor_job(
            self.set_left_and_right_air_supply_vector, device_id, value
        )

    def set_left_and_right_air_supply_vector(
        self, device_id: str, value: LeftAndRightAirSupplyVectorEnum
    ) -> None:
        desired = {}
        match value:
            case LeftAndRightAirSupplyVectorEnum.LEFT_AND_RIGHT_SWING:
                desired = {"horizontalDirection": 1, "horizontalSwitch": 1}
            case LeftAndRightAirSupplyVectorEnum.LEFT_SWING:
                desired = {"horizontalDirection": 2, "horizontalSwitch": 1}
            case LeftAndRightAirSupplyVectorEnum.MIDDLE_SWING:
                desired = {"horizontalDirection": 3, "horizontalSwitch": 1}
            case LeftAndRightAirSupplyVectorEnum.RIGHT_SWING:
                desired = {"horizontalDirection": 4, "horizontalSwitch": 1}
            case LeftAndRightAirSupplyVectorEnum.LEFT_FIX:
                desired = {"horizontalDirection": 9, "horizontalSwitch": 0}
            case LeftAndRightAirSupplyVectorEnum.CENTER_LEFT_FIX:
                desired = {"horizontalDirection": 10, "horizontalSwitch": 0}
            case LeftAndRightAirSupplyVectorEnum.MIDDLE_FIX:
                desired = {"horizontalDirection": 11, "horizontalSwitch": 0}
            case LeftAndRightAirSupplyVectorEnum.CENTER_RIGHT_FIX:
                desired = {"horizontalDirection": 12, "horizontalSwitch": 0}
            case LeftAndRightAirSupplyVectorEnum.RIGHT_FIX:
                desired = {"horizontalDirection": 13, "horizontalSwitch": 0}
            case LeftAndRightAirSupplyVectorEnum.NOT_SET:
                desired = {"horizontalDirection": 8, "horizontalSwitch": 0}

        payload = json.dumps(
            {
                "state": {"desired": desired},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )

        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)

    async def async_set_sleep_mode(self, device_id: str, value: SleepModeEnum) -> None:
        await self.hass.async_add_executor_job(self.set_sleep_mode, device_id, value)

    def set_sleep_mode(self, device_id: str, value: SleepModeEnum) -> None:
        desired = {}
        match value:
            case SleepModeEnum.STANDARD:
                desired = {"sleep": 1}
            case SleepModeEnum.ELDERLY:
                desired = {"sleep": 2}
            case SleepModeEnum.CHILD:
                desired = {"sleep": 3}
            case SleepModeEnum.OFF:
                desired = {"sleep": 0}

        payload = json.dumps(
            {
                "state": {"desired": desired},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )

        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)

    async def async_self_clean_start(self, device_id: str) -> None:
        await self.hass.async_add_executor_job(self.self_clean_start, device_id)

    def self_clean_start(self, device_id: str) -> None:
        payload = json.dumps(
            {
                "state": {"desired": {"powerSwitch": 0, "selfClean": 1}},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )

        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)

    async def async_self_clean_stop(self, device_id: str) -> None:
        await self.hass.async_add_executor_job(self.self_clean_stop, device_id)

    def self_clean_stop(self, device_id: str) -> None:
        payload = json.dumps(
            {
                "state": {"desired": {"selfClean": 0}},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )

        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)

    async def async_light_turn_on(self, device_id: str) -> None:
        await self.hass.async_add_executor_job(self.light_turn_on, device_id)

    def light_turn_on(self, device_id: str) -> None:
        payload = json.dumps(
            {
                "state": {"desired": {"screen": 1}},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )

        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)

    async def async_light_turn_off(self, device_id: str) -> None:
        await self.hass.async_add_executor_job(self.light_turn_off, device_id)

    def light_turn_off(self, device_id: str) -> None:
        payload = json.dumps(
            {
                "state": {"desired": {"screen": 0}},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )

        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)
