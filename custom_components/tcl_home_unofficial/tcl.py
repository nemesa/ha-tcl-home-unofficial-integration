"""."""
from dataclasses import dataclass
import datetime
import hashlib
import logging
import random
import string
import time

import jwt
from homeassistant.core import HomeAssistant
from homeassistant.helpers.httpx_client import get_async_client

_LOGGER = logging.getLogger(__name__)


def getValue(data: dict, keys: list[str]) -> str:
    """Get value from dictionary with fallback."""
    value = None

    for key in keys:
        if key in data:
            value = data[key]
            break

    return value

def safeGetValue(data: dict, keys: list[str], defaultValue) -> str:
    """Get value from dictionary with fallback."""
    value = getValue(data, keys)
    
    if value is None:
        value = defaultValue

    return value

@dataclass
class DoAccountAuthResponseUser:
    def __init__(self, data: dict) -> None:
        self.country_abbr = getValue(data, ["country_abbr", "countryAbbr"])
        self.username = getValue(data, ["username"])
        self.nickname = getValue(data, ["nickname"])

    country_abbr: str
    username: str
    nickname: str


@dataclass
class DoAccountAuthResponse:
    def __init__(self, data: dict) -> None:
        self.status = getValue(data, ["status"])
        if self.status == 1:
            self.token = getValue(data, ["token"])
            self.refresh_token = getValue(data, ["refresh_token", "refreshtoken"])
            self.user = DoAccountAuthResponseUser(data["user"])

    token: str
    status: int
    refresh_token: str
    user: DoAccountAuthResponseUser


@dataclass
class RefreshTokensResponseData:
    def __init__(self, data: dict) -> None:
        self.saas_token = getValue(data, ["saas_token", "saasToken"])
        self.cognito_token = getValue(data, ["cognito_token", "cognitoToken"])
        self.cognito_id = getValue(data, ["cognito_id", "cognitoId"])
        self.mqtt_endpoint = getValue(data, ["mqtt_endpoint", "mqttEndpoint"])

    saas_token: str
    cognito_token: str
    cognito_id: str
    mqtt_endpoint: str


@dataclass
class RefreshTokensResponse:
    def __init__(self, data: dict) -> None:
        self.data = RefreshTokensResponseData(data["data"])
        self.code = getValue(data, ["code"])
        self.message = getValue(data, ["message"])

    code: int
    message: str
    data: RefreshTokensResponseData


@dataclass
class CloudUrlsResponseData:
    def __init__(self, data: dict) -> None:
        self.sso_region = getValue(data, ["sso_region"])
        self.cloud_region = getValue(data, ["cloud_region"])
        self.sso_url = getValue(data, ["sso_url"])
        self.cloud_url = getValue(data, ["cloud_url"])
        self.icon_resource_url = getValue(data, ["icon_resource_url"])
        self.identity_pool_id = getValue(data, ["identity_pool_id"])
        self.upload_web_url = getValue(data, ["upload_web_url"])
        self.device_url = getValue(data, ["device_url"])
        self.cloud_url_emq = getValue(data, ["cloud_url_emq"])
        self.new_struct = getValue(data, ["new_struct", "newStruct"])

    sso_region: str
    cloud_region: str
    sso_url: str
    cloud_url: str
    icon_resource_url: str
    identity_pool_id: str
    upload_web_url: str
    device_url: str
    cloud_url_emq: str
    new_struct: int


@dataclass
class CloudUrlsResponse:
    def __init__(self, data: dict) -> None:
        self.data = CloudUrlsResponseData(data["data"])
        self.code = getValue(data, ["code"])
        self.message = getValue(data, ["message"])

    code: int
    message: str
    data: CloudUrlsResponseData


