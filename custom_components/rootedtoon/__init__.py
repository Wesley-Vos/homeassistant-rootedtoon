"""Support for Toon van Eneco devices."""
import voluptuous as vol

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME, Platform
from homeassistant.core import CoreState, HomeAssistant
from homeassistant.helpers import config_validation as cv, device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_SCAN_INTERVAL_BOILER,
    CONF_SCAN_INTERVAL_P1_METER,
    CONF_SCAN_INTERVAL_THERMOSTAT,
    DEVICE_P1_METER,
    DOMAIN,
    ENECO,
)
from .coordinator import RootedToonDataUpdateCoordinator
from .util import DataStruct

from rootedtoonapi import Toon

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.CLIMATE,
    Platform.SENSOR,
    # Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Toon from a config entry."""
    # coordinator = RootedToonDataUpdateCoordinator(hass, entry=entry)
    toon = Toon(
        host=entry.data.get(CONF_HOST),
        port=entry.data.get(CONF_PORT),
        session=async_get_clientsession(hass),
    )
    coordinators = [
        RootedToonDataUpdateCoordinator(
            hass,
            entry=entry,
            toon=toon,
            update_interval=entry.data.get(CONF_SCAN_INTERVAL_BOILER),
        ),
        RootedToonDataUpdateCoordinator(
            hass,
            entry=entry,
            toon=toon,
            update_interval=entry.data.get(CONF_SCAN_INTERVAL_P1_METER),
        ),
        RootedToonDataUpdateCoordinator(
            hass,
            entry=entry,
            toon=toon,
            update_interval=entry.data.get(CONF_SCAN_INTERVAL_THERMOSTAT),
        ),
    ]

    for coordinator in coordinators:
        await coordinator.async_config_entry_first_refresh()

    data = DataStruct(coordinators=coordinators, toon=toon)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = data

    conf_name = entry.data.get(CONF_NAME)
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={
            (
                DOMAIN,
                conf_name,
            )  # type: ignore[arg-type]
        },
        manufacturer=ENECO,
        name=conf_name,
        model="Toon",
    )

    if data.toon.has_meter_adapter:
        # Register device for the Meter Adapter, since it will have no entities.
        device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={
                (
                    DOMAIN,
                    conf_name,
                    DEVICE_P1_METER,
                )  # type: ignore[arg-type]
            },
            manufacturer=ENECO,
            name="P1 Meter",
            via_device=(DOMAIN, conf_name),
        )

    # Spin up the platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Toon config entry."""

    # Unload entities for this entry/device.
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # Cleanup
    if unload_ok:
        del hass.data[DOMAIN][entry.entry_id]

    return unload_ok
