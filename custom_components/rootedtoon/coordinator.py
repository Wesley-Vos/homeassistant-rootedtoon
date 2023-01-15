"""Provides the Rooted Toon DataUpdateCoordinator."""
from __future__ import annotations

from datetime import timedelta
import logging

from rootedtoonapi import Devices, Toon, ToonError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class RootedToonDataUpdateCoordinator(DataUpdateCoordinator[Devices]):
    """Class to manage fetching Toon data from single endpoint."""

    def __init__(self, hass: HomeAssistant, *, entry: ConfigEntry) -> None:
        """Initialize global Toon data updater."""
        self.entry = entry
        self.config = entry.data

        self.toon = Toon(
            host=self.config.get(CONF_HOST),
            port=self.config.get(CONF_PORT),
            session=async_get_clientsession(hass),
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=self.config.get(CONF_SCAN_INTERVAL)),
        )

    async def _async_update_data(self) -> Devices:
        """Fetch data from Toon."""
        try:
            return await self.toon.update()
        except ToonError as error:
            raise UpdateFailed(f"Invalid response from API: {error}") from error
