from enum import StrEnum

class DeviceTypeEnum(StrEnum):
    SPLIT_AC = "Split AC"
    SPLIT_AC_FRESH_AIR = "Split AC Fresh air"
    PORTABLE_AC = "Portable AC"
    WINDOW_AC = "Window AC"
    CYLINDRICAL_AC = "Cylindrical AC"  # <-- NEU
    DEHUMIDIFIER_DEM = "Dehumidifier DEM"
    DEHUMIDIFIER_DF = "Dehumidifier DF"
    DUCT_AC = "Duct"
    AIR_PURIFIER_BREEVA_A2 = "Breeva A2"
    AIR_PURIFIER_BREEVA_A3 = "Breeva A3"
    AIR_PURIFIER_BREEVA_A5 = "Breeva A5"
    ATW_HEAT_PUMP = "ATW Heat Pump"

def is_device_with_number(original_device_type: str, device_type_to_check: str) -> bool:
    if device_type_to_check.lower().startswith(original_device_type.lower()+"-"):
        suffix = device_type_to_check[len(original_device_type)+1:]
        if suffix.isdigit():
            return True
    return False


def is_implemented_by_integration(device_type: str) -> bool:

    known_device_types=[]
    for known_device_str in DeviceTypeEnum:        
        known_device_types.append(known_device_str)
        if is_device_with_number(known_device_str, device_type):
            device_type = known_device_str

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
    elif device_type == "Cylindrical AC":  # Keep this before the Split AC check.
        return DeviceTypeEnum.CYLINDRICAL_AC
    elif device_type == "Duct":
        return DeviceTypeEnum.DUCT_AC
    elif device_type == "Split AC":
        return DeviceTypeEnum.SPLIT_AC
    elif device_type == "breeva A2":
        return DeviceTypeEnum.AIR_PURIFIER_BREEVA_A2
    elif device_type == "breeva A3":
        return DeviceTypeEnum.AIR_PURIFIER_BREEVA_A3
    elif device_type == "breeva A5":
        return DeviceTypeEnum.AIR_PURIFIER_BREEVA_A5
    elif device_type == "ATW Heat Pump":
        return DeviceTypeEnum.ATW_HEAT_PUMP
    else:
        for known_device_str in DeviceTypeEnum:
            if is_device_with_number(known_device_str, device_type):
                return known_device_str
    return None
