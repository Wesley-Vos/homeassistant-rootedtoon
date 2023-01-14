"""Support for Toon sensors."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
    ENERGY_KILO_WATT_HOUR,
    PERCENTAGE,
    POWER_WATT,
    TEMP_CELSIUS,
    UnitOfVolume,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CURRENCY_EUR,
    CONF_P1_METER_PREFIX,
    CONF_P1_METER_SUFFIX,
    DOMAIN,
    VOLUME_CM3,
    VOLUME_LMIN,
)
from .coordinator import RootedToonDataUpdateCoordinator
from .models import (
    ToonBoilerDeviceEntity,
    ToonElectricityMeterDeviceEntity,
    ToonEntity,
    ToonGasMeterDeviceEntity,
    # ToonRequiredKeysMixin,
    # ToonSolarDeviceEntity,
    # ToonWaterMeterDeviceEntity,
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Toon sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    if coordinator.data.electricity_meter.available():
        entities.extend(
            [
                description.cls(
                    coordinator, entry, description, coordinator.data.electricity_meter
                )
                for description in ELECTRICITY_SENSOR_ENTITIES
            ]
        )
    if coordinator.data.gas_meter.available():
        entities.extend(
            [
                description.cls(
                    coordinator, entry, description, coordinator.data.gas_meter
                )
                for description in GAS_SENSOR_ENTITIES
            ]
        )

    if coordinator.data.thermostat.have_opentherm_boiler:
        entities.extend(
            [
                description.cls(
                    coordinator, entry, description, coordinator.data.thermostat
                )
                for description in BOILER_SENSOR_ENTITIES
            ]
        )

    async_add_entities(entities, True)


class ToonSensor(ToonEntity, SensorEntity):
    """Defines a Toon sensor."""

    entity_description: ToonSensorEntityDescription

    def __init__(
        self,
        coordinator: RootedToonDataUpdateCoordinator,
        entry: ConfigEntry,
        description: ToonSensorEntityDescription,
        device: Any,
    ) -> None:
        """Initialize the Toon sensor."""
        self.entity_description = description
        self.device = device
        super().__init__(coordinator)

        self._attr_unique_id = (
            f"{DOMAIN}_{entry.data.get(CONF_NAME)}_sensor_{description.key}"
        )
        name = f"{entry.data.get(CONF_P1_METER_PREFIX) } {description.name.lower()} { entry.data.get(CONF_P1_METER_SUFFIX)}".strip()
        self._attr_name = name[0].upper() + name[1:]

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        return getattr(self.device, self.entity_description.key)


class ToonElectricityMeterDeviceSensor(ToonSensor, ToonElectricityMeterDeviceEntity):
    """Defines a Electricity Meter sensor."""


class ToonGasMeterDeviceSensor(ToonSensor, ToonGasMeterDeviceEntity):
    """Defines a Gas Meter sensor."""


class ToonBoilerDeviceSensor(ToonSensor, ToonBoilerDeviceEntity):
    """Defines a Boiler sensor."""


@dataclass
class ToonSensorRequiredKeysMixin:
    """Mixin for sensor required keys."""

    cls: type[ToonSensor]


@dataclass
class ToonSensorEntityDescription(SensorEntityDescription, ToonSensorRequiredKeysMixin):
    """Describes Toon sensor entity."""


GAS_SENSOR_ENTITIES: tuple[ToonSensorEntityDescription, ...] = (
    ToonSensorEntityDescription(
        key="total",
        name="Gas total",
        native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.GAS,
        cls=ToonGasMeterDeviceSensor,
    ),
    ToonSensorEntityDescription(
        key="last_hour",
        name="Gas used last hour",
        native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.GAS,
        cls=ToonGasMeterDeviceSensor,
    ),
)

ELECTRICITY_SENSOR_ENTITIES: tuple[ToonSensorEntityDescription, ...] = (
    ToonSensorEntityDescription(
        key="electricity_return_high",
        name="Electricity return high",
        native_unit_of_measurement=POWER_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        cls=ToonElectricityMeterDeviceSensor,
    ),
    ToonSensorEntityDescription(
        key="electricity_return_low",
        name="Electricity return low",
        native_unit_of_measurement=POWER_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        cls=ToonElectricityMeterDeviceSensor,
    ),
    ToonSensorEntityDescription(
        key="electricity_delivery_high",
        name="Electricity delivery high",
        native_unit_of_measurement=POWER_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        cls=ToonElectricityMeterDeviceSensor,
    ),
    ToonSensorEntityDescription(
        key="electricity_delivery_low",
        name="Electricity delivery low",
        native_unit_of_measurement=POWER_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        cls=ToonElectricityMeterDeviceSensor,
    ),
    ToonSensorEntityDescription(
        key="electricity_returned_high",
        name="Electricity returned high",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        cls=ToonElectricityMeterDeviceSensor,
    ),
    ToonSensorEntityDescription(
        key="electricity_returned_low",
        name="Electricity returned low",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        cls=ToonElectricityMeterDeviceSensor,
    ),
    ToonSensorEntityDescription(
        key="electricity_delivered_high",
        name="Electricity delivered high",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        cls=ToonElectricityMeterDeviceSensor,
    ),
    ToonSensorEntityDescription(
        key="electricity_delivered_low",
        name="Electricity delivered low",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        cls=ToonElectricityMeterDeviceSensor,
    ),
)

BOILER_SENSOR_ENTITIES: tuple[ToonSensorEntityDescription, ...] = (
    ToonSensorEntityDescription(
        key="current_modulation_level",
        name="Boiler modulation Level",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:percent",
        state_class=SensorStateClass.MEASUREMENT,
        cls=ToonBoilerDeviceSensor,
    ),
)
