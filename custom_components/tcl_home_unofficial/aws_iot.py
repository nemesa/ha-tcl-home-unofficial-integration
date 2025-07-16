"""."""

import datetime
import json
import logging

import boto3
import boto3.session

from homeassistant.core import HomeAssistant

from .config_entry import New_NameConfigEntry
from .device_ac_common import (
    LeftAndRightAirSupplyVectorEnum,
    UpAndDownAirSupplyVectorEnum,
    ModeEnum,
    SleepModeEnum,
)
from .device import DeviceTypeEnum
from .device_spit_ac import WindSeedEnum
from .device_spit_ac_fresh_air import (
    WindSeed7GearEnum,
    GeneratorModeEnum,
    FreshAirEnum,
    WindFeelingEnum,
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

    async def execute_and_re_try_call_with_device_id_and_value(
        self,
        function,
        device_id: str,
        deviceType: DeviceTypeEnum,
        value: int | float,
        fromException: bool = False,
    ):
        try:
            return await self.hass.async_add_executor_job(
                function, device_id, deviceType, value
            )
        except Exception as e:
            # re-try if the error is due to expired credentials
            if not fromException:
                self.client.close()
                await self.async_setup_client()
                return await self.execute_and_re_try_call_with_device_id_and_value(
                    function=function,
                    device_id=device_id,
                    deviceType=deviceType,
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
        self,
        device_id: str,
        deviceType: DeviceTypeEnum,
        value: int,
        fromException: bool = False,
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_power, device_id, deviceType, value, fromException
        )

    def set_power(self, device_id: str, deviceType: DeviceTypeEnum, value: int) -> None:
        turnOffBeep = (
            self.session_manager.get_config_data().behavior_mute_beep_on_power_on
        )

        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info(
                "AwsIot.power: (%s) %s - %s (turnOffBeep:%s)",
                deviceType,
                device_id,
                value,
                turnOffBeep,
            )

        desired = {"powerSwitch": value}

        if turnOffBeep and value == 1:
            desired["beepSwitch"] = 0

        payload = json.dumps(
            {
                "state": {"desired": desired},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )
        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)

    async def async_set_beep_mode(
        self,
        device_id: str,
        deviceType: DeviceTypeEnum,
        value: int,
        fromException: bool = False,
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_beep_mode, device_id, deviceType, value, fromException
        )

    def set_beep_mode(
        self, device_id: str, deviceType: DeviceTypeEnum, value: int
    ) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info("AwsIot.beep_mode: (%s) %s - %s", deviceType, device_id, value)
        payload = json.dumps(
            {
                "state": {"desired": {"beepSwitch": value}},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )
        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)

    async def async_set_target_temperature(
        self,
        device_id: str,
        deviceType: DeviceTypeEnum,
        value: int | float,
        fromException: bool = False,
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_target_temperature, device_id, deviceType, value, fromException
        )

    def set_target_temperature(
        self, device_id: str, deviceType: DeviceTypeEnum, value: int
    ) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info(
                "AwsIot.set_target_temperature: (%s) %s - %s",
                deviceType,
                device_id,
                value,
            )

        min_temp = 16
        max_temp = 36

        if deviceType == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
            max_temp = 31

        if value < min_temp or value > max_temp:
            _LOGGER.error(
                "Invalid target temperature: %s (Min:%s Max:%s)",
                value,
                min_temp,
                max_temp,
            )
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
        self,
        device_id: str,
        deviceType: DeviceTypeEnum,
        value: ModeEnum,
        fromException: bool = False,
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_mode, device_id, deviceType, value, fromException
        )

    def set_mode(
        self, device_id: str, deviceType: DeviceTypeEnum, value: ModeEnum
    ) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info("AwsIot.set_mode: (%s) %s - %s", deviceType, device_id, value)

        desired = {}
        match value:
            case ModeEnum.AUTO:
                if deviceType == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired = {
                        "windSpeedAutoSwitch": 1,
                        "workMode": 0,
                        "windSpeed7Gear": 0,
                    }
                else:
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
                if deviceType == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired = {
                        "windSpeedAutoSwitch": 0,
                        "workMode": 1,
                        "windSpeed7Gear": 6,
                    }
                else:
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
                if deviceType == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired = {
                        "windSpeedAutoSwitch": 0,
                        "workMode": 2,
                        "windSpeed7Gear": 2,
                    }
                else:
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
                if deviceType == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired = {
                        "windSpeedAutoSwitch": 1,
                        "workMode": 3,
                        "windSpeed7Gear": 0,
                    }
                else:
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
                if deviceType == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired = {
                        "windSpeedAutoSwitch": 1,
                        "workMode": 4,
                        "windSpeed7Gear": 0,
                    }
                else:
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

    async def async_set_wind_7_gear_speed(
        self,
        device_id: str,
        deviceType: DeviceTypeEnum,
        value: WindSeed7GearEnum,
        fromException: bool = False,
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_wind_7_gear_speed, device_id, deviceType, value, fromException
        )

    def set_wind_7_gear_speed(
        self, device_id: str, deviceType: DeviceTypeEnum, value: WindSeed7GearEnum
    ) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info(
                "AwsIot.set_wind_7_gear_speed: (%s) %s - %s",
                deviceType,
                device_id,
                value,
            )

        desired = {}
        match value:
            case WindSeed7GearEnum.AUTO:
                desired = {"windSpeedAutoSwitch": 1, "windSpeed7Gear": 0}
            case WindSeed7GearEnum.TURBO:
                desired = {"windSpeedAutoSwitch": 0, "windSpeed7Gear": 7}
            case WindSeed7GearEnum.SPEED_1:
                desired = {"windSpeedAutoSwitch": 0, "windSpeed7Gear": 1}
            case WindSeed7GearEnum.SPEED_2:
                desired = {"windSpeedAutoSwitch": 0, "windSpeed7Gear": 2}
            case WindSeed7GearEnum.SPEED_3:
                desired = {"windSpeedAutoSwitch": 0, "windSpeed7Gear": 3}
            case WindSeed7GearEnum.SPEED_4:
                desired = {"windSpeedAutoSwitch": 0, "windSpeed7Gear": 4}
            case WindSeed7GearEnum.SPEED_5:
                desired = {"windSpeedAutoSwitch": 0, "windSpeed7Gear": 5}
            case WindSeed7GearEnum.SPEED_6:
                desired = {"windSpeedAutoSwitch": 0, "windSpeed7Gear": 6}

        payload = json.dumps(
            {
                "state": {"desired": desired},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )

        _LOGGER.info(
            "AwsIot.set_wind_7_gear_speed: (%s) %s - %s",
            deviceType,
            device_id,
            value,
        )

        self.client.publish(
            topic=getTopic(device_id),
            qos=1,
            payload=payload,
        )

    async def async_set_wind_speed(
        self,
        device_id: str,
        deviceType: DeviceTypeEnum,
        value: WindSeedEnum,
        fromException: bool = False,
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_wind_speed, deviceType, device_id, value, fromException
        )

    def set_wind_speed(
        self, device_id: str, deviceType: DeviceTypeEnum, value: WindSeedEnum
    ) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info(
                "AwsIot.set_wind_speed: (%s) %s - %s", deviceType, device_id, value
            )

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
        deviceType: DeviceTypeEnum,
        value: UpAndDownAirSupplyVectorEnum,
        fromException: bool = False,
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_up_and_down_air_supply_vector,
            device_id,
            deviceType,
            value,
            fromException,
        )

    def set_up_and_down_air_supply_vector(
        self,
        device_id: str,
        deviceType: DeviceTypeEnum,
        value: UpAndDownAirSupplyVectorEnum,
    ) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info(
                "AwsIot.set_up_and_down_air_supply_vector: (%s) %s - %s",
                deviceType,
                device_id,
                value,
            )
        desired = {}
        match value:
            case UpAndDownAirSupplyVectorEnum.UP_AND_DOWN_SWING:
                if deviceType == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired = {"verticalDirection": 1}
                else:
                    desired = {"verticalSwitch": 1, "verticalDirection": 1}
            case UpAndDownAirSupplyVectorEnum.UPWARDS_SWING:
                if deviceType == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired = {"verticalDirection": 2}
                else:
                    desired = {"verticalSwitch": 1, "verticalDirection": 2}
            case UpAndDownAirSupplyVectorEnum.DOWNWARDS_SWING:
                if deviceType == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired = {"verticalDirection": 3}
                else:
                    desired = {"verticalSwitch": 1, "verticalDirection": 3}
            case UpAndDownAirSupplyVectorEnum.TOP_FIX:
                if deviceType == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired = {"verticalDirection": 9}
                else:
                    desired = {"verticalSwitch": 0, "verticalDirection": 9}
            case UpAndDownAirSupplyVectorEnum.UPPER_FIX:
                if deviceType == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired = {"verticalDirection": 10}
                else:
                    desired = {"verticalSwitch": 0, "verticalDirection": 10}
            case UpAndDownAirSupplyVectorEnum.MIDDLE_FIX:
                if deviceType == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired = {"verticalDirection": 11}
                else:
                    desired = {"verticalSwitch": 0, "verticalDirection": 11}
            case UpAndDownAirSupplyVectorEnum.LOWER_FIX:
                if deviceType == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired = {"verticalDirection": 12}
                else:
                    desired = {"verticalSwitch": 0, "verticalDirection": 12}
            case UpAndDownAirSupplyVectorEnum.BOTTOM_FIX:
                if deviceType == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired = {"verticalDirection": 13}
                else:
                    desired = {"verticalSwitch": 0, "verticalDirection": 13}
            case UpAndDownAirSupplyVectorEnum.NOT_SET:
                if deviceType == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired = {"verticalDirection": 8}
                else:
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
        deviceType: DeviceTypeEnum,
        value: LeftAndRightAirSupplyVectorEnum,
        fromException: bool = False,
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_left_and_right_air_supply_vector,
            device_id,
            deviceType,
            value,
            fromException,
        )

    def set_left_and_right_air_supply_vector(
        self,
        device_id: str,
        deviceType: DeviceTypeEnum,
        value: LeftAndRightAirSupplyVectorEnum,
    ) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info(
                "AwsIot.set_left_and_right_air_supply_vector: (%s) %s - %s",
                deviceType,
                device_id,
                value,
            )
        desired = {}
        match value:
            case LeftAndRightAirSupplyVectorEnum.LEFT_AND_RIGHT_SWING:
                if deviceType == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired = {"horizontalDirection": 1}
                else:
                    desired = {"horizontalDirection": 1, "horizontalSwitch": 1}
            case LeftAndRightAirSupplyVectorEnum.LEFT_SWING:
                if deviceType == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired = {"horizontalDirection": 2}
                else:
                    desired = {"horizontalDirection": 2, "horizontalSwitch": 1}
            case LeftAndRightAirSupplyVectorEnum.MIDDLE_SWING:
                if deviceType == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired = {"horizontalDirection": 3}
                else:
                    desired = {"horizontalDirection": 3, "horizontalSwitch": 1}
            case LeftAndRightAirSupplyVectorEnum.RIGHT_SWING:
                if deviceType == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired = {"horizontalDirection": 4}
                else:
                    desired = {"horizontalDirection": 4, "horizontalSwitch": 1}
            case LeftAndRightAirSupplyVectorEnum.LEFT_FIX:
                if deviceType == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired = {"horizontalDirection": 9}
                else:
                    desired = {"horizontalDirection": 9, "horizontalSwitch": 0}
            case LeftAndRightAirSupplyVectorEnum.CENTER_LEFT_FIX:
                if deviceType == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired = {"horizontalDirection": 10}
                else:
                    desired = {"horizontalDirection": 10, "horizontalSwitch": 0}
            case LeftAndRightAirSupplyVectorEnum.MIDDLE_FIX:
                if deviceType == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired = {"horizontalDirection": 11}
                else:
                    desired = {"horizontalDirection": 11, "horizontalSwitch": 0}
            case LeftAndRightAirSupplyVectorEnum.CENTER_RIGHT_FIX:
                if deviceType == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired = {"horizontalDirection": 12}
                else:
                    desired = {"horizontalDirection": 12, "horizontalSwitch": 0}
            case LeftAndRightAirSupplyVectorEnum.RIGHT_FIX:
                if deviceType == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired = {"horizontalDirection": 13}
                else:
                    desired = {"horizontalDirection": 13, "horizontalSwitch": 0}
            case LeftAndRightAirSupplyVectorEnum.NOT_SET:
                if deviceType == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    desired = {"horizontalDirection": 8}
                else:
                    desired = {"horizontalDirection": 8, "horizontalSwitch": 0}

        payload = json.dumps(
            {
                "state": {"desired": desired},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )

        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)

    async def async_set_sleep_mode(
        self,
        device_id: str,
        deviceType: DeviceTypeEnum,
        value: SleepModeEnum,
        fromException: bool = False,
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_sleep_mode, device_id, deviceType, value, fromException
        )

    def set_sleep_mode(
        self, device_id: str, deviceType: DeviceTypeEnum, value: SleepModeEnum
    ) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info(
                "AwsIot.set_sleep_mode: (%s) %s - %s", deviceType, device_id, value
            )
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
        self,
        device_id: str,
        deviceType: DeviceTypeEnum,
        value: int,
        fromException: bool = False,
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_eco, device_id, deviceType, value, fromException
        )

    def set_eco(self, device_id: str, deviceType: DeviceTypeEnum, value: int) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info("AwsIot.set_eco: (%s) %s - %s", deviceType, device_id, value)
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
        self,
        device_id: str,
        deviceType: DeviceTypeEnum,
        value: int,
        fromException: bool = False,
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_healthy, device_id, deviceType, value, fromException
        )

    def set_healthy(
        self, device_id: str, deviceType: DeviceTypeEnum, value: int
    ) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info(
                "AwsIot.set_healthy: (%s) %s - %s", deviceType, device_id, value
            )
        payload = json.dumps(
            {
                "state": {"desired": {"healthy": value}},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )
        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)

    async def async_set_drying(
        self,
        device_id: str,
        deviceType: DeviceTypeEnum,
        value: int,
        fromException: bool = False,
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_drying, device_id, deviceType, value, fromException
        )

    def set_drying(
        self, device_id: str, deviceType: DeviceTypeEnum, value: int
    ) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info(
                "AwsIot.set_drying: (%s) %s - %s", deviceType, device_id, value
            )
        payload = json.dumps(
            {
                "state": {"desired": {"antiMoldew": value}},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )
        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)

    async def async_set_self_clean(
        self,
        device_id: str,
        deviceType: DeviceTypeEnum,
        value: int,
        fromException: bool = False,
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_self_clean, device_id, deviceType, value, fromException
        )

    def set_self_clean(
        self, device_id: str, deviceType: DeviceTypeEnum, value: int
    ) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info(
                "AwsIot.set_self_clean: (%s) %s - %s", deviceType, device_id, value
            )
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

    async def async_set_generator_mode(
        self,
        device_id: str,
        deviceType: DeviceTypeEnum,
        value: GeneratorModeEnum,
        fromException: bool = False,
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_generator_mode, device_id, deviceType, value, fromException
        )

    def set_generator_mode(
        self, device_id: str, deviceType: DeviceTypeEnum, value: GeneratorModeEnum
    ) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info(
                "AwsIot.set_generator_mode: (%s) %s - %s", deviceType, device_id, value
            )
        desired = {}
        match value:
            case GeneratorModeEnum.NONE:
                desired = {"generatorMode": 0}
            case GeneratorModeEnum.L1:
                desired = {"generatorMode": 1}
            case GeneratorModeEnum.L2:
                desired = {"generatorMode": 2}
            case GeneratorModeEnum.L3:
                desired = {"generatorMode": 3}

        payload = json.dumps(
            {
                "state": {"desired": desired},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )
        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)

    async def async_set_fresh_air(
        self,
        device_id: str,
        deviceType: DeviceTypeEnum,
        value: FreshAirEnum,
        fromException: bool = False,
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_fresh_air, device_id, deviceType, value, fromException
        )

    def set_fresh_air(
        self, device_id: str, deviceType: DeviceTypeEnum, value: FreshAirEnum
    ) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info(
                "AwsIot.set_fresh_air: (%s) %s - %s", deviceType, device_id, value
            )
        desired = {}
        match value:
            case FreshAirEnum.OFF:
                desired = {"newWindSwitch": 0}
            case FreshAirEnum.ON:
                desired = {"newWindSwitch": 1, "selfClean": 0}
            case FreshAirEnum.AUTO:
                desired = {"newWindAutoSwitch": 1, "newWindStrength": 0}
            case FreshAirEnum.STRENGTH_1:
                desired = {"newWindAutoSwitch": 0, "newWindStrength": 1}
            case FreshAirEnum.STRENGTH_2:
                desired = {"newWindAutoSwitch": 0, "newWindStrength": 2}
            case FreshAirEnum.STRENGTH_3:
                desired = {"newWindAutoSwitch": 0, "newWindStrength": 3}

        payload = json.dumps(
            {
                "state": {"desired": desired},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )
        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)

    async def async_set_wind_feeling(
        self,
        device_id: str,
        deviceType: DeviceTypeEnum,
        value: WindFeelingEnum,
        fromException: bool = False,
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_wind_feeling, device_id, deviceType, value, fromException
        )

    def set_wind_feeling(
        self, device_id: str, deviceType: DeviceTypeEnum, value: FreshAirEnum
    ) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info(
                "AwsIot.set_fresh_air: (%s) %s - %s", deviceType, device_id, value
            )
        desired = {}
        match value:
            case WindFeelingEnum.NONE:
                desired = {"softWind": 0}
            case WindFeelingEnum.SOFT:
                desired = {"horizontalDirection": 8, "softWind": 1}
            case WindFeelingEnum.SHOWER:
                desired = {
                    "horizontalDirection": 8,
                    "softWind": 2,
                    "verticalDirection": 9,
                }
            case WindFeelingEnum.CARPET:
                desired = {
                    "horizontalDirection": 8,
                    "softWind": 3,
                    "verticalDirection": 13,
                }
            case WindFeelingEnum.SURROUND:
                desired = {"softWind": 4, "verticalDirection": 8}
        payload = json.dumps(
            {
                "state": {"desired": desired},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )
        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)

    async def async_set_light(
        self,
        device_id: str,
        deviceType: DeviceTypeEnum,
        value: int,
        fromException: bool = False,
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_light, device_id, deviceType, value, fromException
        )

    def set_light(self, device_id: str, deviceType: DeviceTypeEnum, value: int) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info("AwsIot.set_light: (%s) %s - %s", deviceType, device_id, value)
        payload = json.dumps(
            {
                "state": {"desired": {"screen": value}},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )
        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)

    async def async_set_light_sense(
        self,
        device_id: str,
        deviceType: DeviceTypeEnum,
        value: int,
        fromException: bool = False,
    ) -> None:
        await self.execute_and_re_try_call_with_device_id_and_value(
            self.set_light_sense, device_id, deviceType, value, fromException
        )

    def set_light_sense(
        self, device_id: str, deviceType: DeviceTypeEnum, value: int
    ) -> None:
        if self.session_manager.is_verbose_device_logging():
            _LOGGER.info(
                "AwsIot.set_light_sense: (%s) %s - %s", deviceType, device_id, value
            )
        payload = json.dumps(
            {
                "state": {"desired": {"lightSense": value}},
                "clientToken": f"mobile_{int(datetime.datetime.now().timestamp())}",
            }
        )
        self.client.publish(topic=getTopic(device_id), qos=1, payload=payload)
