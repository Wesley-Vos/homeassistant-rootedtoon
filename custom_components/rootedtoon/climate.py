"""Support for Toon thermostat."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from typing import Any

from rootedtoonapi import (
    ACTIVE_STATE_AWAY,
    ACTIVE_STATE_COMFORT,
    ACTIVE_STATE_HOME,
    ACTIVE_STATE_SLEEP,
    PROGRAM_STATE_OFF,
    PROGRAM_STATE_ON,
    PROGRAM_STATE_OVERRIDE,
)

from homeassistant.components.climate import (
    PRESET_AWAY,
    PRESET_COMFORT,
    PRESET_HOME,
    PRESET_SLEEP,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, CONF_NAME, TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import RootedToonDataUpdateCoordinator
from .const import (
    CONF_THERMOSTAT_PREFIX,
    CONF_THERMOSTAT_SUFFIX,
    DEFAULT_MAX_TEMP,
    DEFAULT_MIN_TEMP,
    DOMAIN,
    ENECO,
)
from .helpers import toon_exception_handler
from .models import ToonDisplayDeviceEntity
from .util import upper_first


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up a Toon binary sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ToonThermostatDevice(coordinator, entry.data)])


class ToonThermostatDevice(ToonDisplayDeviceEntity, ClimateEntity):
    """Representation of a Toon climate device."""

    _attr_icon = "mdi:thermostat"
    _attr_max_temp = DEFAULT_MAX_TEMP
    _attr_min_temp = DEFAULT_MIN_TEMP
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.PRESET_MODE
    )
    _attr_temperature_unit = TEMP_CELSIUS

    def __init__(
        self, coordinator: RootedToonDataUpdateCoordinator, config: Any
    ) -> None:
        """Initialize Toon climate entity."""
        super().__init__(coordinator)
        self._attr_hvac_modes = [HVACMode.HEAT, HVACMode.AUTO]
        self._attr_preset_modes = [
            PRESET_AWAY,
            PRESET_COMFORT,
            PRESET_HOME,
            PRESET_SLEEP,
        ]
        name = f"{config.get(CONF_THERMOSTAT_PREFIX)} thermostat {config.get(CONF_THERMOSTAT_SUFFIX)}".strip()
        self._attr_name = upper_first(name)
        self._attr_unique_id = f"{DOMAIN}_{config.get(CONF_NAME)}_climate"
        self.config = config

    @property
    def hvac_action(self) -> HVACAction:
        """Return the current running hvac operation."""
        if (
            self.coordinator.data.thermostat.heating
            or self.coordinator.data.thermostat.pre_heating
        ):
            return HVACAction.HEATING
        return HVACAction.IDLE

    @property
    def hvac_mode(self) -> HVACMode:
        """Return the current HVAC Mode"""
        if self.coordinator.data.thermostat.program:
            return HVACMode.AUTO
        return HVACMode.HEAT

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode, e.g., home, away, temp."""
        mapping = {
            ACTIVE_STATE_AWAY: PRESET_AWAY,
            ACTIVE_STATE_COMFORT: PRESET_COMFORT,
            ACTIVE_STATE_HOME: PRESET_HOME,
            ACTIVE_STATE_SLEEP: PRESET_SLEEP,
        }
        return mapping.get(self.coordinator.data.thermostat.active_state)

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self.coordinator.data.thermostat.current_display_temperature

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        return self.coordinator.data.thermostat.current_setpoint

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the current state of the burner."""
        return {
            "burner_info": self.coordinator.data.thermostat.burner_state,
            "modulation_level": self.coordinator.data.thermostat.current_modulation_level,
        }

    @toon_exception_handler
    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Change the setpoint of the thermostat."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        await self.coordinator.toon.set_current_setpoint(temperature)

    @toon_exception_handler
    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        mapping = {
            PRESET_AWAY: ACTIVE_STATE_AWAY,
            PRESET_COMFORT: ACTIVE_STATE_COMFORT,
            PRESET_HOME: ACTIVE_STATE_HOME,
            PRESET_SLEEP: ACTIVE_STATE_SLEEP,
        }
        if preset_mode in mapping:
            await self.coordinator.toon.set_active_state(mapping[preset_mode])

    @toon_exception_handler
    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        mapping = {HVACMode.AUTO: PROGRAM_STATE_ON, HVACMode.HEAT: PROGRAM_STATE_OFF}
        await self.coordinator.toon.set_hvac_mode(mapping[hvac_mode])

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            name=self.name,
            manufacturer=ENECO,
            via_device=(DOMAIN, self.config.get(CONF_NAME)),
        )
