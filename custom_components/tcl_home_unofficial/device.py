"""."""

import json
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from .device_enums import ModeEnum, DehumidifierModeEnum
from .device_capabilities import DeviceCapabilityEnum, get_capabilities
from .device_features import getSupportedFeatures, DeviceFeatureEnum
from .device_portable_ac import (
    TCL_PortableAC_DeviceData,
    get_stored_portable_ac_data,
    handle_portable_ac_mode_change,
)
from .device_spit_ac_fresh_air import (
    TCL_SplitAC_Fresh_Air_DeviceData,
    get_stored_spit_ac_fresh_data,
    handle_split_ac_freshair_mode_change,
)
from .device_spit_ac import (
    TCL_SplitAC_DeviceData,
    get_stored_spit_ac_data,
    handle_split_ac_mode_change,
)
from .device_window_ac import (
    TCL_WindowAC_DeviceData,
    get_stored_window_ac_data,
    handle_window_ac_mode_change,
)
from .device_dehumidifier import (
    TCL_Dehumidifier_DeviceData,
    get_stored_dehumidifier_data,
    handle_dehumidifier_mode_change,
)

from .device_types import DeviceTypeEnum, calculateDeviceType
from .device_data_storage import get_stored_data, safe_set_value, set_stored_data
from .tcl import GetThingsResponseData

_LOGGER = logging.getLogger(__name__)


