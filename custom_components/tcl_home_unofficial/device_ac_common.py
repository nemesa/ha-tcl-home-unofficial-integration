"""."""

from enum import StrEnum


class ModeEnum(StrEnum):
    COOL = "Cool"
    HEAT = "Heat"
    DEHUMIDIFICATION = "Dehumidification"
    FAN = "Fan"
    AUTO = "Auto"


def getMode(work_mode: int | float) -> ModeEnum:
    match work_mode:
        case 0:
            return ModeEnum.AUTO
        case 1:
            return ModeEnum.COOL
        case 2:
            return ModeEnum.DEHUMIDIFICATION
        case 3:
            return ModeEnum.FAN
        case 4:
            return ModeEnum.HEAT
        case _:
            return ModeEnum.AUTO


class UpAndDownAirSupplyVectorEnum(StrEnum):
    UP_AND_DOWN_SWING = "Up and down swing"
    UPWARDS_SWING = "Upwards swing"
    DOWNWARDS_SWING = "Downwards swing"
    TOP_FIX = "Top fix"
    UPPER_FIX = "Upper fix"
    MIDDLE_FIX = "Middle fix"
    LOWER_FIX = "Lower fix"
    BOTTOM_FIX = "Bottom fix"
    NOT_SET = "Not set"


def getUpAndDownAirSupplyVector(
    vertical_direction: int | float,
) -> UpAndDownAirSupplyVectorEnum:
    match vertical_direction:
        case 1:
            return UpAndDownAirSupplyVectorEnum.UP_AND_DOWN_SWING
        case 2:
            return UpAndDownAirSupplyVectorEnum.UPWARDS_SWING
        case 3:
            return UpAndDownAirSupplyVectorEnum.DOWNWARDS_SWING
        case 8:
            return UpAndDownAirSupplyVectorEnum.NOT_SET
        case 9:
            return UpAndDownAirSupplyVectorEnum.TOP_FIX
        case 10:
            return UpAndDownAirSupplyVectorEnum.UPPER_FIX
        case 11:
            return UpAndDownAirSupplyVectorEnum.MIDDLE_FIX
        case 12:
            return UpAndDownAirSupplyVectorEnum.LOWER_FIX
        case 13:
            return UpAndDownAirSupplyVectorEnum.BOTTOM_FIX


class LeftAndRightAirSupplyVectorEnum(StrEnum):
    LEFT_AND_RIGHT_SWING = "Left and right swing"
    LEFT_SWING = "Left swing"
    MIDDLE_SWING = "Middle swing"
    RIGHT_SWING = "Right swing"
    LEFT_FIX = "Left fix"
    CENTER_LEFT_FIX = "Center-left fix"
    MIDDLE_FIX = "Middle fix"
    CENTER_RIGHT_FIX = "Center-right fix"
    RIGHT_FIX = "Right fix"
    NOT_SET = "Not set"


def getLeftAndRightAirSupplyVector(
    horizontal_direction: int | float,
) -> LeftAndRightAirSupplyVectorEnum:
    match horizontal_direction:
        case 1:
            return LeftAndRightAirSupplyVectorEnum.LEFT_AND_RIGHT_SWING
        case 2:
            return LeftAndRightAirSupplyVectorEnum.LEFT_SWING
        case 3:
            return LeftAndRightAirSupplyVectorEnum.MIDDLE_SWING
        case 4:
            return LeftAndRightAirSupplyVectorEnum.RIGHT_SWING
        case 8:
            return LeftAndRightAirSupplyVectorEnum.NOT_SET
        case 9:
            return LeftAndRightAirSupplyVectorEnum.LEFT_FIX
        case 10:
            return LeftAndRightAirSupplyVectorEnum.CENTER_LEFT_FIX
        case 11:
            return LeftAndRightAirSupplyVectorEnum.MIDDLE_FIX
        case 12:
            return LeftAndRightAirSupplyVectorEnum.CENTER_RIGHT_FIX
        case 13:
            return LeftAndRightAirSupplyVectorEnum.RIGHT_FIX


class SleepModeEnum(StrEnum):
    STANDARD = "Standard"
    ELDERLY = "Elderly"
    CHILD = "Child"
    OFF = "off"


def getSleepMode(sleep: int | float) -> SleepModeEnum:
    match sleep:
        case 1:
            return SleepModeEnum.STANDARD
        case 2:
            return SleepModeEnum.ELDERLY
        case 3:
            return SleepModeEnum.CHILD
        case 0:
            return SleepModeEnum.OFF


class WindSeed7GearEnum(StrEnum):
    TURBO = "Turbo"
    AUTO = "Auto"
    SPEED_1 = "1"
    SPEED_2 = "2"
    SPEED_3 = "3"
    SPEED_4 = "4"
    SPEED_5 = "5"
    SPEED_6 = "6"


def getWindSeed7Gear(wind_speed_7_gear: int) -> WindSeed7GearEnum:
    match wind_speed_7_gear:
        case 1:
            return WindSeed7GearEnum.SPEED_1
        case 2:
            return WindSeed7GearEnum.SPEED_2
        case 3:
            return WindSeed7GearEnum.SPEED_3
        case 4:
            return WindSeed7GearEnum.SPEED_4
        case 5:
            return WindSeed7GearEnum.SPEED_5
        case 6:
            return WindSeed7GearEnum.SPEED_6
        case 7:
            return WindSeed7GearEnum.TURBO
        case 0:
            return WindSeed7GearEnum.AUTO
        case _:
            return WindSeed7GearEnum.AUTO
