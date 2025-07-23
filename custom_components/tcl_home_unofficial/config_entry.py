"""."""

import logging
from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .device import Device

type New_NameConfigEntry = ConfigEntry[RuntimeData]

_LOGGER = logging.getLogger(__name__)


@dataclass
class ConfigData:
    """Class to hold config data."""

    username: str
    password: str
    app_login_url: str
    cloud_urls:str
    app_id: str
    verbose_device_logging: bool
    verbose_session_logging: bool
    verbose_setup_logging: bool


@dataclass
class RuntimeData:
    """Class to hold your data."""

    coordinator: DataUpdateCoordinator
    devices: list[Device] | None = None
    non_implemented_devices: list[Device] | None = None


def buildConfigData(data: dict, fallback: dict = {}):
    config = ConfigData(
        username=data.get(CONF_USERNAME, fallback[CONF_USERNAME]),
        password=data.get(CONF_PASSWORD, fallback[CONF_PASSWORD]),
        app_login_url=data.get("app_login_url", fallback["app_login_url"]),
        cloud_urls=data.get("cloud_urls", fallback["cloud_urls"]),
        app_id=data.get("app_id", fallback["app_id"]),
        verbose_device_logging=data.get(
            "verbose_device_logging", fallback["verbose_device_logging"]
        ),
        verbose_session_logging=data.get(
            "verbose_session_logging", fallback["verbose_session_logging"]
        ),
        verbose_setup_logging=data.get(
            "verbose_setup_logging", fallback["verbose_setup_logging"]
        ),
    )
    return config


def sanitizeConfigData(config: ConfigData) -> None:
    return ConfigData(
        username=config.username,
        password="*****",
        app_login_url=config.app_login_url,
        cloud_urls=config.cloud_urls,
        app_id=config.app_id,
        verbose_device_logging=config.verbose_device_logging,
        verbose_session_logging=config.verbose_session_logging,
        verbose_setup_logging=config.verbose_setup_logging,
    )


def convertToConfigData(
    config_entry: ConfigEntry,
) -> ConfigData:
    """Convert a ConfigEntry to ConfigData."""

    if config_entry.options:
        return buildConfigData(config_entry.options, config_entry.data)
    return buildConfigData(config_entry.data)
