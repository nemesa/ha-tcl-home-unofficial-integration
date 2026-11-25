"""TCL ATW Heat Pump Weather Compensation Curves.

Based on official TCL ATW R290 Heat Pump manual:
Table of Heating Ambient Temperatures - Target Water Temperatures (Unit: °C).

Note: The TCL Home app and firmware use 1-based curve indexing:
- Value 1 = Low Temperature Curve 1 (Pardoseală)
- Value 2 = Low Temperature Curve 2 (Pardoseală)
...
- Value 8 = Low Temperature Curve 8 (Pardoseală)
- Value 9 = Low Temperature Curve 9 (Inginerie)
- Value 10 = High Temperature Curve 1 (Calorifere / Radiatoare)
...
- Value 18 = High Temperature Curve 9 (Inginerie)
"""

from typing import Any


def _build_low_temp_curve_1() -> dict[int, int]:
    r = {}
    for t in range(-20, -15):
        r[t] = 38
    for t in range(-15, -10):
        r[t] = 37
    for t in range(-10, -5):
        r[t] = 36
    for t in range(-5, 3):
        r[t] = 35
    for t in range(3, 8):
        r[t] = 34
    for t in range(8, 13):
        r[t] = 33
    for t in range(13, 21):
        r[t] = 32
    return r


def _build_low_temp_curve_2() -> dict[int, int]:
    r = {}
    for t in range(-20, -16):
        r[t] = 37
    for t in range(-16, -11):
        r[t] = 36
    for t in range(-11, -6):
        r[t] = 35
    for t in range(-6, 3):
        r[t] = 34
    for t in range(3, 8):
        r[t] = 33
    for t in range(8, 13):
        r[t] = 32
    for t in range(13, 21):
        r[t] = 31
    return r


def _build_low_temp_curve_3() -> dict[int, int]:
    r = {}
    for t in range(-20, -17):
        r[t] = 36
    for t in range(-17, -12):
        r[t] = 35
    for t in range(-12, -7):
        r[t] = 34
    for t in range(-7, 1):
        r[t] = 33
    for t in range(1, 6):
        r[t] = 32
    for t in range(6, 12):
        r[t] = 31
    for t in range(12, 18):
        r[t] = 30
    for t in range(18, 21):
        r[t] = 29
    return r


def _build_low_temp_curve_4() -> dict[int, int]:
    r = {}
    for t in range(-20, -17):
        r[t] = 35
    for t in range(-17, -12):
        r[t] = 34
    for t in range(-12, -7):
        r[t] = 33
    for t in range(-7, 1):
        r[t] = 32
    for t in range(1, 6):
        r[t] = 31
    for t in range(6, 12):
        r[t] = 30
    for t in range(12, 18):
        r[t] = 29
    for t in range(18, 21):
        r[t] = 28
    return r


def _build_low_temp_curve_5() -> dict[int, int]:
    r = {}
    for t in range(-20, -17):
        r[t] = 34
    for t in range(-17, -12):
        r[t] = 33
    for t in range(-12, -7):
        r[t] = 32
    for t in range(-7, 1):
        r[t] = 31
    for t in range(1, 6):
        r[t] = 30
    for t in range(6, 11):
        r[t] = 29
    for t in range(11, 17):
        r[t] = 28
    for t in range(17, 21):
        r[t] = 27
    return r


def _build_low_temp_curve_6() -> dict[int, int]:
    r = {}
    for t in range(-20, -16):
        r[t] = 32
    for t in range(-16, -8):
        r[t] = 31
    for t in range(-8, 0):
        r[t] = 30
    for t in range(0, 6):
        r[t] = 29
    for t in range(6, 11):
        r[t] = 28
    for t in range(11, 17):
        r[t] = 27
    for t in range(17, 21):
        r[t] = 26
    return r


def _build_low_temp_curve_7() -> dict[int, int]:
    r = {}
    for t in range(-20, -16):
        r[t] = 31
    for t in range(-16, -8):
        r[t] = 30
    for t in range(-8, 0):
        r[t] = 29
    for t in range(0, 6):
        r[t] = 28
    for t in range(6, 11):
        r[t] = 27
    for t in range(11, 17):
        r[t] = 26
    for t in range(17, 21):
        r[t] = 25
    return r


def _build_low_temp_curve_8() -> dict[int, int]:
    r = {}
    for t in range(-20, -16):
        r[t] = 29
    for t in range(-16, -8):
        r[t] = 28
    for t in range(-8, 0):
        r[t] = 27
    for t in range(0, 7):
        r[t] = 26
    for t in range(7, 14):
        r[t] = 25
    for t in range(14, 21):
        r[t] = 24
    return r