@dataclass
class GetThingsResponseData:
    def __init__(self, data: dict) -> None:
        self.device_id = getValue(data, ["device_id", "deviceId"])
        self.product_key = getValue(data, ["product_key", "productKey"])
        self.platform = getValue(data, ["platform"])
        self.nick_name = getValue(data, ["nick_name", "nickName"])
        self.device_name = getValue(data, ["device_name", "deviceName"])
        self.category = getValue(data, ["category"])
        self.firmware_version = getValue(data, ["firmware_version", "firmwareVersion"])
        self.is_online = int(getValue(data, ["is_online", "isOnline"]))
        self.room = getValue(data, ["room"])
        self.type = getValue(data, ["type"])
        self.net_type = getValue(data, ["net_type", "netType"])
        self.device_type = getValue(data, ["device_type", "deviceType"])
        if self.room is None:
            if data["labels"] and len(data["labels"]) > 0:
                for label in data["labels"]:
                    if label["labelKey"] == "room":
                        self.room = label["labelValue"]
                        break

        if self.nick_name is None and self.room is not None:
            self.nick_name = self.room

    device_id: str
    platform: str
    nick_name: str
    device_name: str
    category: str
    firmware_version: str
    is_online: int
    room: str
    type: int
    device_type: str
    net_type: int


@dataclass
class GetThingsResponse:
    def __init__(self, data: dict) -> None:
        self.code = getValue(data, ["code"])
        self.message = getValue(data, ["message"])
        self.data = [GetThingsResponseData(item) for item in data["data"]]

    code: int
    message: str
    data: list[GetThingsResponseData]


@dataclass
class GetAwsCredentialsResponseCredentials:
    def __init__(self, data: dict) -> None:
        self.access_key_id = getValue(data, ["access_key_id", "AccessKeyId"])
        self.expiration = int(getValue(data, ["expiration", "Expiration"]))
        self.secret_key = getValue(data, ["secret_key", "SecretKey"])
        self.session_token = getValue(data, ["session_token", "SessionToken"])

    access_key_id: str
    expiration: int
    secret_key: str
    session_token: str


@dataclass
class GetAwsCredentialsResponse:
    def __init__(self, data: dict) -> None:
        self.Credentials = GetAwsCredentialsResponseCredentials(data["Credentials"])
        self.identity_id = getValue(data, ["IdentityId", "identity_id"])

    identity_id: str
    Credentials: GetAwsCredentialsResponseCredentials


@dataclass
class GetWorkTimeResponseDataItem:
    def __init__(self, data: dict) -> None:
        if data:
            self.date = getValue(data, ["date"])
            self.work_time = getValue(data, ["work_time", "workTime"])
            self.ai_work_time = getValue(data, ["ai_work_time", "aiWorkTime"])

    date: str
    work_time: float
    ai_work_time: float

@dataclass
class GetWorkTimeResponseData:
    def __init__(self, data: dict) -> None:
        if data:
            self.device_id = getValue(data, ["device_id", "deviceId"])
            self.date = getValue(data, ["date"])
            self.time_zone = getValue(data, ["time_zone", "timeZone"])
            self.time_offset = getValue(data, ["time_offset", "timeOffset"])
            self.current_total_work_time = GetWorkTimeResponseDataItem(safeGetValue(data, ["current_total_work_time","currentTotalWorkTime"],None))
            self.before_total_work_time = GetWorkTimeResponseDataItem(safeGetValue(data, ["before_total_work_time","beforeTotalWorkTime"],None))
            self.work_time_details = [GetWorkTimeResponseDataItem(item) for item in safeGetValue(data, ["work_time_details","workTimeDetails"],[])]
        
    device_id: str
    date: str
    time_zone: str
    time_offset: str
    current_total_work_time: GetWorkTimeResponseDataItem
    before_total_work_time: GetWorkTimeResponseDataItem
    work_time_details: list[GetWorkTimeResponseDataItem]
    
@dataclass
class GetWorkTimeResponse:
    def __init__(self, data: dict) -> None:        
        self.code = getValue(data, ["code"])
        self.message = getValue(data, ["message"])
        self.data = GetWorkTimeResponseData(safeGetValue(data, ["data"],{}))

    code: int
    message: str
    data: GetWorkTimeResponseData
    


