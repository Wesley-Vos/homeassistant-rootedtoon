"""Provides the Rooted Toon DataUpdateCoordinator."""
from __future__ import annotations

from datetime import timedelta
import logging
import secrets

from rootedtoonapi import Status, Toon, ToonError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class RootedToonDataUpdateCoordinator(DataUpdateCoordinator[Status]):
    """Class to manage fetching Toon data from single endpoint."""

    def __init__(self, hass: HomeAssistant, *, entry: ConfigEntry) -> None:
        """Initialize global Toon data updater."""
        self.entry = entry
        config = entry.data

        self.toon = Toon(
            host=config[CONF_HOST],
            port=config[CONF_PORT],
            session=async_get_clientsession(hass),
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> Status:
        """Fetch data from Toon."""
        try:
            return await self.toon.update_climate()
        except ToonError as error:
            raise UpdateFailed(f"Invalid response from API: {error}") from error
