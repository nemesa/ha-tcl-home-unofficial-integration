"""."""

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .device import Device

type New_NameConfigEntry = ConfigEntry[RuntimeData]


@dataclass
class ConfigData:
    """Class to hold config data."""

    username: str
    password: str
    app_client_id: str
    app_id: str
    aws_region: str


@dataclass
class RuntimeData:
    """Class to hold your data."""

    coordinator: DataUpdateCoordinator
    devices: list[Device] | None = None


def convertToConfigData(
    config_entry: New_NameConfigEntry,
) -> ConfigData:
    """Convert a ConfigEntry to ConfigData."""
    return ConfigData(
        username=config_entry.data[CONF_USERNAME],
        password=config_entry.data[CONF_PASSWORD],
        app_client_id=config_entry.data["app_client_id"],
        app_id=config_entry.data["app_id"],
        aws_region=config_entry.data["aws_region"],
    )