class Device:
    """Device."""

    def __init__(
        self,
        aws_thing: dict | None,
        tcl_thing: GetThingsResponseData | None = None,
        device_storage: dict | None = None,
    ) -> None:
        self.device_id = "noId"
        self.product_key = None
        self.device_type_str = ""
        self.name = "noName"
        self.storage = device_storage
        self.firmware_version = "noVersion"
        self.has_aws_thing = "false"
        self.capabilities_str = ""
        self.capabilities = []
        self.supported_features = []
        self.mode_enum_to_value_mapp = {}
        self.mode_value_to_enum_mapp = {}
        self.is_online = False
        if tcl_thing is not None:
            self.is_online = tcl_thing.is_online
            self.product_key = tcl_thing.product_key
            self.device_type_str = tcl_thing.device_name
            self.device_id = tcl_thing.device_id
            self.name = tcl_thing.nick_name
            self.firmware_version = tcl_thing.firmware_version

        self.device_type = calculateDeviceType(self.device_type_str)
        self.is_implemented_by_integration = self.device_type is not None
        if aws_thing is not None:
            self.has_aws_thing = "true"
            try:
                if "state" in aws_thing:
                    if "reported" in aws_thing["state"]:
                        self.supported_features = getSupportedFeatures(
                            self.device_type, aws_thing["state"]["reported"], self.storage
                        )
                        self.create_mode_mapps()
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
                    self.device_id,
                    str(e),
                )
                self.capabilities_str = str(e)

            match self.device_type:
                case DeviceTypeEnum.SPLIT_AC:
                    self.data = TCL_SplitAC_DeviceData(
                        device_id=self.device_id,
                        aws_thing_state=aws_thing["state"]["reported"],
                        delta=aws_thing["state"].get("delta", {}),
                    )
                case DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
                    self.data = TCL_SplitAC_Fresh_Air_DeviceData(
                        device_id=self.device_id,
                        aws_thing_state=aws_thing["state"]["reported"],
                        delta=aws_thing["state"].get("delta", {}),
                    )
                case DeviceTypeEnum.PORTABLE_AC:
                    self.data = TCL_PortableAC_DeviceData(
                        device_id=self.device_id,
                        aws_thing_state=aws_thing["state"]["reported"],
                        delta=aws_thing["state"].get("delta", {}),
                    )
                case DeviceTypeEnum.WINDOW_AC:
                    self.data = TCL_WindowAC_DeviceData(
                        device_id=self.device_id,
                        aws_thing_state=aws_thing["state"]["reported"],
                        delta=aws_thing["state"].get("delta", {}),
                    )
                case DeviceTypeEnum.DEHUMIDIFIER:
                    self.data = TCL_Dehumidifier_DeviceData(
                        device_id=self.device_id,
                        aws_thing_state=aws_thing["state"]["reported"],
                        delta=aws_thing["state"].get("delta", {}),
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
    is_online: bool
    is_implemented_by_integration: bool
    storage: dict[str, any]
    mode_enum_to_value_mapp: dict[str, int]
    mode_value_to_enum_mapp: dict[int, str]
    data: (
        TCL_SplitAC_DeviceData
        | TCL_SplitAC_Fresh_Air_DeviceData
        | TCL_PortableAC_DeviceData
        | TCL_WindowAC_DeviceData
        | TCL_Dehumidifier_DeviceData
        | None
    ) = None

    def get_supported_modes(self) -> list[ModeEnum | DehumidifierModeEnum]:
        modes: list[ModeEnum | DehumidifierModeEnum] = []
        if DeviceFeatureEnum.INTERNAL_IS_AC in self.supported_features:        
            if DeviceFeatureEnum.MODE_AC_COOL in self.supported_features:
                modes.append(ModeEnum.COOL)
            if DeviceFeatureEnum.MODE_AC_HEAT in self.supported_features:
                modes.append(ModeEnum.HEAT)
            if DeviceFeatureEnum.MODE_AC_DEHUMIDIFICATION in self.supported_features:
                modes.append(ModeEnum.DEHUMIDIFICATION)
            if DeviceFeatureEnum.MODE_AC_FAN in self.supported_features:
                modes.append(ModeEnum.FAN)
            if DeviceFeatureEnum.MODE_AC_AUTO in self.supported_features:
                modes.append(ModeEnum.AUTO)
        if DeviceFeatureEnum.INTERNAL_IS_DEHUMIDIFIER in self.supported_features:
            if DeviceFeatureEnum.MODE_DEHUMIDIFIER_DRY in self.supported_features:
                modes.append(DehumidifierModeEnum.DRY)
            if DeviceFeatureEnum.MODE_DEHUMIDIFIER_COMFORT in self.supported_features:
                modes.append(DehumidifierModeEnum.COMFORT)
            if DeviceFeatureEnum.MODE_DEHUMIDIFIER_CONTINUE in self.supported_features:
                modes.append(DehumidifierModeEnum.CONTINUE)
            if DeviceFeatureEnum.MODE_DEHUMIDIFIER_TURBO in self.supported_features:
                modes.append(DehumidifierModeEnum.TURBO)
        return modes

    def create_mode_mapps(self) -> None:
        self.mode_enum_to_value_mapp: dict[str, int] = {}
        self.mode_value_to_enum_mapp: dict[int, str] = {}
        work_mode = 0
        if DeviceFeatureEnum.INTERNAL_IS_AC in self.supported_features:
            if DeviceFeatureEnum.MODE_AC_AUTO in self.supported_features:
                self.mode_enum_to_value_mapp[ModeEnum.AUTO] = work_mode
                self.mode_value_to_enum_mapp[work_mode] = ModeEnum.AUTO
                work_mode += 1
            else:
                self.mode_enum_to_value_mapp[ModeEnum.AUTO] = 0

            if DeviceFeatureEnum.MODE_AC_COOL in self.supported_features:
                self.mode_enum_to_value_mapp[ModeEnum.COOL] = work_mode
                self.mode_value_to_enum_mapp[work_mode] = ModeEnum.COOL
                work_mode += 1
            else:
                self.mode_enum_to_value_mapp[ModeEnum.COOL] = 0

            if DeviceFeatureEnum.MODE_AC_DEHUMIDIFICATION in self.supported_features:
                self.mode_enum_to_value_mapp[ModeEnum.DEHUMIDIFICATION] = work_mode
                self.mode_value_to_enum_mapp[work_mode] = ModeEnum.DEHUMIDIFICATION
                work_mode += 1
            else:
                self.mode_enum_to_value_mapp[ModeEnum.DEHUMIDIFICATION] = 0

            if DeviceFeatureEnum.MODE_AC_FAN in self.supported_features:
                self.mode_enum_to_value_mapp[ModeEnum.FAN] = work_mode
                self.mode_value_to_enum_mapp[work_mode] = ModeEnum.FAN
                work_mode += 1
            else:
                self.mode_enum_to_value_mapp[ModeEnum.FAN] = 0

            if DeviceFeatureEnum.MODE_AC_HEAT in self.supported_features:
                self.mode_enum_to_value_mapp[ModeEnum.HEAT] = work_mode
                self.mode_value_to_enum_mapp[work_mode] = ModeEnum.HEAT
                work_mode += 1
            else:
                self.mode_enum_to_value_mapp[ModeEnum.HEAT] = 0
        
        if DeviceFeatureEnum.INTERNAL_IS_DEHUMIDIFIER in self.supported_features:
            if DeviceFeatureEnum.MODE_DEHUMIDIFIER_DRY in self.supported_features:
                self.mode_enum_to_value_mapp[DehumidifierModeEnum.DRY] = work_mode
                self.mode_value_to_enum_mapp[work_mode] = DehumidifierModeEnum.DRY
                work_mode += 1
            else:
                self.mode_enum_to_value_mapp[DehumidifierModeEnum.DRY] = 0
                
            if DeviceFeatureEnum.MODE_DEHUMIDIFIER_TURBO in self.supported_features:
                self.mode_enum_to_value_mapp[DehumidifierModeEnum.TURBO] = work_mode
                self.mode_value_to_enum_mapp[work_mode] = DehumidifierModeEnum.TURBO
                work_mode += 1
            else:
                self.mode_enum_to_value_mapp[DehumidifierModeEnum.TURBO] = 0
                
            if DeviceFeatureEnum.MODE_DEHUMIDIFIER_COMFORT in self.supported_features:
                self.mode_enum_to_value_mapp[DehumidifierModeEnum.COMFORT] = work_mode
                self.mode_value_to_enum_mapp[work_mode] = DehumidifierModeEnum.COMFORT
                work_mode += 1
            else:
                self.mode_enum_to_value_mapp[DehumidifierModeEnum.COMFORT] = 0
                
            if DeviceFeatureEnum.MODE_DEHUMIDIFIER_CONTINUE in self.supported_features:
                self.mode_enum_to_value_mapp[DehumidifierModeEnum.CONTINUE] = work_mode
                self.mode_value_to_enum_mapp[work_mode] = DehumidifierModeEnum.CONTINUE
                work_mode += 1
            else:
                self.mode_enum_to_value_mapp[DehumidifierModeEnum.CONTINUE] = 0


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
    elif device.device_type == DeviceTypeEnum.SPLIT_AC:
        return await get_stored_spit_ac_data(hass, device.device_id)
    elif device.device_type == DeviceTypeEnum.PORTABLE_AC:
        return await get_stored_portable_ac_data(hass, device.device_id)
    elif device.device_type == DeviceTypeEnum.WINDOW_AC:
        return await get_stored_window_ac_data(hass, device.device_id)
    elif device.device_type == DeviceTypeEnum.DEHUMIDIFIER:
        return await get_stored_dehumidifier_data(hass, device.device_id)


def get_desired_state_for_mode_change(
    device: Device, stored_data: dict, value: ModeEnum
) -> dict:
    desired_state = {"workMode": device.mode_enum_to_value_mapp.get(value, 0)}
    if device.device_type == DeviceTypeEnum.SPLIT_AC_FRESH_AIR:
        desired_state = handle_split_ac_freshair_mode_change(
            desired_state=desired_state,
            value=value,
            supported_features=device.supported_features,
            stored_data=stored_data,
        )
    elif device.device_type == DeviceTypeEnum.SPLIT_AC:
        desired_state = handle_split_ac_mode_change(
            desired_state=desired_state,
            value=value,
            supported_features=device.supported_features,
            stored_data=stored_data,
        )
    elif device.device_type == DeviceTypeEnum.PORTABLE_AC:
        desired_state = handle_portable_ac_mode_change(
            desired_state=desired_state,
            value=value,
            supported_features=device.supported_features,
            stored_data=stored_data,
        )
    elif device.device_type == DeviceTypeEnum.WINDOW_AC:
        desired_state = handle_window_ac_mode_change(
            desired_state=desired_state,
            value=value,
            supported_features=device.supported_features,
            stored_data=stored_data,
        )
    elif device.device_type == DeviceTypeEnum.DEHUMIDIFIER:
        desired_state = handle_dehumidifier_mode_change(
            desired_state=desired_state,
            value=value,
            supported_features=device.supported_features,
            stored_data=stored_data,
        )
    return desired_state


async def store_rn_prode_data(
    hass: HomeAssistant, device_id, rn_probe_data: dict
) -> dict:
    stored_data = await get_stored_data(hass, device_id)
    stored_data, need_save = safe_set_value(
        data=stored_data,
        path="non_user_config.rn_probe_data",
        value=rn_probe_data,
        overwrite_if_exists=True,
    )
    if need_save:
        await set_stored_data(hass, device_id, stored_data)
    return await get_stored_data(hass, device_id)