@dataclass
class GetEnergyConsumptioneResponseDataItem:
    def __init__(self, data: dict) -> None:
        if data:
            self.date = getValue(data, ["date"])
            self.consumption = getValue(data, ["consumption"])
            self.ai_consumption = getValue(data, ["ai_consumption", "aiConsumption"])

    date: str
    consumption: float
    ai_consumption: float

@dataclass
class GetEnergyConsumptioneResponseDataResult:
    def __init__(self, data: dict) -> None:
        if data:
            self.date = getValue(data, ["date"])
            self.offline_electricity = getValue(data, ["offline_electricity", "offlineElectricity"])
            self.total_electricity = getValue(data, ["total_electricity", "totalElectricity"])
            self.online_electricity = getValue(data, ["online_electricity", "onlineElectricity"])
            self.ai_electricity = getValue(data, ["ai_electricity", "aiElectricity"])

    date: str
    offline_electricity: float
    total_electricity: float
    online_electricity: float
    ai_electricity: float


@dataclass
class GetEnergyConsumptioneResponseData:
    def __init__(self, data: dict) -> None:    
        self.device_id = getValue(data, ["device_id", "deviceId"])
        self.date = getValue(data, ["date"])
        self.time_zone = getValue(data, ["time_zone", "timeZone"])
        self.time_offset = getValue(data, ["time_offset", "timeOffset"])
        self.curr_statistics_res = GetEnergyConsumptioneResponseDataResult(safeGetValue(data, ["curr_statistics_res","currStatisticsRes"],None))
        self.before_statistics_res = GetEnergyConsumptioneResponseDataResult(safeGetValue(data, ["before_statistics_res","beforeStatisticsRes"],None))
        self.consumption_details = [GetEnergyConsumptioneResponseDataItem(item) for item in safeGetValue(data, ["consumption_details","consumptionDetails"],[])]
        
    device_id: str
    date: str
    time_zone: str
    time_offset: str
    curr_statistics_res: GetEnergyConsumptioneResponseDataResult
    before_statistics_res: GetEnergyConsumptioneResponseDataResult
    work_time_details: list[GetEnergyConsumptioneResponseDataItem]
    
@dataclass
class GetEnergyConsumptioneResponse:
    def __init__(self, data: dict) -> None:
        self.code = getValue(data, ["code"])
        self.message = getValue(data, ["message"])
        self.data = GetEnergyConsumptioneResponseData(safeGetValue(data, ["data"],{}))

    code: int
    message: str
    data: GetEnergyConsumptioneResponseData    

async def do_account_auth(
    hass: HomeAssistant,
    username: str,
    password: str,
    login_url: str,
    verbose_logging: bool = False,
) -> DoAccountAuthResponse:
    if verbose_logging:
        _LOGGER.info("TCL-Service.do_account_auth: %s", login_url)
    pw = hashlib.md5(password.encode("utf-8")).hexdigest()

    payload = {
        "equipment": 2,
        "password": pw,
        "osType": 1,
        "username": username,
        "clientVersion": "4.8.1",
        "osVersion": "6.0",
        "deviceModel": "AndroidAndroid SDK built for x86",
        "captchaRule": 2,
        "channel": "app",
    }

    headers = {
        "th_platform": "android",
        "th_version": "4.8.1",
        "th_appbulid": "830",
        "user-agent": "Android",
        "content-type": "application/json; charset=UTF-8",
    }

    httpx_client = get_async_client(hass)
    response = await httpx_client.post(login_url, json=payload, headers=headers, timeout=15)

    response_obj = response.json()
    if verbose_logging:
        _LOGGER.info("TCL-Service.do_account_auth response: %s", response_obj)
    if response.status_code == 200:
        authResponse = DoAccountAuthResponse(response_obj)
        if authResponse.status == 1:
            return authResponse
    return None


