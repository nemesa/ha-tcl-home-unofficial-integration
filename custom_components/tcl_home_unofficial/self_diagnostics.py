from homeassistant.core import HomeAssistant
import logging
from homeassistant.helpers import storage
from .const import get_device_self_dignose_storege_key

_LOGGER = logging.getLogger(__name__)


class SelfDiagnostics:
    def __init__(self, hass: HomeAssistant, device_id: str) -> None:
        self.hass = hass
        self.device_id = device_id
        self.init_state: dict[str, any] | None = None
        self.init_desc: str | None = None
        self.prev_state: dict[str, any] | None = None
        self.steps: list[any] = []
        self.ignored_properties = ["capabilities", "errorCode", "authFlag"]

    async def get_stored_data(self) -> dict[str, any] | None:
        key = get_device_self_dignose_storege_key(self.device_id)
        data_storage: storage.Store[dict] = storage.Store(
            hass=self.hass, version=1, key=key
        )
        data = await data_storage.async_load()
        return data

    async def set_stored_data(self, data: dict[str, any]) -> dict[str, any] | None:
        key = get_device_self_dignose_storege_key(self.device_id)
        data_storage: storage.Store[dict] = storage.Store(
            hass=self.hass, version=1, key=key
        )

        await data_storage.async_save(data=data)

    async def clearStorage(self):
        await self.set_stored_data(None)

    async def addState(
        self, action_description: str, aws_thing: dict[str, any]
    ) -> None:
        is_first = False
        if self.init_state is None:
            stored = await self.get_stored_data()
            if stored is not None:
                self.init_state = stored.get("initState", None)
                self.init_desc = stored.get("initDesc", None)
                self.prev_state = stored.get("prevState", None)
                self.steps = stored.get("steps", None)
            else:
                self.init_state = aws_thing
                self.init_desc = action_description
                is_first = True

        _LOGGER.info(
            "Adding self diagnostics state for action: %s (is_first:%s)",
            action_description,
            is_first,
        )
        if not is_first:
            metadata_desired = aws_thing["metadata"]["desired"]
            metadata_reported = aws_thing["metadata"]["reported"]
            prev_metadata_desired = self.prev_state["metadata"]["desired"]
            prev_metadata_reported = self.prev_state["metadata"]["reported"]
            changed_desired_keys = []
            changed_reported_keys = []
            for key, value in metadata_desired.items():
                if key not in self.ignored_properties:
                    ts_d = value.get("timestamp", None)
                    ts_r = metadata_reported[key].get("timestamp", None)
                    prev_ts_d = prev_metadata_desired[key].get("timestamp", None)
                    prev_ts_r = prev_metadata_reported[key].get("timestamp", None)
                    if ts_d != prev_ts_d:
                        changed_desired_keys.append(key)
                    if ts_r != prev_ts_r:
                        changed_reported_keys.append(key)

            step_data = {
                "actionDescription": action_description,
                "changedDesiredKeys": changed_desired_keys,
                "changedReportedKeys": changed_reported_keys,
                "changedDesiredData": {},
                "changedReportedData": {},
            }

            for key in changed_desired_keys:
                currentData = aws_thing["state"]["desired"][key]
                prevData = self.prev_state["state"]["desired"][key]
                step_data["changedDesiredData"][key] = {
                    "from": prevData,
                    "to": currentData,
                }

            for key in changed_reported_keys:
                currentData = aws_thing["state"]["reported"][key]
                prevData = self.prev_state["state"]["reported"][key]
                step_data["changedReportedData"][key] = {
                    "from": prevData,
                    "to": currentData,
                }

            self.steps.append(step_data)

        self.prev_state = aws_thing
        await self.set_stored_data(
            {
                "initState": self.init_state,
                "initDesc": self.init_desc,
                "prevState": aws_thing,
                "steps": self.steps,
            }
        )
