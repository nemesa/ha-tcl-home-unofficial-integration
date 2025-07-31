from enum import IntEnum
import logging

_LOGGER = logging.getLogger(__name__)


class DeviceCapabilityEnum(IntEnum):
    CAPABILITY_01 = 1
    CAPABILITY_02 = 2
    CAPABILITY_03 = 3
    CAPABILITY_04 = 4
    CAPABILITY_SOFT_WIND = 5
    CAPABILITY_06 = 6
    CAPABILITY_07 = 7
    CAPABILITY_08 = 8
    CAPABILITY_09 = 9
    CAPABILITY_10 = 10
    CAPABILITY_11 = 11
    CAPABILITY_12 = 12
    CAPABILITY_13 = 13
    CAPABILITY_14 = 14
    CAPABILITY_15 = 15
    CAPABILITY_16 = 16
    CAPABILITY_17 = 17
    CAPABILITY_18 = 18
    CAPABILITY_19 = 19
    CAPABILITY_20 = 20
    CAPABILITY_8C_HEATING = 21
    CAPABILITY_22 = 22
    CAPABILITY_GENERATOR_MODE = 23
    CAPABILITY_24 = 24
    CAPABILITY_25 = 25
    CAPABILITY_26 = 26
    CAPABILITY_27 = 27
    CAPABILITY_28 = 28
    CAPABILITY_29 = 29
    CAPABILITY_30 = 30
    CAPABILITY_31 = 31
    CAPABILITY_32 = 32
    CAPABILITY_33 = 33
    CAPABILITY_34 = 34
    CAPABILITY_35 = 35
    CAPABILITY_36 = 36
    CAPABILITY_37 = 37
    CAPABILITY_38 = 38
    CAPABILITY_39 = 39
    CAPABILITY_40 = 40
    CAPABILITY_41 = 41
    CAPABILITY_42 = 42
    CAPABILITY_43 = 43
    CAPABILITY_44 = 44
    CAPABILITY_45 = 45
    CAPABILITY_46 = 46
    CAPABILITY_47 = 47
    CAPABILITY_48 = 48
    CAPABILITY_49 = 49
    CAPABILITY_50 = 50


def get_capabilities(aws_capabilities: list[int]) -> list[DeviceCapabilityEnum]:
    return aws_capabilities


def is_all_capabilities_implemented(capabilities: list[DeviceCapabilityEnum]) -> bool:
    implemented_capabilities = [
        DeviceCapabilityEnum.CAPABILITY_02,
        DeviceCapabilityEnum.CAPABILITY_03,
        DeviceCapabilityEnum.CAPABILITY_SOFT_WIND,
        DeviceCapabilityEnum.CAPABILITY_07,
        DeviceCapabilityEnum.CAPABILITY_08,
        DeviceCapabilityEnum.CAPABILITY_09,
        DeviceCapabilityEnum.CAPABILITY_11,
        DeviceCapabilityEnum.CAPABILITY_12,
        DeviceCapabilityEnum.CAPABILITY_13,
        DeviceCapabilityEnum.CAPABILITY_8C_HEATING,
        DeviceCapabilityEnum.CAPABILITY_22,
        DeviceCapabilityEnum.CAPABILITY_GENERATOR_MODE,
        DeviceCapabilityEnum.CAPABILITY_28,
        DeviceCapabilityEnum.CAPABILITY_31,
        DeviceCapabilityEnum.CAPABILITY_33,
        DeviceCapabilityEnum.CAPABILITY_34,
        DeviceCapabilityEnum.CAPABILITY_35,
        DeviceCapabilityEnum.CAPABILITY_36,
        DeviceCapabilityEnum.CAPABILITY_39,
        DeviceCapabilityEnum.CAPABILITY_40,
        DeviceCapabilityEnum.CAPABILITY_41,
        DeviceCapabilityEnum.CAPABILITY_42,
        DeviceCapabilityEnum.CAPABILITY_43,
        DeviceCapabilityEnum.CAPABILITY_48,
    ]
    return all(capability in capabilities for capability in implemented_capabilities)
