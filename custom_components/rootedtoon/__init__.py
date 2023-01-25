"""Support for Toon van Eneco devices."""
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, device_registry as dr

from .const import CONF_ENABLE_P1_METER, DEVICE_P1_METER, DOMAIN, ENECO
from .coordinator import RootedToonDataUpdateCoordinator

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.CALENDAR,
    Platform.CLIMATE,
    Platform.SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Toon from a config entry."""
    coordinator = RootedToonDataUpdateCoordinator(hass, entry=entry)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

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

    if entry.data.get(CONF_ENABLE_P1_METER) and coordinator.data.has_meter_adapter:
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