def _build_high_temp_curve(
    t_neg20: int, t_neg16: int, t_neg8: int, t_0: int, t_7: int, t_14: int
) -> dict[int, int]:
    r = {}
    for t in range(-20, -16):
        r[t] = t_neg20
    for t in range(-16, -8):
        r[t] = t_neg16
    for t in range(-8, 0):
        r[t] = t_neg8
    for t in range(0, 7):
        r[t] = t_0
    for t in range(7, 14):
        r[t] = t_7
    for t in range(14, 21):
        r[t] = t_14
    return r


HEATING_CURVES: dict[int, dict[str, Any]] = {
    1: {
        "id": 1,
        "name": "Curve 1 Underfloor (32°C - 38°C)",
        "label": "Low Temp 1 (Floor 32-38°C)",
        "emitter": "Underfloor (Low Temp)",
        "min_water": 32,
        "max_water": 38,
        "points": _build_low_temp_curve_1(),
    },
    2: {
        "id": 2,
        "name": "Curve 2 Underfloor (31°C - 37°C)",
        "label": "Low Temp 2 (Floor 31-37°C)",
        "emitter": "Underfloor (Low Temp)",
        "min_water": 31,
        "max_water": 37,
        "points": _build_low_temp_curve_2(),
    },
    3: {
        "id": 3,
        "name": "Curve 3 Underfloor (29°C - 36°C)",
        "label": "Low Temp 3 (Floor 29-36°C)",
        "emitter": "Underfloor (Low Temp)",
        "min_water": 29,
        "max_water": 36,
        "points": _build_low_temp_curve_3(),
    },
    4: {
        "id": 4,
        "name": "Curve 4 Underfloor (28°C - 35°C)",
        "label": "Low Temp 4 (Floor 28-35°C)",
        "emitter": "Underfloor (Low Temp)",
        "min_water": 28,
        "max_water": 35,
        "points": _build_low_temp_curve_4(),
    },
    5: {
        "id": 5,
        "name": "Curve 5 Underfloor (27°C - 34°C)",
        "label": "Low Temp 5 (Floor 27-34°C)",
        "emitter": "Underfloor (Low Temp)",
        "min_water": 27,
        "max_water": 34,
        "points": _build_low_temp_curve_5(),
    },
    6: {
        "id": 6,
        "name": "Curve 6 Underfloor (26°C - 32°C)",
        "label": "Low Temp 6 (Floor 26-32°C)",
        "emitter": "Underfloor (Low Temp)",
        "min_water": 26,
        "max_water": 32,
        "points": _build_low_temp_curve_6(),
    },
    7: {
        "id": 7,
        "name": "Curve 7 Underfloor (25°C - 31°C)",
        "label": "Low Temp 7 (Floor 25-31°C)",
        "emitter": "Underfloor (Low Temp)",
        "min_water": 25,
        "max_water": 31,
        "points": _build_low_temp_curve_7(),
    },
    8: {
        "id": 8,
        "name": "Curve 8 Underfloor (24°C - 29°C)",
        "label": "Low Temp 8 (Floor 24-29°C)",
        "emitter": "Underfloor (Low Temp)",
        "min_water": 24,
        "max_water": 29,
        "points": _build_low_temp_curve_8(),
    },
    9: {
        "id": 9,
        "name": "Curve 9 Underfloor (Custom / Engineering)",
        "label": "Low Temp 9 (Engineering Custom)",
        "emitter": "Underfloor (Low Temp)",
        "min_water": None,
        "max_water": None,
        "points": {},
    },
    10: {
        "id": 10,
        "name": "Curve 1 Radiators (50°C - 55°C)",
        "label": "High Temp 1 (Radiators 50-55°C)",
        "emitter": "Radiators (High Temp)",
        "min_water": 50,
        "max_water": 55,
        "points": _build_high_temp_curve(55, 54, 53, 52, 51, 50),
    },
    11: {
        "id": 11,
        "name": "Curve 2 Radiators (48°C - 53°C)",
        "label": "High Temp 2 (Radiators 48-53°C)",
        "emitter": "Radiators (High Temp)",
        "min_water": 48,
        "max_water": 53,
        "points": _build_high_temp_curve(53, 52, 51, 50, 49, 48),
    },
    12: {
        "id": 12,
        "name": "Curve 3 Radiators (47°C - 52°C)",
        "label": "High Temp 3 (Radiators 47-52°C)",
        "emitter": "Radiators (High Temp)",
        "min_water": 47,
        "max_water": 52,
        "points": _build_high_temp_curve(52, 51, 50, 49, 48, 47),
    },
    13: {
        "id": 13,
        "name": "Curve 4 Radiators (45°C - 50°C)",
        "label": "High Temp 4 (Radiators 45-50°C)",
        "emitter": "Radiators (High Temp)",
        "min_water": 45,
        "max_water": 50,
        "points": _build_high_temp_curve(50, 49, 48, 47, 46, 45),
    },
    14: {
        "id": 14,
        "name": "Curve 5 Radiators (43°C - 48°C)",
        "label": "High Temp 5 (Radiators 43-48°C)",
        "emitter": "Radiators (High Temp)",
        "min_water": 43,
        "max_water": 48,
        "points": _build_high_temp_curve(48, 47, 46, 45, 44, 43),
    },
    15: {
        "id": 15,
        "name": "Curve 6 Radiators (40°C - 45°C)",
        "label": "High Temp 6 (Radiators 40-45°C)",
        "emitter": "Radiators (High Temp)",
        "min_water": 40,
        "max_water": 45,
        "points": _build_high_temp_curve(45, 44, 43, 42, 41, 40),
    },
    16: {
        "id": 16,
        "name": "Curve 7 Radiators (38°C - 43°C)",
        "label": "High Temp 7 (Radiators 38-43°C)",
        "emitter": "Radiators (High Temp)",
        "min_water": 38,
        "max_water": 43,
        "points": _build_high_temp_curve(43, 42, 41, 40, 39, 38),
    },
    17: {
        "id": 17,
        "name": "Curve 8 Radiators (35°C - 40°C)",
        "label": "High Temp 8 (Radiators 35-40°C)",
        "emitter": "Radiators (High Temp)",
        "min_water": 35,
        "max_water": 40,
        "points": _build_high_temp_curve(40, 39, 38, 37, 36, 35),
    },
    18: {
        "id": 18,
        "name": "Curve 9 Radiators (Custom / Engineering)",
        "label": "High Temp 9 (Engineering Custom)",
        "emitter": "Radiators (High Temp)",
        "min_water": None,
        "max_water": None,
        "points": {},
    },
}

