"""Config flow for the TCL Home - Unofficial integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .config_entry import ConfigData
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

# TODO adjust the data schema to the data that you need
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(
            "app_client_id", "App ClientId", DEFAULT_CLIENT_ID, "desc:App ClientId"
        ): int,
        vol.Required("app_id", "App Id", DEFAULT_APP_ID): str,
        vol.Required("aws_region", "Aws region", DEFAULT_AWS_REGION): str,
        vol.Required(CONF_USERNAME, "TCL Home app - Emial", DEFAULT_USER): str,
        vol.Required(CONF_PASSWORD, "TCL Home app - Password", DEFAULT_PW): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # _LOGGER.info("validate_input: %s", data)

    sessionManager = SessionManager(
        hass=hass,
        configData=ConfigData(
            app_client_id=data["app_client_id"],
            app_id=data["app_id"],
            aws_region=data["aws_region"],
            username=data[CONF_USERNAME],
            password=data[CONF_PASSWORD],
        ),
    )

    await sessionManager.async_load()

    authResult = await sessionManager.async_get_auth_data()

    if authResult.token:
        return {"title": f"TCL Home integration - {data[CONF_USERNAME]}"}

    data["sessionManager"] = sessionManager

    # authResult = await do_account_auth(
    #     data[CONF_USERNAME], data[CONF_PASSWORD], data["app_client_id"]
    # )
    # if authResult["token"]:
    #     data["authResult"] = authResult
    #     return {"title": f"TCL Home integration - {data[CONF_USERNAME]}"}

    raise InvalidAuth


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MyTestIntegration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
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


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
