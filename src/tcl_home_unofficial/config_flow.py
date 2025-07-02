"""Config flow for the TCL Home - Unofficial integration."""

from __future__ import annotations

import logging
from typing import Any, Dict

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
    FlowResult,
)
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaConfigFlowHandler,
    SchemaFlowFormStep,
)

from homeassistant.config_entries import ConfigEntry
from .config_entry import ConfigData, convertToConfigData
from .const import (
    DEFAULT_APP_ID,
    DEFAULT_AWS_REGION,
    DEFAULT_CLIENT_ID,
    DEFAULT_PW,
    DEFAULT_USER,
    DOMAIN,
)
from .session_manager import SessionManager

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("app_client_id", default=DEFAULT_CLIENT_ID): int,
        vol.Required("app_id", default=DEFAULT_APP_ID): str,
        vol.Required("aws_region", default=DEFAULT_AWS_REGION): str,
        vol.Required(CONF_USERNAME, default=DEFAULT_USER): str,
        vol.Required(CONF_PASSWORD, default=DEFAULT_PW): str,
        vol.Required("verbose_device_logging", default=False): bool,
        vol.Required("verbose_session_logging", default=False): bool,
        vol.Required("verbose_setup_logging", default=False): bool,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""

    sessionManager = SessionManager(
        hass=hass,
        configData=ConfigData(
            app_client_id=data["app_client_id"],
            app_id=data["app_id"],
            aws_region=data["aws_region"],
            username=data[CONF_USERNAME],
            password=data[CONF_PASSWORD],
            verbose_device_logging=data["verbose_device_logging"],
            verbose_session_logging=data["verbose_session_logging"],
            verbose_setup_logging=data["verbose_setup_logging"],
        ),
    )

    await sessionManager.async_load()

    authResult = await sessionManager.async_get_auth_data()

    if authResult.token:
        return {"title": f"TCL Home integration - {data[CONF_USERNAME]}"}

    raise InvalidAuth


class TclHomeUnofficialConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TclHomeUnofficialConfigFlow."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return TclHomeUnofficialOptionsFlowHandler()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        _LOGGER.info("Starting config flow for TCL Home Unofficial integration")
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info.get("title"))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        _LOGGER.info("Reconfiguring TCL Home Unofficial integration %s", user_input)


class TclHomeUnofficialOptionsFlowHandler(OptionsFlow):
    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            options = self.config_entry.options | user_input
            return self.async_create_entry(data=options)

        data = convertToConfigData(self.config_entry)
        errors: Dict[str, str] = {}

        data_schema = vol.Schema(
            {
                vol.Required(
                    "app_client_id",
                    default=data.app_client_id,
                ): int,
                vol.Required("app_id", default=data.app_id): str,
                vol.Required("aws_region", default=data.aws_region): str,
                vol.Required(CONF_USERNAME, default=data.username): str,
                vol.Required(CONF_PASSWORD, default=data.password): str,
                vol.Required(
                    "verbose_device_logging", default=data.verbose_device_logging
                ): bool,
                vol.Required(
                    "verbose_session_logging", default=data.verbose_session_logging
                ): bool,
                vol.Required(
                    "verbose_setup_logging", default=data.verbose_setup_logging
                ): bool,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