# Alias for 0 to map to Curve 1
HEATING_CURVES[0] = HEATING_CURVES[1]


def get_heating_curve_options() -> list[str]:
    """Return all 18 heating curve options for Home Assistant Select."""
    return [HEATING_CURVES[i]["name"] for i in range(1, 19)]


def get_heating_curve_name(index: int) -> str:
    """Return friendly name for curve index (1-18, fallback to 1)."""
    curve = HEATING_CURVES.get(index)
    if curve:
        return curve["name"]
    return f"Curve {index}"


def get_heating_curve_index(name_or_label: str) -> int:
    """Return curve index (1-18) from option string."""
    for idx in range(1, 19):
        c = HEATING_CURVES.get(idx)
        if not c:
            continue
        if (
            c["name"] == name_or_label
            or c["label"] == name_or_label
            or str(idx) == str(name_or_label).strip()
        ):
            return idx
    # Fallback try numeric parse
    try:
        val = int(name_or_label)
        if 1 <= val <= 18:
            return val
        if val == 0:
            return 1
    except (ValueError, TypeError):
        pass
    return 1


def get_target_water_temp_from_curve(curve_index: int, ambient_temp: float) -> int | None:
    """Calculate target flow water temperature given ambient outdoor temperature."""
    curve = HEATING_CURVES.get(curve_index)
    if not curve or not curve.get("points"):
        return None
    t = int(round(ambient_temp))
    if t < -20:
        t = -20
    elif t > 20:
        t = 20
    return curve["points"].get(t)


def get_heating_curve_attributes(curve_index: int, ambient_temp: float | None = None) -> dict[str, Any]:
    """Get rich dictionary of curve metadata and points for Home Assistant attributes."""
    curve = HEATING_CURVES.get(curve_index, HEATING_CURVES[1])
    points = curve.get("points", {})
    attrs: dict[str, Any] = {
        "curve_id": curve.get("id", curve_index),
        "curve_name": curve.get("name", f"Curve {curve_index}"),
        "curve_label": curve.get("label", ""),
        "emitter_type": curve.get("emitter", ""),
        "min_target_water_temp": curve.get("min_water"),
        "max_target_water_temp": curve.get("max_water"),
    }
    if ambient_temp is not None:
        calc_target = get_target_water_temp_from_curve(curve_index, ambient_temp)
        if calc_target is not None:
            attrs["calculated_target_water_temp"] = calc_target
    if points:
        attrs["curve_points"] = {str(k): v for k, v in points.items()}
    return attrs
