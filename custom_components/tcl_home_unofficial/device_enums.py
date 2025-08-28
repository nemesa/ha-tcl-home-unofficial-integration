"""."""

from enum import StrEnum


class ModeEnum(StrEnum):
    COOL = "Cool"
    HEAT = "Heat"
    DEHUMIDIFICATION = "Dehumidification"
    FAN = "Fan"
    AUTO = "Auto"


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


class WindSeedEnum(StrEnum):
    STRONG = "Strong"
    HIGH = "High"
    MID_HIGH = "Mid-high"
    MEDIUM = "Medium"
    MID_LOW = "Mid-low"
    LOW = "Low"
    MUTE = "Mute"
    AUTO = "Auto"


def getWindSpeed(wind_speed: int, turbo: int, silence_switch: int) -> WindSeedEnum:
    match wind_speed:
        case 6:
            return WindSeedEnum.STRONG if turbo == 1 else WindSeedEnum.HIGH
        case 5:
            return WindSeedEnum.MID_HIGH
        case 4:
            return WindSeedEnum.MEDIUM
        case 3:
            return WindSeedEnum.MID_LOW
        case 2:
            return WindSeedEnum.MUTE if silence_switch == 1 else WindSeedEnum.LOW
        case 0:
            return WindSeedEnum.AUTO
        case _:
            return WindSeedEnum.AUTO


class PortableWindSeedEnum(StrEnum):
    HIGH = "High"
    LOW = "Low"
    AUTO = "Auto"


def getPortableWindSeed(wind_speed: int, has_auto_mode: bool) -> PortableWindSeedEnum:
    if has_auto_mode:
        match wind_speed:
            case 2:
                return PortableWindSeedEnum.HIGH
            case 1:
                return PortableWindSeedEnum.LOW
            case 0:
                return PortableWindSeedEnum.AUTO
            case _:
                return PortableWindSeedEnum.AUTO
    else:
        match wind_speed:
            case 1:
                return PortableWindSeedEnum.HIGH
            case 0:
                return PortableWindSeedEnum.LOW
            case _:
                return PortableWindSeedEnum.LOW


class WindowAcWindSeedEnum(StrEnum):
    SPEED_1 = "1"
    SPEED_2 = "2"
    SPEED_3 = "3"
    AUTO = "Auto"


def getWindowAcWindSeed(wind_speed: int) -> PortableWindSeedEnum:
    match wind_speed:
        case 2:
            return WindowAcWindSeedEnum.SPEED_1
        case 4:
            return WindowAcWindSeedEnum.SPEED_2
        case 6:
            return WindowAcWindSeedEnum.SPEED_3
        case _:
            return WindowAcWindSeedEnum.AUTO


class TemperatureTypeEnum(StrEnum):
    FAHRENHEIT = "Fahrenheit"
    CELSIUS = "Celsius"


def getTemperatureType(temperature_type: int) -> TemperatureTypeEnum:
    match temperature_type:
        case 1:
            return TemperatureTypeEnum.FAHRENHEIT
        case 0:
            return TemperatureTypeEnum.CELSIUS
        case _:
            return TemperatureTypeEnum.CELSIUS


class FreshAirEnum(StrEnum):
    AUTO = "Auto"
    STRENGTH_1 = "1"
    STRENGTH_2 = "2"
    STRENGTH_3 = "3"


def getFreshAir(new_wind_strength: int) -> FreshAirEnum:
    match new_wind_strength:
        case 1:
            return FreshAirEnum.STRENGTH_1
        case 2:
            return FreshAirEnum.STRENGTH_2
        case 3:
            return FreshAirEnum.STRENGTH_3
        case 0:
            return FreshAirEnum.AUTO
        case _:
            return FreshAirEnum.AUTO


class WindFeelingEnum(StrEnum):
    NONE = "Not set"
    SOFT = "Soft"
    SHOWER = "Shower"
    CARPET = "Carpet"
    SURROUND = "Surround"


def getWindFeeling(soft_wind: int) -> WindFeelingEnum:
    match soft_wind:
        case 1:
            return WindFeelingEnum.SOFT
        case 2:
            return WindFeelingEnum.SHOWER
        case 3:
            return WindFeelingEnum.CARPET
        case 3:
            return WindFeelingEnum.SURROUND
        case 0:
            return WindFeelingEnum.NONE
        case _:
            return WindFeelingEnum.NONE


class GeneratorModeEnum(StrEnum):
    NONE = "Not set"
    L1 = "L1 30%"
    L2 = "L1 50%"
    L3 = "L1 70%"


def getGeneratorMode(generator_mode: int) -> GeneratorModeEnum:
    match generator_mode:
        case 1:
            return GeneratorModeEnum.L1
        case 2:
            return GeneratorModeEnum.L2
        case 3:
            return GeneratorModeEnum.L3
        case 0:
            return GeneratorModeEnum.NONE
