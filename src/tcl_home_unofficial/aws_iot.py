"""."""

import datetime
import json
import logging

import boto3
import boto3.session

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

        self.client = boto3Session.client(service_name="iot-data")

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
            device_url=clud_urls.data.device_url,
            saas_token=saas_token,
            country_abbr=authResult.user.country_abbr,
            verbose_logging=self.session_manager.is_verbose_device_logging(),
        )

        return things

    async def execute_and_re_try_call_with_device_id(
        self, function, device_id: str, fromException: bool = False
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

    async def execute_and_re_try_call_with_device_id_and_value(
        self, function, device_id: str, value: int, fromException: bool = False
    ):
        try:
            return await self.hass.async_add_executor_job(function, device_id, value)
        except Exception as e:
            # re-try if the error is due to expired credentials
            if not fromException:
                self.client.close()
                await self.async_setup_client()
                return await self.execute_and_re_try_call_with_device_id_and_value(
                    function=function,
                    device_id=device_id,
                    value=value,
                    fromException=True,
                )
            _LOGGER.error(
                "Aws_iot - Error execute_and_re_try_call_with_device_id_and_value %s - %s | %s",
                device_id,
                value,
                e,
            )
            raise e

    async def async_get_thing(
        self, device_id: str, fromException: bool = False
    ) -> dict:
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

    async def async_set_power(
        self, device_id: str, value: SleepModeEnum, fromException: bool = False
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_power, device_id, value, fromException
        )

    def set_power(self, device_id: str, value: int) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info("AwsIot.power: %s - %s", device_id, value)
        payload = json.dumps(
            {
                "state": {"desired": {"powerSwitch": value}},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )
        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)

    async def async_set_beep_mode(
        self, device_id: str, value: SleepModeEnum, fromException: bool = False
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_beep_mode, device_id, value, fromException
        )

    def set_beep_mode(self, device_id: str, value: int) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info("AwsIot.beep_mode: %s - %s", device_id, value)
        payload = json.dumps(
            {
                "state": {"desired": {"beepSwitch": value}},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )
        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)

    async def async_set_target_temperature(
        self, device_id: str, value: int, fromException: bool = False
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_target_temperature, device_id, value, fromException
        )

    def set_target_temperature(self, device_id: str, value: int) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info("AwsIot.set_target_temperature: %s -> %s", device_id, value)

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

    async def async_set_mode(
        self, device_id: str, value: ModeEnum, fromException: bool = False
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_mode, device_id, value, fromException
        )

    def set_mode(self, device_id: str, value: ModeEnum) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info("AwsIot.set_mode: %s -> %s", device_id, value)

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

    async def async_set_wind_speed(
        self, device_id: str, value: WindSeedEnum, fromException: bool = False
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_wind_speed, device_id, value, fromException
        )

    def set_wind_speed(self, device_id: str, value: WindSeedEnum) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info("AwsIot.set_wind_speed: %s -> %s", device_id, value)

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

    async def async_set_up_and_down_air_supply_vector(
        self,
        device_id: str,
        value: UpAndDownAirSupplyVectorEnum,
        fromException: bool = False,
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_up_and_down_air_supply_vector, device_id, value, fromException
        )

    def set_up_and_down_air_supply_vector(
        self, device_id: str, value: UpAndDownAirSupplyVectorEnum
    ) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info(
                "AwsIot.set_up_and_down_air_supply_vector: %s -> %s",
                device_id,
                value,
            )
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
        self,
        device_id: str,
        value: LeftAndRightAirSupplyVectorEnum,
        fromException: bool = False,
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_left_and_right_air_supply_vector, device_id, value, fromException
        )

    def set_left_and_right_air_supply_vector(
        self, device_id: str, value: LeftAndRightAirSupplyVectorEnum
    ) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info(
                "AwsIot.set_left_and_right_air_supply_vector: %s -> %s",
                device_id,
                value,
            )
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

    async def async_set_sleep_mode(
        self, device_id: str, value: SleepModeEnum, fromException: bool = False
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_sleep_mode, device_id, value, fromException
        )

    def set_sleep_mode(self, device_id: str, value: SleepModeEnum) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info("AwsIot.set_sleep_mode: %s -> %s", device_id, value)
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

    async def async_set_eco(
        self, device_id: str, value: SleepModeEnum, fromException: bool = False
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_eco, device_id, value, fromException
        )

    def set_eco(self, device_id: str, value: int) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info("AwsIot.set_eco: %s - %s", device_id, value)
        if value == 1:
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
        else:
            payload = json.dumps(
                {
                    "state": {"desired": {"ECO": 0}},
                    "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
                }
            )
        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)

    async def async_set_healthy(
        self, device_id: str, value: SleepModeEnum, fromException: bool = False
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_healthy, device_id, value, fromException
        )

    def set_healthy(self, device_id: str, value: int) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info("AwsIot.set_healthy: %s - %s", device_id, value)
        payload = json.dumps(
            {
                "state": {"desired": {"healthy": value}},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )
        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)

    async def async_set_drying(
        self, device_id: str, value: SleepModeEnum, fromException: bool = False
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_drying, device_id, value, fromException
        )

    def set_drying(self, device_id: str, value: int) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info("AwsIot.set_drying: %s - %s", device_id, value)
        payload = json.dumps(
            {
                "state": {"desired": {"antiMoldew": value}},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )
        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)

    async def async_set_self_clean(
        self, device_id: str, value: SleepModeEnum, fromException: bool = False
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_self_clean, device_id, value, fromException
        )

    def set_self_clean(self, device_id: str, value: int) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info("AwsIot.set_self_clean: %s - %s", device_id, value)
        if value == 1:
            payload = json.dumps(
                {
                    "state": {"desired": {"powerSwitch": 0, "selfClean": 1}},
                    "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
                }
            )
        else:
            payload = json.dumps(
                {
                    "state": {"desired": {"selfClean": 0}},
                    "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
                }
            )
        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)

    async def async_set_light(
        self, device_id: str, value: SleepModeEnum, fromException: bool = False
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_light, device_id, value, fromException
        )

    def set_light(self, device_id: str, value: int) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info("AwsIot.set_light: %s - %s", device_id, value)
        payload = json.dumps(
            {
                "state": {"desired": {"screen": value}},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )
        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)
