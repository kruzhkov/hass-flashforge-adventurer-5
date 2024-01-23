import logging
from typing import Callable

from homeassistant import config_entries, core
from homeassistant.components.mjpeg.camera import MjpegCamera

from .const import DOMAIN
from .sensor import (
    FlashforgeAdventurer5CommonPropertiesMixin,
    PrinterDefinition,
)

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities: Callable,
) -> bool:
    config = hass.data[DOMAIN][config_entry.entry_id]
    # Update our config to include new repos and remove those that have been removed.
    if config_entry.options:
        config.update(config_entry.options)
    sensors = [
        FlashforgeAdventurer5Camera(config),
    ]
    async_add_entities(sensors, update_before_add=True)


class FlashforgeAdventurer5Camera(
    FlashforgeAdventurer5CommonPropertiesMixin, MjpegCamera
):
    def __init__(self, printer_definition: PrinterDefinition) -> None:
        self.ip = printer_definition["ip_address"]
        self.port = printer_definition["port"]
        super().__init__(
            name=self.name, mjpeg_url=self.stream_url, still_image_url=None
        )

    @property
    def name(self) -> str:
        return f"{super().name} camera"

    @property
    def unique_id(self) -> str:
        return f"{super().unique_id}_camera"

    @property
    def stream_url(self) -> str:
        return f"http://{self.ip}:8080/?action=stream"
