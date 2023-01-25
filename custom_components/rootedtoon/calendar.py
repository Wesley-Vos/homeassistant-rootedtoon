"""Support for Toon thermostat."""
from __future__ import annotations

from datetime import datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import RootedToonDataUpdateCoordinator
from .const import CONF_THERMOSTAT_PREFIX, CONF_THERMOSTAT_SUFFIX, DOMAIN

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from .models import ToonThermostatDeviceEntity
from .util import upper_first


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up a Toon calendar based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ToonThermostatCalendar(coordinator, entry)])


class ToonThermostatCalendar(CalendarEntity, ToonThermostatDeviceEntity):
    """Representation of a Toon calendar."""

    _attr_icon = "mdi:thermostat"

    def __init__(
        self, coordinator: RootedToonDataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize Toon climate entity."""
        super().__init__(coordinator)

        name = f"{entry.data.get(CONF_THERMOSTAT_PREFIX) } calendar { entry.data.get(CONF_THERMOSTAT_SUFFIX)}".strip()
        self._attr_name = upper_first(name)

    def _map_to_calendar_event(self, data):
        return CalendarEvent(
            start=data.start_datetime,
            end=data.end_datetime,
            summary=data.state,
        )

    @property
    def event(self):
        events = self.coordinator.data.thermostat.internal_program.events
        if len(events) > 0:
            return self._map_to_calendar_event(events[0])
        return None

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> list[CalendarEvent]:
        events = self.coordinator.data.thermostat.internal_program.events
        return [
            self._map_to_calendar_event(e)
            for e in filter(
                lambda e: e.end_datetime >= start_date and e.start_datetime <= end_date,
                events,
            )
        ]
