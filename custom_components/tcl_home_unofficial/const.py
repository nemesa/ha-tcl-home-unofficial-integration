"""Constants for the TCL Home - Unofficial integration."""


def get_device_data_storege_key(device_id: str) -> str:
    """Get the storage key for a device."""
    return f"{DOMAIN}.device_data_storage.{device_id}"


def get_device_self_dignose_storege_key(device_id: str) -> str:
    """Get the storage key for a device."""
    return f"{DOMAIN}.device_self_dignose_storage.{device_id}"


DOMAIN = "tcl_home_unofficial"


DEFAULT_APP_LOGI_URL = "https://pa.account.tcl.com/account/login?clientId=54148614"
DEFAULT_APP_CLOUD_URL = "https://prod-center.aws.tcljd.com/v3/global/cloud_url_get"

DEFAULT_APP_ID = "wx6e1af3fa84fbe523"

DEFAULT_USER = ""
DEFAULT_PW = ""

DEFAULT_SCAN_INTERVAL = 60
MIN_SCAN_INTERVAL = 10
