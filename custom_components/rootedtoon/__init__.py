"""Support for Toon van Eneco devices."""
import voluptuous as vol

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import CoreState, HomeAssistant
from homeassistant.helpers import config_validation as cv, device_registry as dr
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .coordinator import RootedToonDataUpdateCoordinator

PLATFORMS = [
    # Platform.BINARY_SENSOR,
    Platform.CLIMATE,
    # Platform.SENSOR,
    # Platform.SWITCH,
]


# async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
#     """Set up the Toon components."""
#     if DOMAIN not in config:
#         return True

#     hass.async_create_task(
#         hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_IMPORT})
#     )

#     return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Toon from a config entry."""
    coordinator = RootedToonDataUpdateCoordinator(hass, entry=entry)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Register device for the Meter Adapter, since it will have no entities.
    # device_registry = dr.async_get(hass)
    # device_registry.async_get_or_create(
    #     config_entry_id=entry.entry_id,
    #     identifiers={
    #         (
    #             DOMAIN,
    #             coordinator.data.agreement.agreement_id,
    #             "meter_adapter",
    #         )  # type: ignore[arg-type]
    #     },
    #     manufacturer="Eneco",
    #     name="Meter Adapter",
    #     via_device=(DOMAIN, coordinator.data.agreement.agreement_id),
    # )

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
