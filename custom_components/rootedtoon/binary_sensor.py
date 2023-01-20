"""Support for Toon binary sensors."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_NAME
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_BOILER_PREFIX,
    CONF_BOILER_SUFFIX,
    DOMAIN,
    CONF_THERMOSTAT_PREFIX,
    CONF_THERMOSTAT_SUFFIX,
)
from .coordinator import RootedToonDataUpdateCoordinator
from .models import (
    ToonBoilerDeviceEntity,
    ToonBoilerModuleDeviceEntity,
    ToonDisplayDeviceEntity,
    ToonEntity,
)
from .util import upper_first
from typing import Any


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up a Toon binary sensor based on a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]

    entities = [
        description.cls(coordinator, entry, description, data.toon.thermostat)
        for description in BINARY_SENSOR_ENTITIES
    ]
    if data.toon.thermostat.have_opentherm_boiler:
        entities.extend(
            [
                description.cls(coordinator, entry, description, data.toon.thermostat)
                for description in BINARY_SENSOR_ENTITIES_BOILER
            ]
        )

    async_add_entities(entities, True)


class ToonBinarySensor(ToonEntity, BinarySensorEntity):
    """Defines an Toon binary sensor."""

    entity_description: ToonBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: RootedToonDataUpdateCoordinator,
        entry: ConfigEntry,
        description: ToonBinarySensorEntityDescription,
        device: Any,
    ) -> None:
        """Initialize the Toon sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self.device = device

        self._attr_unique_id = (
            f"{DOMAIN}_{entry.data.get(CONF_NAME)}_binary_sensor_{description.key}"
        )

    @property
    def is_on(self) -> bool | None:
        """Return the status of the binary sensor."""
        value = getattr(self.device, self.entity_description.key)

        if self.entity_description.inverted:
            return not value

        return value


class ToonBoilerBinarySensor(ToonBinarySensor, ToonBoilerDeviceEntity):
    """Defines a Boiler binary sensor."""

    def __init__(
        self,
        coordinator: RootedToonDataUpdateCoordinator,
        entry: ConfigEntry,
        description: ToonBinarySensorEntityDescription,
        device: Any,
    ) -> None:
        """Initialize the Toon sensor."""
        super().__init__(coordinator, entry, description, device)
        name = f"{entry.data.get(CONF_BOILER_PREFIX) } {description.name.lower()} { entry.data.get(CONF_BOILER_SUFFIX)}".strip()
        self._attr_name = upper_first(name)


class ToonDisplayBinarySensor(ToonBinarySensor, ToonDisplayDeviceEntity):
    """Defines a Toon Display binary sensor."""

    def __init__(
        self,
        coordinator: RootedToonDataUpdateCoordinator,
        entry: ConfigEntry,
        description: ToonBinarySensorEntityDescription,
        device: Any,
    ) -> None:
        """Initialize the Toon sensor."""
        super().__init__(coordinator, entry, description, device)
        name = f"{entry.data.get(CONF_THERMOSTAT_PREFIX) } {description.name.lower()} { entry.data.get(CONF_THERMOSTAT_SUFFIX)}".strip()
        self._attr_name = upper_first(name)


class ToonBoilerModuleBinarySensor(ToonBinarySensor, ToonBoilerModuleDeviceEntity):
    """Defines a Boiler module binary sensor."""

    def __init__(
        self,
        coordinator: RootedToonDataUpdateCoordinator,
        entry: ConfigEntry,
        description: ToonBinarySensorEntityDescription,
        device: Any,
    ) -> None:
        """Initialize the Toon sensor."""
        super().__init__(coordinator, entry, description, device)
        name = f"{entry.data.get(CONF_BOILER_PREFIX) } {description.name.lower()} { entry.data.get(CONF_BOILER_SUFFIX)}".strip()
        self._attr_name = upper_first(name)


@dataclass
class ToonBinarySensorRequiredKeysMixin:
    """Mixin for binary sensor required keys."""

    cls: type[ToonBinarySensor]


@dataclass
class ToonBinarySensorEntityDescription(
    BinarySensorEntityDescription, ToonBinarySensorRequiredKeysMixin
):
    """Describes Toon binary sensor entity."""

    inverted: bool = False


BINARY_SENSOR_ENTITIES = (
    ToonBinarySensorEntityDescription(
        key="boiler_module_connected",
        name="Boiler module connection",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        cls=ToonBoilerModuleBinarySensor,
    ),
    ToonBinarySensorEntityDescription(
        key="program_overridden",
        name="Thermostat program override",
        icon="mdi:gesture-tap",
        cls=ToonDisplayBinarySensor,
    ),
)

BINARY_SENSOR_ENTITIES_BOILER: tuple[ToonBinarySensorEntityDescription, ...] = (
    ToonBinarySensorEntityDescription(
        key="heating",
        name="Boiler heating",
        icon="mdi:fire",
        cls=ToonBoilerBinarySensor,
    ),
    ToonBinarySensorEntityDescription(
        key="hot_tapwater",
        name="Hot tap water",
        icon="mdi:water-pump",
        cls=ToonBoilerBinarySensor,
    ),
    ToonBinarySensorEntityDescription(
        key="pre_heating",
        name="Boiler preheating",
        icon="mdi:fire",
        cls=ToonBoilerBinarySensor,
    ),
    ToonBinarySensorEntityDescription(
        key="burner",
        name="Boiler burner",
        icon="mdi:fire",
        cls=ToonBoilerBinarySensor,
    ),
    ToonBinarySensorEntityDescription(
        key="error_found",
        name="Boiler status",
        device_class=BinarySensorDeviceClass.PROBLEM,
        icon="mdi:alert",
        cls=ToonBoilerBinarySensor,
    ),
    ToonBinarySensorEntityDescription(
        key="opentherm_communication_error",
        name="OpenTherm connection",
        inverted=True,
        device_class=BinarySensorDeviceClass.PROBLEM,
        icon="mdi:check-network-outline",
        cls=ToonBoilerBinarySensor,
    ),
)
