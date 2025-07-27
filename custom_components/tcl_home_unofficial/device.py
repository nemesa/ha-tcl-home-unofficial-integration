"""."""

import json
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from .device_ac_common import ModeEnum
from .device_capabilities import DeviceCapabilityEnum, get_capabilities
from .device_features import getSupportedFeatures, DeviceFeatureEnum
from .device_portable_ac import TCL_PortableAC_DeviceData, get_stored_portable_ac_data
from .device_spit_ac_fresh_air import (
    TCL_SplitAC_Fresh_Air_DeviceData,
    get_stored_spit_ac_fresh_data,
)
from .device_spit_ac_type1 import (
    TCL_SplitAC_Type1_DeviceData,
    get_stored_spit_ac_type1_data,
)
from .device_spit_ac_type2 import (
    TCL_SplitAC_Type2_DeviceData,
    get_stored_spit_ac_type2_data,
)
from .device_types import DeviceTypeEnum, calculateDeviceType

_LOGGER = logging.getLogger(__name__)


# def calculateDeviceType(
#     device_id: str, device_type: str, aws_thing: dict | None
# ) -> DeviceTypeEnum | None:
#     _LOGGER.debug("Calculating device type for %s (%s)", device_id, device_type)
#     if device_type == "Portable AC":
#         return DeviceTypeEnum.PORTABLE_AC
#     elif device_type == "Split AC Fresh air":
#         return DeviceTypeEnum.SPLIT_AC_FRESH_AIR
#     elif device_type == "Split AC" or device_type == "Split AC-1":
#         if aws_thing is not None:
#             capabilities = aws_thing["state"]["reported"].get("capabilities", [])
#             capabilities.sort()
#             for type_capabilities in get_SplitAC_Type1_capabilities():
#                 if capabilities == type_capabilities:
#                     return DeviceTypeEnum.SPLIT_AC_TYPE_1
#             for type_capabilities in get_SplitAC_Type2_capabilities():
#                 if capabilities == type_capabilities:
#                     return DeviceTypeEnum.SPLIT_AC_TYPE_2
#             return DeviceTypeEnum.SPLIT_AC
#     return None


class Device:
    """Device."""

    def __init__(
        self,
        device_id: str,
        device_type_str: str | None,
        device_type: DeviceTypeEnum | None,
        name: str,
        firmware_version: str,
        aws_thing: dict | None,
    ) -> None:
        self.device_type_str = device_type_str
        self.device_id = device_id
        if device_type is None:
            self.device_type = calculateDeviceType(
                device_id, device_type_str, aws_thing
            )
        else:
            self.device_type = device_type
        self.name = name
        self.storage = {}
        self.firmware_version = firmware_version
        self.is_implemented_by_integration = self.device_type is not None
        self.has_aws_thing = "false"
        self.capabilities_str = ""
        self.capabilities = []
        self.supported_features = []

        if aws_thing is not None:
            self.has_aws_thing = "true"
            try:
                if "state" in aws_thing:
                    if "reported" in aws_thing["state"]:
                        self.supported_features = getSupportedFeatures(self.device_type, aws_thing["state"]["reported"])
                                                
                        if "capabilities" in aws_thing["state"]["reported"]:
                            capabilities_array = aws_thing["state"]["reported"][
                                "capabilities"
                            ]
                            capabilities_array.sort()
                            self.capabilities = get_capabilities(capabilities_array)
                            self.capabilities_str = json.dumps(capabilities_array)
            except Exception as e:
                _LOGGER.error(
                    "Error while getting capabilities for device %s: %s",
                    device_id,
                    str(e),
                )
                self.capabilities_str = str(e)

            

            match self.device_type:
                case DeviceTypeEnum.SPLIT_AC_TYPE_1:
                    self.data = TCL_SplitAC_Type1_DeviceData(
                        device_id,
                        aws_thing["state"]["reported"],
                        aws_thing["state"].get("delta", {}),
                    )
                case DeviceTypeEnum.SPLIT_AC_TYPE_2:
                    self.data = TCL_SplitAC_Type2_DeviceData(
                        device_id,
                        aws_thing["state"]["reported"],
                        aws_thing["state"].get("delta", {}),
                    )
                case DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    self.data = TCL_SplitAC_Fresh_Air_DeviceData(
                        device_id,
                        aws_thing["state"]["reported"],
                        aws_thing["state"].get("delta", {}),
                    )
                case DeviceTypeEnum.PORTABLE_AC:
                    self.data = TCL_PortableAC_DeviceData(
                        device_id,
                        aws_thing["state"]["reported"],
                        aws_thing["state"].get("delta", {}),
                    )

                case _:
                    self.data = None
        else:
            self.data = None

    capabilities_str: str
    capabilities: list[DeviceCapabilityEnum]
    supported_features: list[DeviceFeatureEnum]
    device_id: int
    device_type: str
    device_type_str: str
    has_aws_thing: str
    name: str
    firmware_version: str
    is_implemented_by_integration: bool
    storage: dict[str, any]
    data: (
        TCL_SplitAC_Type1_DeviceData
        | TCL_SplitAC_Fresh_Air_DeviceData
        | TCL_PortableAC_DeviceData
        | None
    ) = None

    def get_supported_modes(self) -> list[ModeEnum]:
        if DeviceFeatureEnum.MODE_HEAT not in self.supported_features:
            return [e.value for e in ModeEnum if e != ModeEnum.HEAT]
        return [e.value for e in ModeEnum]


def toDeviceInfo(device: Device) -> DeviceInfo:
    """Convert Device to DeviceInfo."""
    return DeviceInfo(
        name=f"{device.name} ({device.device_id}){'' if device.is_implemented_by_integration else ' (Not implemented)'}",
        manufacturer="TCL",
        model=device.device_type,
        sw_version=device.firmware_version,
        identifiers={
            (
                DOMAIN,
                f"TCL-{device.device_id}",
            )
        },
    )


async def get_device_storage(hass: HomeAssistant, device: Device) -> None:
    if device.device_type == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
        return await get_stored_spit_ac_fresh_data(hass, device.device_id)
    elif device.device_type == DeviceTypeEnum.SPLIT_AC_TYPE_1:
        return await get_stored_spit_ac_type1_data(hass, device.device_id)
    elif device.device_type == DeviceTypeEnum.SPLIT_AC_TYPE_2:
        return await get_stored_spit_ac_type2_data(hass, device.device_id)
    elif device.device_type == DeviceTypeEnum.PORTABLE_AC:
        return await get_stored_portable_ac_data(hass, device.device_id)
