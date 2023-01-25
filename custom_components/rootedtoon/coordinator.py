"""Provides the Rooted Toon DataUpdateCoordinator."""
from __future__ import annotations

from datetime import datetime, timedelta
from functools import reduce
from math import gcd
import logging

from rootedtoonapi import Devices, Toon, ToonError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_ENABLE_BOILER,
    CONF_ENABLE_P1_METER,
    CONF_ENABLE_PROGRAM,
    CONF_SCAN_INTERVAL_BOILER,
    CONF_SCAN_INTERVAL_P1_METER,
    CONF_SCAN_INTERVAL_PROGRAM,
    CONF_SCAN_INTERVAL_THERMOSTAT,
    DOMAIN,
    UPDATE_INTERVAL,
    UPDATE_FUNC,
)

_LOGGER = logging.getLogger(__name__)


class RootedToonDataUpdateCoordinator(DataUpdateCoordinator[Devices]):
    """Class to manage fetching Toon data from single endpoint."""

    def __init__(self, hass: HomeAssistant, *, entry: ConfigEntry) -> None:
        """Initialize global Toon data updater."""
        self.entry = entry
        self.config = entry.data
        self.update_tick: int = 0

        self.toon = Toon(
            host=self.config.get(CONF_HOST),
            port=self.config.get(CONF_PORT),
            session=async_get_clientsession(hass),
        )

        devices = (
            (
                self.config.get(CONF_ENABLE_BOILER),
                int(self.config.get(CONF_SCAN_INTERVAL_BOILER)),
                self.toon.update_boiler,
            ),
            (
                self.config.get(CONF_ENABLE_P1_METER),
                int(self.config.get(CONF_SCAN_INTERVAL_P1_METER)),
                self.toon.update_energy_meter,
            ),
            (
                self.config.get(CONF_ENABLE_PROGRAM),
                int(self.config.get(CONF_SCAN_INTERVAL_PROGRAM)),
                self.toon.update_program,
            ),
            (
                True,
                int(self.config.get(CONF_SCAN_INTERVAL_THERMOSTAT)),
                self.toon.update_climate,
            ),
        )

        update_intervals = [device[1] for device in devices if device[0]]
        common_update_interval = reduce(gcd, update_intervals)

        self.update_intervals = [
            {
                UPDATE_INTERVAL: device[1] / common_update_interval,
                UPDATE_FUNC: device[2],
            }
            for device in devices
            if device[0]
        ]

        self.max_tick_size = max(
            update_interval.get(UPDATE_INTERVAL)
            for update_interval in self.update_intervals
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=common_update_interval),
        )

    async def _async_update_data(self) -> Devices:
        """Fetch data from Toon."""
        try:
            for update in self.update_intervals:
                if self.update_tick % update.get(UPDATE_INTERVAL) == 0:
                    await update.get(UPDATE_FUNC)()

            self.update_tick = (self.update_tick + 1) % self.max_tick_size
            return self.toon._devices

        except ToonError as error:
            raise UpdateFailed(f"Invalid response from API: {error}") from error