async def get_cloud_urls(
    hass: HomeAssistant,
    cloud_urls: str,
    username: str,
    token: str,
    verbose_logging: bool = False,
) -> CloudUrlsResponse:
    if verbose_logging:
        _LOGGER.info("TCL-Service.get_cloud_urls: %s", cloud_urls)

    payload = {"ssoId": username, "ssoToken": token}

    headers = {
        "user-agent": "Android",
        "content-type": "application/json; charset=UTF-8",
    }

    httpx_client = get_async_client(hass)
    response = await httpx_client.post(cloud_urls, json=payload, headers=headers, timeout=15)
    response_obj = response.json()
    if verbose_logging:
        _LOGGER.info("TCL-Service.get_cloud_urls response: %s", response_obj)
    if response.status_code == 200:
        return CloudUrlsResponse(response_obj)
    return None


async def refreshTokens(
    hass: HomeAssistant,
    refresh_tokens_url: str,
    username: str,
    accessToken: str,
    appId: str,
    verbose_logging: bool = False,
) -> RefreshTokensResponse:
    url = f"{refresh_tokens_url}/v3/auth/refresh_tokens"
    if verbose_logging:
        _LOGGER.info("TCL-Service.refreshTokens: %s", url)

    payload = {
        "userId": username,
        "ssoToken": accessToken,
        "appId": appId,
    }

    headers = {
        "user-agent": "Android",
        "content-type": "application/json; charset=UTF-8",
        "accept-encoding": "gzip, deflate, br",
    }

    httpx_client = get_async_client(hass)
    response = await httpx_client.post(url, json=payload, headers=headers, timeout=15)
    response_obj = response.json()
    if verbose_logging:
        _LOGGER.info("TCL-Service.refreshTokens response: %s", response_obj)
    if response.status_code == 200:
        return RefreshTokensResponse(response_obj)
    return None


async def get_aws_credentials(
    hass: HomeAssistant,
    aws_region: str,
    cognitoToken: str,
    verbose_logging: bool = False,
) -> GetAwsCredentialsResponse:
    url = f"https://cognito-identity.{aws_region}.amazonaws.com/"

    if verbose_logging:
        _LOGGER.info("TCL-Service.get_aws_credentials: %s", url)
    identity_pool_id = get_sub_from_jwt_token(cognitoToken)

    payload = {
        "IdentityId": identity_pool_id,
        "Logins": {"cognito-identity.amazonaws.com": cognitoToken},
    }

    headers = {
        "User-agent": "aws-sdk-android/2.22.6 Linux/6.1.23-android14-4-00257-g7e35917775b8-ab9964412 Dalvik/2.1.0/0 en_US",
        "X-Amz-Target": "AWSCognitoIdentityService.GetCredentialsForIdentity",
        "content-type": "application/x-amz-json-1.1",
    }

    httpx_client = get_async_client(hass)
    response = await httpx_client.post(url, json=payload, headers=headers, timeout=15)
    response_obj = response.json()
    if verbose_logging:
        _LOGGER.info("TCL-Service.get_aws_credentials response: %s", response_obj)
    if response.status_code == 200:
        return GetAwsCredentialsResponse(response_obj)
    return None


async def get_things(
    hass: HomeAssistant,
    device_url: str,
    saas_token: str,
    country_abbr: str,
    verbose_logging: bool = False,
) -> GetThingsResponse:
    url = f"{device_url}/v3/user/get_things"
    if verbose_logging:
        _LOGGER.info("TCL-Service.get_things: %s", url)
    timestamp = str(int(time.time() * 1000))
    nonce = "".join(
        random.choices(string.ascii_lowercase + string.digits, k=16)
    )  # similar to Math.random().toString(36)
    sign = calculate_md5_hash_bytes(timestamp + nonce + saas_token)

    headers = {
        "platform": "android",
        "appversion": "5.4.1",
        "thomeversion": "4.8.1",
        "accesstoken": saas_token,
        #"countrycode": country_abbr,
        "accept-language": "en",
        "timestamp": timestamp,
        "nonce": nonce,
        "sign": sign,
        "user-agent": "Android",
        "content-type": "application/json; charset=UTF-8",
        "accept-encoding": "gzip, deflate, br",
    }    

    httpx_client = get_async_client(hass)

    response = await httpx_client.post(url, json={}, headers=headers, timeout=15)
    if response.status_code != 200:
        raise Exception("Error at get_things: " + response.text)
    response_obj = response.json()
    # _LOGGER.info("TCL-Service.get_things: %s", response_obj)
    if verbose_logging:
        _LOGGER.info("TCL-Service.get_things response: %s", response_obj)
    return GetThingsResponse(response_obj)




