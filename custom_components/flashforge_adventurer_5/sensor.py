from datetime import timedelta
import logging
from typing import Any, Callable, Dict, Optional, TypedDict

import async_timeout
from homeassistant import config_entries, core
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
import voluptuous as vol

from .const import DOMAIN
from .protocol import get_print_job_status

LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required("ip"): cv.string,
        vol.Required("port"): cv.string,
    }
)


class PrinterDefinition(TypedDict):
    ip: str
    port: int


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities: Callable,
) -> bool:
    config = hass.data[DOMAIN][config_entry.entry_id]
    if config_entry.options:
        config.update(config_entry.options)
    coordinator = FlashforgeAdventurer5Coordinator(hass, config)
    await coordinator.async_config_entry_first_refresh()
    sensors = [
        FlashforgeAdventurer5ProgressSensor(coordinator, config),
        FlashforgeAdventurer5TempNozzleSensor(coordinator, config),
        FlashforgeAdventurer5TempDesiredNozzleSensor(coordinator, config),
        FlashforgeAdventurer5TempBedSensor(coordinator, config),
        FlashforgeAdventurer5TempDesiredBedSensor(coordinator, config),
        FlashforgeAdventurer5MachineStatusSensor(coordinator, config),
        FlashforgeAdventurer5MoveModeSensor(coordinator, config),
        FlashforgeAdventurer5CurrentFileSensor(coordinator, config),
        FlashforgeAdventurer5LayerSensor(coordinator, config),
    ]
    async_add_entities(sensors, update_before_add=True)


class FlashforgeAdventurer5Coordinator(DataUpdateCoordinator):
    def __init__(self, hass, printer_definition: PrinterDefinition):
        super().__init__(
            hass,
            LOGGER,
            name="My sensor",
            update_interval=timedelta(seconds=60),
        )
        self.ip = printer_definition["ip_address"]
        self.port = printer_definition["port"]

    async def _async_update_data(self):
        async with async_timeout.timeout(5):
            return await get_print_job_status(self.ip, self.port)


class FlashforgeAdventurer5CommonPropertiesMixin:
    @property
    def name(self) -> str:
        return f"FlashForge Adventurer 5"

    @property
    def unique_id(self) -> str:
        return f"flashforge_adventurer_3_{self.ip}"


class BaseFlashforgeAdventurer5Sensor(
    FlashforgeAdventurer5CommonPropertiesMixin, CoordinatorEntity, Entity
):
    def __init__(
        self, coordinator: DataUpdateCoordinator, printer_definition: PrinterDefinition
    ) -> None:
        super().__init__(coordinator)
        self.ip = printer_definition["ip_address"]
        self.port = printer_definition["port"]
        self._available = False
        self.attrs = {}

    @property
    def state(self) -> Optional[str]:
        return self._state

    @property
    def device_state_attributes(self) -> Dict[str, Any]:
        return self.attrs

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        return self.attrs

    @callback
    def _handle_coordinator_update(self) -> None:
        self.attrs = self.coordinator.data
        self.async_write_ha_state()


class FlashforgeAdventurer5ProgressSensor(BaseFlashforgeAdventurer5Sensor):
    @property
    def name(self) -> str:
        return f"Progress"

    @property
    def unique_id(self) -> str:
        return f"{super().unique_id}_progress"

    @property
    def available(self) -> bool:
        return True

    @property
    def state(self) -> Optional[str]:
        return self.attrs.get("progress", 0)

    @property
    def icon(self) -> str:
        return "mdi:percent-circle"

    @property
    def unit_of_measurement(self) -> str:
        return "%"


class FlashforgeAdventurer5TempNozzleSensor(BaseFlashforgeAdventurer5Sensor):
    @property
    def name(self) -> str:
        return f"Nozzle"

    @property
    def unique_id(self) -> str:
        return f"{super().unique_id}_tempnozzle"

    @property
    def available(self) -> bool:
        return True

    @property
    def state(self) -> Optional[str]:
        return self.attrs.get("nozzle_temperature", 0)

    @property
    def icon(self) -> str:
        return "mdi:thermometer"

    @property
    def unit_of_measurement(self) -> str:
        return "ºC"


