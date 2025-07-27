from enum import StrEnum


class DeviceTypeEnum(StrEnum):
    SPLIT_AC = "Split AC"
    SPLIT_AC_FRESH_AIR = "Split AC Fresh air"
    PORTABLE_AC = "Portable AC"


def is_implemented_by_integration(device_type: str) -> bool:
    known_device_types = ["Split AC", "Split AC-1", "Split AC Fresh air", "Portable AC"]
    if device_type.lower() in list(map(str.lower, known_device_types)):
        return True
    return False


def calculateDeviceType(device_type: str) -> DeviceTypeEnum | None:
    if device_type == "Portable AC":
        return DeviceTypeEnum.PORTABLE_AC
    elif device_type == "Split AC Fresh air":
        return DeviceTypeEnum.SPLIT_AC_FRESH_AIR
    elif device_type == "Split AC" or device_type == "Split AC-1":
        return DeviceTypeEnum.SPLIT_AC
    return None