async def get_work_time(
    hass: HomeAssistant,
    device_url: str,
    saas_token: str,
    deviceId: str,
    date_filter: str,
    verbose_logging: bool = False,
) -> GetWorkTimeResponse:
    """
    date filter samples: 
        week:  ?week=20250928-20251004
        month: /2025/10
        year:  /2025
        
    """
    url = f"{device_url}/v3/ac/{deviceId}/work-time/info{date_filter}"
    if verbose_logging:
        _LOGGER.info("TCL-Service.get_work_time: %s", url)
    timestamp = str(int(time.time() * 1000))
    nonce = "".join(
        random.choices(string.ascii_lowercase + string.digits, k=16)
    )  # similar to Math.random().toString(36)
    sign = calculate_md5_hash_bytes(timestamp + nonce + saas_token)

    headers = {
        "platform": "android",
        "timestamp": timestamp,
        "nonce": nonce,
        "sign": sign,
        "user-agent": "Android",
        "appversion": "5.4.1",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en",
        "accesstoken": saas_token,        
    }    

    httpx_client = get_async_client(hass)

    response = await httpx_client.get(url, headers=headers, timeout=15)
    if response.status_code != 200:
        raise Exception("Error at get_work_time: " + response.text)
    response_obj = response.json()
    # _LOGGER.info("TCL-Service.get_work_time: %s", response_obj)
    if verbose_logging:
        _LOGGER.info("TCL-Service.get_work_time response: %s", response_obj)
    return GetWorkTimeResponse(response_obj)



async def get_energy_consumption(
    hass: HomeAssistant,
    device_url: str,
    saas_token: str,
    deviceId: str,
    date_filter: str,
    verbose_logging: bool = False,
) -> GetEnergyConsumptioneResponse:
    """
    date filter samples: 
        week:  ?week=20250928-20251004
        month: /2025/10
        year:  /2025
        
    """
    url = f"{device_url}/v3/ac/{deviceId}/power/consumption/info/{date_filter}"
    if verbose_logging:
        _LOGGER.info("TCL-Service.get_energy_consumption: %s", url)        
    
    timestamp = str(int(time.time() * 1000))
    nonce = "".join(
        random.choices(string.ascii_lowercase + string.digits, k=16)
    )  # similar to Math.random().toString(36)
    sign = calculate_md5_hash_bytes(timestamp + nonce + saas_token)

    headers = {
        "platform": "android",
        "timestamp": timestamp,
        "nonce": nonce,
        "sign": sign,
        "user-agent": "Android",
        "appversion": "5.4.1",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en",
        "accesstoken": saas_token,   
    }    

    httpx_client = get_async_client(hass)

    response = await httpx_client.get(url, headers=headers, timeout=15)
    if response.status_code != 200:
        raise Exception("Error at get_energy_consumption: " + response.text)
    response_obj = response.json()
    # _LOGGER.info("TCL-Service.get_energy_consumption: %s", response_obj)
    if verbose_logging:
        _LOGGER.info("TCL-Service.get_energy_consumption response: %s", response_obj)
    return GetEnergyConsumptioneResponse(response_obj)

