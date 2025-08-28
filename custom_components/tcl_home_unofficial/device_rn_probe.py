"""React Native bundle probing utilities for fan-speed mapping.

Centralizes the React Native bundle probe logic so it can be invoked from
the coordinator (or elsewhere) without cluttering setup.

What this module provides:
- Pick highest `plugInVersion` record from `/v3/config/get`.
- Download bundle ZIP, read `main.jsbundle`, parse `FAN_SPEED_*` mapping.
- Orchestrate end-to-end probe and persist mapping into per-device storage
  under `detected.fan_speed.mapping` when available.
"""

from __future__ import annotations

from io import BytesIO
from typing import Any
import zipfile


def _version_key(v: str | None) -> tuple[int, ...]:
    """Convert dotted version like '3.0.6' into a numeric tuple for sorting.

    Unknown/invalid values sort lowest.
    """
    if not v:
        return (0,)
    try:
        return tuple(int(p) for p in str(v).split("."))
    except Exception:
        return (0,)


def pick_best_plugin_record(cfg_data: Any) -> dict | None:
    """From /v3/config/get payload (.data), pick the record with highest plugInVersion.

    Accepts either a list of dicts or a single dict. Returns the chosen dict or None.
    """
    records: list[dict] = []
    if isinstance(cfg_data, list):
        records = [r for r in cfg_data if isinstance(r, dict)]
    elif isinstance(cfg_data, dict):
        records = [cfg_data]
    else:
        return None

    if not records:
        return None

    return max(records, key=lambda r: _version_key(r.get("plugInVersion")))


def zip_contains_main_jsbundle(zip_bytes: bytes) -> bool:
    """Return True if the in-memory ZIP has a member ending in 'main.jsbundle'."""
    try:
        with zipfile.ZipFile(BytesIO(zip_bytes)) as zf:
            return any(name.endswith("main.jsbundle") for name in zf.namelist())
    except zipfile.BadZipFile:
        return False


def read_main_jsbundle_text(zip_bytes: bytes) -> tuple[str | None, str | None]:
    """Return (bundle_text, member_name) if main.jsbundle exists, else (None, None)."""
    try:
        with zipfile.ZipFile(BytesIO(zip_bytes)) as zf:
            for name in zf.namelist():
                if name.endswith("main.jsbundle"):
                    data = zf.read(name)
                    try:
                        return data.decode("utf-8", errors="ignore"), name
                    except Exception:
                        return None, name
    except zipfile.BadZipFile:
        return None, None
    return None, None


def parse_fan_speed_mapping(bundle_text: str) -> list[str] | None:
    """Parse FAN_SPEED_* new Map([...]) tokens from bundle text and return ordered list.

    Looks for an explicit new Map([...]) containing entries like ['FAN_SPEED_AUTO',0].
    Returns a list of tokens in order or None if not found.
    """
    import re

    map_pattern = re.compile(r"new\s+Map\(\[(.*?)\]\)", re.DOTALL)
    entry_pattern = re.compile(r"[\"'](FAN_SPEED_[A-Z_]+)[\"']\s*,\s*(\d+)")

    for m in map_pattern.finditer(bundle_text):
        entries = entry_pattern.findall(m.group(1))
        if entries and any(tok.startswith("FAN_SPEED_") for tok, _ in entries):
            return [tok for tok, _ in entries]
    return None


# Orchestration (HA-aware): fetch config, download ZIP, read bundle, parse mapping
async def fetch_and_parse_mapping(hass, session_manager, product_key: str | None) -> list[str] | None:
    """Fetch RN config, download ZIP, read main.jsbundle, and parse mapping.

    Returns ordered FAN_SPEED_* tokens or None.
    """
    if not product_key:
        return None
    from .tcl import get_config
    from homeassistant.helpers.httpx_client import get_async_client

    cloud = await session_manager.async_aws_cloud_urls()
    tokens = await session_manager.async_refresh_tokens()
    auth = await session_manager.async_get_auth_data(allowInvalid=True)

    cfg = await get_config(
        hass=hass,
        cloud_url=cloud.data.cloud_url,
        saas_token=tokens.data.saas_token,
        country_abbr=(auth.user.country_abbr if auth and auth.user else None),
        product_key=product_key,
        verbose_logging=False,
    )
    if not cfg or cfg.data is None:
        return None

    best = pick_best_plugin_record(cfg.data)
    if not best:
        return None
    url = best.get("plugInUrl")
    if not url:
        return None

    httpx = get_async_client(hass)
    resp = await httpx.get(url)
    if resp.status_code != 200:
        return None

    bundle_text, _member = read_main_jsbundle_text(resp.content)
    if not bundle_text:
        return None
    return parse_fan_speed_mapping(bundle_text)


async def probe_and_persist_mapping(hass, session_manager, device) -> None:
    """End-to-end probe for a device: fetch RN bundle, parse mapping, persist per-device.

    Writes mapping to detected.fan_speed.mapping if available. Silent no-op on failure.
    """
    from .device_data_storage import set_detected_fan_speed_mapping

    product_key = getattr(device, "product_key", None)
    mapping = await fetch_and_parse_mapping(hass, session_manager, product_key)
    if not mapping:
        return
    await set_detected_fan_speed_mapping(hass, device.device_id, mapping)