class FlashforgeAdventurer5TempDesiredNozzleSensor(BaseFlashforgeAdventurer5Sensor):
    @property
    def name(self) -> str:
        return f"Nozzle desired"

    @property
    def unique_id(self) -> str:
        return f"{super().unique_id}_tempnozzledesired"

    @property
    def available(self) -> bool:
        return True

    @property
    def state(self) -> Optional[str]:
        return self.attrs.get("desired_nozzle_temperature", 0)

    @property
    def icon(self) -> str:
        return "mdi:thermometer"

    @property
    def unit_of_measurement(self) -> str:
        return "ºC"


class FlashforgeAdventurer5TempBedSensor(BaseFlashforgeAdventurer5Sensor):
    @property
    def name(self) -> str:
        return f"Bed"

    @property
    def unique_id(self) -> str:
        return f"{super().unique_id}_tempbed"

    @property
    def available(self) -> bool:
        return True

    @property
    def state(self) -> Optional[str]:
        return self.attrs.get("bed_temperature", 0)

    @property
    def icon(self) -> str:
        return "mdi:thermometer"

    @property
    def unit_of_measurement(self) -> str:
        return "ºC"


class FlashforgeAdventurer5TempDesiredBedSensor(BaseFlashforgeAdventurer5Sensor):
    @property
    def name(self) -> str:
        return f"Bed desired"

    @property
    def unique_id(self) -> str:
        return f"{super().unique_id}_tempbeddesired"

    @property
    def available(self) -> bool:
        return True

    @property
    def state(self) -> Optional[str]:
        return self.attrs.get("desired_bed_temperature", 0)

    @property
    def icon(self) -> str:
        return "mdi:thermometer"

    @property
    def unit_of_measurement(self) -> str:
        return "ºC"


class FlashforgeAdventurer5MachineStatusSensor(BaseFlashforgeAdventurer5Sensor):
    @property
    def name(self) -> str:
        return f"Machine status"

    @property
    def unique_id(self) -> str:
        return f"{super().unique_id}_machine_status"

    @property
    def available(self) -> bool:
        return True

    @property
    def state(self) -> Optional[str]:
        return self.attrs.get("machine_status", "")

    @property
    def icon(self) -> str:
        return "mdi:state-machine"


class FlashforgeAdventurer5MoveModeSensor(BaseFlashforgeAdventurer5Sensor):
    @property
    def name(self) -> str:
        return f"Move mode"

    @property
    def unique_id(self) -> str:
        return f"{super().unique_id}_move_mode"

    @property
    def available(self) -> bool:
        return True

    @property
    def state(self) -> Optional[str]:
        return self.attrs.get("move_mode", "")

    @property
    def icon(self) -> str:
        return "mdi:auto-mode"


class FlashforgeAdventurer5CurrentFileSensor(BaseFlashforgeAdventurer5Sensor):
    @property
    def name(self) -> str:
        return f"Current file"

    @property
    def unique_id(self) -> str:
        return f"{super().unique_id}_current_file"

    @property
    def available(self) -> bool:
        return True

    @property
    def state(self) -> Optional[str]:
        return self.attrs.get("current_file", "")

    @property
    def icon(self) -> str:
        return "mdi:file-arrow-up-down"


class FlashforgeAdventurer5LayerSensor(BaseFlashforgeAdventurer5Sensor):
    @property
    def name(self) -> str:
        return f"Layer"

    @property
    def unique_id(self) -> str:
        return f"{super().unique_id}_layer"

    @property
    def available(self) -> bool:
        return True

    @property
    def state(self) -> Optional[str]:
        return self.attrs.get("layer", "")

    @property
    def icon(self) -> str:
        return "mdi:layers"