@dataclass
class ConfigGetResponse:
    def __init__(self, data: dict) -> None:
        self.code = getValue(data, ["code"])
        self.message = getValue(data, ["message"])
        # Store full payload from the API under .data (no filtering)
        self.data = data.get("data", data)

    code: int | None
    message: str | None
    data: dict


async def get_config(
    hass: HomeAssistant,
    cloud_url: str,
    saas_token: str,
    country_abbr: str | None = None,
    product_key: str | None = None,
    verbose_logging: bool = False,
) -> ConfigGetResponse | None:
    """Call `/v3/config/get` and return the full response.

    Stores the entire payload under `.data` without adding convenience fields
    or aliases. Callers should access fields directly from `.data`.
    """
    url = f"{cloud_url}/v3/config/get"
    if verbose_logging:
        _LOGGER.info("TCL-Service.get_config: %s (productKey=%s)", url, product_key)

    payload = {}
    if product_key:
        payload["productKey"] = product_key
    if country_abbr:
        payload["countryCode"] = country_abbr

    timestamp = str(int(time.time() * 1000))
    nonce = "".join(random.choices(string.ascii_lowercase + string.digits, k=16))
    sign = calculate_md5_hash_bytes(timestamp + nonce + saas_token)

    headers = {
        "platform": "android",
        "appversion": "5.4.1",
        "thomeversion": "4.8.1",
        "accesstoken": saas_token,
        "accept-language": "en",
        "timestamp": timestamp,
        "nonce": nonce,
        "sign": sign,
        "user-agent": "Android",
        "content-type": "application/json; charset=UTF-8",
        "accept-encoding": "gzip, deflate, br",
    }

    httpx_client = get_async_client(hass)
    response = await httpx_client.post(url, json=payload, headers=headers, timeout=15)
    if response.status_code != 200:
        if verbose_logging:
            _LOGGER.error(
                "TCL-Service.get_config: HTTP %s - %s",
                response.status_code,
                response.text,
            )
        return None

    resp_json = response.json()
    if verbose_logging:
        _LOGGER.info("TCL-Service.get_config response: %s", resp_json)

    return ConfigGetResponse(resp_json)


def calculate_md5_hash_bytes(input_str: str) -> str:
    try:
        digest = hashlib.md5(input_str.encode("utf-8")).digest()
        hex_chars = []
        for b in digest:
            byte_value = b & 0xFF
            if byte_value < 16:
                hex_chars.append("0")
            hex_chars.append(format(byte_value, "x"))
        return "".join(hex_chars)
    except Exception:
        _LOGGER.exception("Error calculating MD5 hash")
        return ""


def get_sub_from_jwt_token(token: str) -> str:
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded.get("sub", "")
    except Exception as e:
        _LOGGER.error("Error decoding JWT token: %s", e)
        return ""


def check_if_jwt_expired(
    tokenName: str, jwt_token: str, exp_property_name: str
) -> bool:
    """Check if the JWT token is expired."""
    try:
        decoded = jwt.decode(jwt_token, options={"verify_signature": False})
        exp = int(decoded.get(exp_property_name, "0"))
        now = datetime.datetime.now().timestamp()

        is_expired = exp < now
        _LOGGER.debug(
            "JWT token (%s) expiration check: exp=%s, now=%s (is_expired=%s)",
            tokenName,
            exp,
            now,
            is_expired,
        )

        return is_expired
    except Exception as e:
        _LOGGER.error("Error decoding JWT token: %s", e)
        return ""


def check_if_expired(exp) -> bool:
    """Check if the given expiration time is in the past."""
    now = datetime.datetime.now().timestamp()
    is_expired = exp < now
    return is_expired

def get_day_for_filer(addDays=0) -> str:    
    time=datetime.datetime.now()+ datetime.timedelta(days=addDays)    
    return time.strftime("%Y%m%d")

def get_day_for_data(addDays=0) -> str:    
    time=datetime.datetime.now()+ datetime.timedelta(days=addDays)    
    return time.strftime("%Y-%m-%d")