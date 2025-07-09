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
    DEFAULT_APP_LOGI_URL,
    DEFAULT_APP_CLOUD_URL,
    DEFAULT_PW,
    DEFAULT_USER,
    DOMAIN,
)
from .session_manager import SessionManager

_LOGGER = logging.getLogger(__name__)

STEP_LOG_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("verbose_device_logging", default=False): bool,
        vol.Required("verbose_session_logging", default=False): bool,
        vol.Required("verbose_setup_logging", default=False): bool,
    }
)


async def isUserCanLogIn(hass: HomeAssistant, data: dict[str, Any]) -> dict:
    sessionManager = SessionManager(
        hass=hass,
        configData=ConfigData(
            app_login_url=data["app_login_url"],
            cloud_urls=data["cloud_urls"],
            app_id=data["app_id"],
            username=data[CONF_USERNAME],
            password=data[CONF_PASSWORD],
            verbose_device_logging=False,
            verbose_session_logging=False,
            verbose_setup_logging=False,
            behavior_keep_target_temperature_at_cliet_mode_change=False,
            behavior_mute_beep_on_power_on=False,
        ),
    )

    await sessionManager.clear_storage()
    await sessionManager.async_load()

    authResult = await sessionManager.async_get_auth_data(allowInvalid=True)
    if authResult is not None and authResult.token:
        return {"success": True}
    return {"success": False}


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    authResult = await isUserCanLogIn(hass, data)

    if authResult["success"]:
        return {"title": f"TCL Home integration - {data[CONF_USERNAME]}"}

    raise InvalidAuth


class TclHomeUnofficialConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TclHomeUnofficialConfigFlow."""

    VERSION = 1
    _input_data: dict[str, Any] = {}
    _title: str

    _has_invalid_auth: bool = False

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
        if self._has_invalid_auth:
            errors["base"] = "invalid_auth"
        user_name = DEFAULT_USER
        user_password = DEFAULT_PW

        if self._input_data is not None:
            if CONF_USERNAME in self._input_data:
                user_name = self._input_data[CONF_USERNAME]
            if CONF_PASSWORD in self._input_data:
                user_password = self._input_data[CONF_PASSWORD]

        data_schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME, default=user_name): str,
                vol.Required(CONF_PASSWORD, default=user_password): str,
            }
        )

        if user_input is not None:
            self._input_data = user_input

            # Call the next step
            self._has_invalid_auth = False
            return await self.async_step_settings_of_app()

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            last_step=False,
        )

    async def async_step_settings_of_app(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            self._input_data.update(user_input)

            canUserLoginResult = await isUserCanLogIn(self.hass, self._input_data)
            if canUserLoginResult["success"] is False:
                self._has_invalid_auth = True
                return await self.async_step_user()
            else:
                return await self.async_step_settings_of_behavior()

        app_login_url = DEFAULT_APP_LOGI_URL
        cloud_urls = DEFAULT_APP_CLOUD_URL
        app_id = DEFAULT_APP_ID
        if self._input_data is not None:
            if "app_login_url" in self._input_data:
                app_login_url = self._input_data["app_login_url"]
            if "app_id" in self._input_data:
                app_id = self._input_data["app_id"]
            if "cloud_urls" in self._input_data:
                cloud_urls = self._input_data["cloud_urls"]

        data_schema = vol.Schema(
            {
                vol.Required("app_login_url", default=app_login_url): str,
                vol.Required("cloud_urls", default=cloud_urls): str,
                vol.Required("app_id", default=app_id): str,
            }
        )

        return self.async_show_form(
            step_id="settings_of_app",
            data_schema=data_schema,
            errors=errors,
            last_step=False,
        )

    async def async_step_settings_of_behavior(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            self._input_data.update(user_input)
            return await self.async_step_settings_of_logs()

        behavior_keep_target_temperature_at_cliet_mode_change = False
        behavior_mute_beep_on_power_on = False
        if self._input_data is not None:
            if (
                "behavior_keep_target_temperature_at_cliet_mode_change"
                in self._input_data
            ):
                behavior_keep_target_temperature_at_cliet_mode_change = (
                    self._input_data[
                        "behavior_keep_target_temperature_at_cliet_mode_change"
                    ]
                )
        if self._input_data is not None:
            if "behavior_mute_beep_on_power_on" in self._input_data:
                behavior_mute_beep_on_power_on = self._input_data[
                    "behavior_mute_beep_on_power_on"
                ]

        data_schema = vol.Schema(
            {
                vol.Required(
                    "behavior_keep_target_temperature_at_cliet_mode_change",
                    default=behavior_keep_target_temperature_at_cliet_mode_change,
                ): bool,
                vol.Required(
                    "behavior_mute_beep_on_power_on",
                    default=behavior_mute_beep_on_power_on,
                ): bool,
            }
        )

        return self.async_show_form(
            step_id="settings_of_behavior",
            data_schema=data_schema,
            errors=errors,
            last_step=False,
        )

    async def async_step_settings_of_logs(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            self._input_data.update(user_input)
            info = {
                "title": f"TCL Home integration - {self._input_data[CONF_USERNAME]}"
            }
            await self.async_set_unique_id(info.get("title"))
            self._abort_if_unique_id_configured()
            # return self.async_create_entry(title=info["title"], data=user_input)
            self._title = info["title"]

            return self.async_create_entry(
                title=self._title, data=self._input_data, options=self._input_data
            )

        # ----------------------------------------------------------------------------
        # Show settings form.  The step id always needs to match the bit after async_step_ in your method.
        # Set last_step to True here if it is last step.
        # ----------------------------------------------------------------------------
        return self.async_show_form(
            step_id="settings_of_logs",
            data_schema=STEP_LOG_DATA_SCHEMA,
            errors=errors,
            last_step=True,
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

        self.data = convertToConfigData(self.config_entry)

        return self.async_show_menu(
            step_id="init",
            # menu_options=["option_page_1", "option_page_2"],
            menu_options={
                "option_page_account": "Account",
                "option_page_tcl_app": "TCL App Settings",
                "option_page_logs": "Logs",
                "option_page_behaviors": "Behaviors",
            },
        )

    async def async_step_option_page_account(self, user_input=None):
        if user_input is not None:
            options = self.config_entry.options | user_input
            return self.async_create_entry(data=options)

        data = convertToConfigData(self.config_entry)
        data_schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME, default=data.username): str,
                vol.Required(CONF_PASSWORD, default=data.password): str,
            }
        )

        return self.async_show_form(
            step_id="option_page_account", data_schema=data_schema
        )

    async def async_step_option_page_tcl_app(self, user_input=None):
        if user_input is not None:
            options = self.config_entry.options | user_input
            return self.async_create_entry(data=options)

        data = convertToConfigData(self.config_entry)
        data_schema = vol.Schema(
            {
                vol.Required("app_login_url", default=data.app_login_url): str,
                vol.Required("cloud_urls", default=data.cloud_urls): str,
                vol.Required("app_id", default=data.app_id): str,
            }
        )

        return self.async_show_form(
            step_id="option_page_tcl_app", data_schema=data_schema
        )

    async def async_step_option_page_logs(self, user_input=None):
        if user_input is not None:
            options = self.config_entry.options | user_input
            return self.async_create_entry(data=options)

        data = convertToConfigData(self.config_entry)
        data_schema = vol.Schema(
            {
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

        return self.async_show_form(step_id="option_page_logs", data_schema=data_schema)

    async def async_step_option_page_behaviors(self, user_input=None):
        if user_input is not None:
            options = self.config_entry.options | user_input
            return self.async_create_entry(data=options)

        data = convertToConfigData(self.config_entry)
        data_schema = vol.Schema(
            {
                vol.Required(
                    "behavior_keep_target_temperature_at_cliet_mode_change",
                    default=data.behavior_keep_target_temperature_at_cliet_mode_change,
                ): bool,
                vol.Required(
                    "behavior_mute_beep_on_power_on",
                    default=data.behavior_mute_beep_on_power_on,
                ): bool,
            }
        )

        return self.async_show_form(
            step_id="option_page_behaviors", data_schema=data_schema
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
