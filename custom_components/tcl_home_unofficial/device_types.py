from enum import StrEnum


class DeviceTypeEnum(StrEnum):
    SPLIT_AC = "Split AC"
    SPLIT_AC_FRESH_AIR = "Split AC Fresh air"
    PORTABLE_AC = "Portable AC"
    WINDOW_AC = "Window AC"
    DEHUMIDIFIER_DEM = "Dehumidifier DEM"
    DEHUMIDIFIER_DF = "Dehumidifier DF"
    DUCT_AC = "Duct"


def is_split_ac_with_number(device_type:str)-> bool:
    if device_type.lower().startswith("split ac-"):
        suffix = device_type[9:]
        if suffix.isdigit():
            return True
    return False

def is_implemented_by_integration(device_type: str) -> bool:
    known_device_types = [
        "Split AC",
        "Split AC-#",
        "Split AC Fresh air",
        "Portable AC",
        "Window AC",
        "Dehumidifier DEM",
        "Dehumidifier DF",
        "Duct",
    ]
    
    if is_split_ac_with_number(device_type):
        device_type = "Split AC-#"
    
    if device_type.lower() in list(map(str.lower, known_device_types)):
        return True
    return False


def calculateDeviceType(device_type: str) -> DeviceTypeEnum | None:
    if device_type == "Portable AC":
        return DeviceTypeEnum.PORTABLE_AC
    elif device_type == "Dehumidifier DEM":
        return DeviceTypeEnum.DEHUMIDIFIER_DEM
    elif device_type == "Dehumidifier DF":
        return DeviceTypeEnum.DEHUMIDIFIER_DF
    elif device_type == "Split AC Fresh air":
        return DeviceTypeEnum.SPLIT_AC_FRESH_AIR
    elif device_type == "Window AC":
        return DeviceTypeEnum.WINDOW_AC
    elif device_type == "Duct":
        return DeviceTypeEnum.DUCT_AC
    elif device_type == "Split AC" or is_split_ac_with_number(device_type):
        return DeviceTypeEnum.SPLIT_AC
    return None
