"""Provides the Rooted Toon DataUpdateCoordinator."""
from __future__ import annotations

from datetime import timedelta
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
    CONF_SCAN_INTERVAL_BOILER,
    CONF_SCAN_INTERVAL_P1_METER,
    CONF_SCAN_INTERVAL_THERMOSTAT,
    DOMAIN,
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
        update_intervals = [
            self.config.get(conf_var)
            for conf_var in [
                CONF_SCAN_INTERVAL_BOILER,
                CONF_SCAN_INTERVAL_P1_METER,
                CONF_SCAN_INTERVAL_THERMOSTAT,
            ]
        ]
        common_update_interval = reduce(gcd, update_intervals)

        self.update_intervals = [
            {
                "interval": int(update_intervals[0] / common_update_interval),
                "func": self.toon.update_boiler,
            },
            {
                "interval": int(update_intervals[1] / common_update_interval),
                "func": self.toon.update_energy_meter,
            },
            {
                "interval": int(update_intervals[2] / common_update_interval),
                "func": self.toon.update_climate,
            },
        ]
        self.max_tick_size = max(
            update_interval.get("interval") for update_interval in self.update_intervals
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
            # print(self.update_intervals)
            print(self.update_tick, self.config.get(CONF_HOST))
            for update in self.update_intervals:
                # print(update)
                # print(self.update_tick % update.get("interval"))
                if self.update_tick % update.get("interval") == 0:
                    print("Exjecute", update.get("func"))
                    await update.get("func")()

            self.update_tick = (self.update_tick + 1) % self.max_tick_size
            return self.toon._devices
            # return await self.toon.update()

        except ToonError as error:
            raise UpdateFailed(f"Invalid response from API: {error}") from error
