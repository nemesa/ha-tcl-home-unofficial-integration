"""."""

from dataclasses import dataclass
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers import storage

from .config_entry import ConfigData, New_NameConfigEntry, convertToConfigData
from .const import DOMAIN
from .tcl import (
    DoAccountAuthResponse,
    GetAwsCredentialsResponse,
    RefreshTokensResponse,
    check_if_expired,
    check_if_jwt_expired,
    do_account_auth,
    get_aws_credentials,
    refreshTokens,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class StorageData:
    authData: DoAccountAuthResponse | None = None
    refreshTokensData: RefreshTokensResponse | None = None
    awsCredentialsData: GetAwsCredentialsResponse | None = None


class SessionManager:
    def __init__(
        self,
        hass: HomeAssistant,
        configData: ConfigData | None = None,
        config_entry: New_NameConfigEntry | None = None,
    ) -> None:
        if configData is not None:
            self.configData = configData
        else:
            self.configData = convertToConfigData(config_entry)

        self._store: storage.Store[dict] = storage.Store(
            hass=hass, version=1, key=DOMAIN
        )
        self.storageData = StorageData(
            authData=None, refreshTokensData=None, awsCredentialsData=None
        )

    def is_verbose_device_logging(self) -> bool:
        return self.configData.verbose_device_logging

    def is_verbose_session_logging(self) -> bool:
        return self.configData.verbose_session_logging

    def is_verbose_setup_logging(self) -> bool:
        return self.configData.verbose_setup_logging

    def get_aws_region(self) -> str:
        return self.configData.aws_region

    async def async_load(self) -> StorageData:
        """Load the stored data."""
        storageData = StorageData(
            authData=None, refreshTokensData=None, awsCredentialsData=None
        )
        data = await self._store.async_load()
        if data is None:
            if self.is_verbose_session_logging():
                _LOGGER.info(
                    "SessionManager.async_load: No data found, creating new StorageData"
                )
        else:
            if self.is_verbose_session_logging():
                _LOGGER.info("SessionManager.async_load: Data found, load StorageData")
            if data.get("authData") is not None:
                storageData.authData = DoAccountAuthResponse(data["authData"])
            else:
                if self.is_verbose_session_logging():
                    _LOGGER.info("SessionManager.async_load authData is None")

            if data.get("refreshTokensData") is not None:
                storageData.refreshTokensData = RefreshTokensResponse(
                    data["refreshTokensData"]
                )
            else:
                if self.is_verbose_session_logging():
                    _LOGGER.info("SessionManager.async_load refreshTokensData is None")

            if data.get("awsCredentialsData") is not None:
                storageData.awsCredentialsData = GetAwsCredentialsResponse(
                    data["awsCredentialsData"]
                )
            else:
                if self.is_verbose_session_logging():
                    _LOGGER.info("SessionManager.async_load awsCredentialsData is None")

        if self.is_verbose_session_logging():
            _LOGGER.info("SessionManager.async_load done")
        self.storageData = storageData
        return storageData

    async def clear_storage(self) -> None:
        if self.is_verbose_session_logging():
            _LOGGER.info("SessionManager.clear_storage")
        self.storageData.refreshTokensData = None
        self.storageData.authData = None
        self.storageData.awsCredentialsData = None
        await self._store.async_save(data=self.storageData)
        await self.async_load()

    async def async_force_get_auth_data(self) -> DoAccountAuthResponse:
        if self.is_verbose_session_logging():
            _LOGGER.info("SessionManager.async_force_get_auth_data")
        authData = await do_account_auth(
            username=self.configData.username,
            password=self.configData.password,
            clientId=self.configData.app_client_id,
            verbose_logging=self.is_verbose_session_logging(),
        )

        self.storageData.authData = authData
        await self._store.async_save(data=self.storageData)
        return authData

    async def async_get_auth_data(self) -> DoAccountAuthResponse:
        if self.storageData.authData is not None:
            if self.is_verbose_session_logging():
                _LOGGER.debug("SessionManager.async_get_auth_data.resolve from storage")
            if check_if_jwt_expired(
                "authData.token", self.storageData.authData.token, "exp"
            ):
                if self.is_verbose_session_logging():
                    _LOGGER.debug("SessionManager.async_get_auth_data token expired")
                return await self.async_force_get_auth_data()

            if check_if_jwt_expired(
                "authData.refresh_token", self.storageData.authData.refresh_token, "exp"
            ):
                if self.is_verbose_session_logging():
                    _LOGGER.debug(
                        "SessionManager.async_get_auth_data refresh_token expired"
                    )
                return await self.async_force_get_auth_data()
            return self.storageData.authData

        return await self.async_force_get_auth_data()

    async def async_force_refresh_tokens(self) -> RefreshTokensResponse:
        if self.is_verbose_session_logging():
            _LOGGER.info("SessionManager.async_force_refresh_tokens")
        authData = await self.async_get_auth_data()

        refreshTokensData = await refreshTokens(
            username=authData.user.username,
            accessToken=authData.token,
            appId=self.configData.app_id,
            verbose_logging=self.is_verbose_session_logging(),
        )

        self.storageData.refreshTokensData = refreshTokensData
        await self._store.async_save(data=self.storageData)
        return refreshTokensData

    async def async_refresh_tokens(self) -> RefreshTokensResponse:
        if self.storageData.refreshTokensData is not None:
            if self.is_verbose_session_logging():
                _LOGGER.debug(
                    "SessionManager.async_refresh_tokens.resolve from storage"
                )

            if check_if_jwt_expired(
                "saas_token",
                self.storageData.refreshTokensData.data.saas_token,
                "expiredDate",
            ):
                if self.is_verbose_session_logging():
                    _LOGGER.debug(
                        "SessionManager.async_refresh_tokens saas_token expired"
                    )
                return await self.async_force_refresh_tokens()

            if check_if_jwt_expired(
                "cognito_token",
                self.storageData.refreshTokensData.data.cognito_token,
                "exp",
            ):
                if self.is_verbose_session_logging():
                    _LOGGER.debug(
                        "SessionManager.async_refresh_tokens cognito_token expired"
                    )
                return await self.async_force_refresh_tokens()

            return self.storageData.refreshTokensData

        return await self.async_force_refresh_tokens()

    async def async_force_aws_credentials(self) -> GetAwsCredentialsResponse:
        if self.is_verbose_session_logging():
            _LOGGER.info("SessionManager.async_force_aws_credentials")
        refreshTokensData = await self.async_refresh_tokens()

        awsCredentials = await get_aws_credentials(
            cognitoToken=refreshTokensData.data.cognito_token,
            verbose_logging=self.is_verbose_session_logging(),
        )

        self.storageData.awsCredentialsData = awsCredentials
        await self._store.async_save(data=self.storageData)
        return awsCredentials

    async def async_aws_credentials(self) -> GetAwsCredentialsResponse:
        if self.storageData.awsCredentialsData is not None:
            if self.is_verbose_session_logging():
                _LOGGER.debug(
                    "SessionManager.async_aws_credentials.resolve from storage"
                )

            if check_if_expired(
                self.storageData.awsCredentialsData.Credentials.expiration
            ):
                if self.is_verbose_session_logging():
                    _LOGGER.info(
                        "SessionManager.async_aws_credentials Credentials expired"
                    )
                return await self.async_force_aws_credentials()

            return self.storageData.awsCredentialsData

        return await self.async_force_aws_credentials()
