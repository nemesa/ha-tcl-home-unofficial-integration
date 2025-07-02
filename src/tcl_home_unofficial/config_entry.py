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
    app_client_id: str
    app_id: str
    aws_region: str
    verbose_device_logging: bool
    verbose_session_logging: bool
    verbose_setup_logging: bool


@dataclass
class RuntimeData:
    """Class to hold your data."""

    coordinator: DataUpdateCoordinator
    devices: list[Device] | None = None


def buildConfigData(data: dict):
    config = ConfigData(
        username=data[CONF_USERNAME],
        password=data[CONF_PASSWORD],
        app_client_id=data["app_client_id"],
        app_id=data["app_id"],
        aws_region=data["aws_region"],
        verbose_device_logging=data["verbose_device_logging"],
        verbose_session_logging=data["verbose_session_logging"],
        verbose_setup_logging=data["verbose_setup_logging"],
    )
    return config


def sanitizeConfigData(config: ConfigData) -> None:
    return ConfigData(
        username=config.username,
        password="*****",
        app_client_id=config.app_client_id,
        app_id=config.app_id,
        aws_region=config.aws_region,
        verbose_device_logging=config.verbose_device_logging,
        verbose_session_logging=config.verbose_session_logging,
        verbose_setup_logging=config.verbose_setup_logging,
    )


def convertToConfigData(
    config_entry: ConfigEntry,
) -> ConfigData:
    """Convert a ConfigEntry to ConfigData."""

    if config_entry.options:
        return buildConfigData(config_entry.options)
    return buildConfigData(config_entry.data)
