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
    verbose_logging: bool


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
        verbose_logging=data["verbose_logging"],
    )
    return config


def logConfigData(config: ConfigData) -> None:
    log = f"config-data: username: {config.username}"
    log += f", app_client_id: {config.app_client_id}"
    log += ", password: *****"
    log += f", app_id: {config.app_id}"
    log += f", aws_region: {config.aws_region}"
    log += f", verbose_logging: {config.verbose_logging}"

    if config.verbose_logging:
        _LOGGER.info(log)


def convertToConfigData(
    config_entry: ConfigEntry,
) -> ConfigData:
    """Convert a ConfigEntry to ConfigData."""

    if config_entry.options:
        config = buildConfigData(config_entry.options)
        logConfigData(config)
        return config
    else:
        config = buildConfigData(config_entry.data)
        logConfigData(config)
        return config
