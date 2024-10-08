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
    UnitOfEnergy,
    PERCENTAGE,
    UnitOfPressure,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfVolume,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_BOILER_PREFIX,
    CONF_BOILER_SUFFIX,
    CONF_ENABLE_BOILER,
    CONF_ENABLE_P1_METER,
    CONF_P1_METER_PREFIX,
    CONF_P1_METER_SUFFIX,
    CONF_THERMOSTAT_PREFIX,
    CONF_THERMOSTAT_SUFFIX,
    DOMAIN,
    STATE_TO_PRESET_MODE_MAPPING,
)
from .coordinator import RootedToonDataUpdateCoordinator
from .models import (
    ToonBoilerDeviceEntity,
    ToonElectricityMeterDeviceEntity,
    ToonDeviceEntity,
    ToonEntity,
    ToonGasMeterDeviceEntity,
    ToonThermostatDeviceEntity,
)
from .util import upper_first


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Toon sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    boiler_enabled = entry.data.get(CONF_ENABLE_BOILER)
    p1_meter_enabled = entry.data.get(CONF_ENABLE_P1_METER)

    entities = []
    if p1_meter_enabled and coordinator.data.p1_meter.electricity_meter.available:
        entities.extend(
            [
                description.cls(
                    coordinator,
                    entry,
                    description,
                    coordinator.data.p1_meter.electricity_meter,
                )
                for description in ELECTRICITY_SENSOR_ENTITIES
            ]
        )
    if p1_meter_enabled and coordinator.data.p1_meter.gas_meter.available:
        entities.extend(
            [
                description.cls(
                    coordinator, entry, description, coordinator.data.p1_meter.gas_meter
                )
                for description in GAS_SENSOR_ENTITIES
            ]
        )

    if p1_meter_enabled and coordinator.data.smart_plugs.available:
        for smart_plug in coordinator.data.smart_plugs.devices:
            entities.extend(
                [
                    ToonSmartPlugDeviceSensor(
                        coordinator=coordinator,
                        entry=entry,
                        description=ToonSensorEntityDescription(
                            key="power",
                            name=f"{ smart_plug.name } power",
                            # suggested_display_precision=1,
                            native_unit_of_measurement=UnitOfPower.WATT,
                            state_class=SensorStateClass.MEASUREMENT,
                            device_class=SensorDeviceClass.POWER,
                            cls=ToonSmartPlugDeviceSensor,
                        ),
                        device=smart_plug,
                    ),
                    ToonSmartPlugDeviceSensor(
                        coordinator=coordinator,
                        entry=entry,
                        description=ToonSensorEntityDescription(
                            key="total",
                            name=f"{ smart_plug.name } energy",
                            # suggested_display_precision=3,
                            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR ,
                            state_class=SensorStateClass.TOTAL,
                            device_class=SensorDeviceClass.ENERGY,
                            cls=ToonSmartPlugDeviceSensor,
                        ),
                        device=smart_plug,
                    ),
                ]
            )

    if coordinator.data.thermostat.have_opentherm_boiler:
        if boiler_enabled and coordinator.data.boiler.available():
            entities.extend(
                [
                    description.cls(
                        coordinator, entry, description, coordinator.data.boiler
                    )
                    for description in BOILER_SENSOR_ENTITIES
                ]
            )
        entities.extend(
            [
                description.cls(
                    coordinator, entry, description, coordinator.data.thermostat
                )
                for description in THERMOSTAT_SENSOR_ENTITIES
            ]
        )
        entities.extend(
            [
                description.cls(
                    coordinator, entry, description, coordinator.data.thermostat
                )
                for description in THERMOSTAT_PROGRAM_SENSOR_ENTITIES
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

        self._attr_unique_id = f"{DOMAIN}_{entry.data.get(CONF_NAME)}_sensor_{ description.name.replace(' ', '') }_{description.key}"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        return getattr(self.device, self.entity_description.key)


class ToonP1MeterSensor(ToonSensor):
    """Defines a P1 Meter sensor."""

    def __init__(
        self,
        coordinator: RootedToonDataUpdateCoordinator,
        entry: ConfigEntry,
        description: ToonSensorEntityDescription,
        device: Any,
    ) -> None:
        super().__init__(coordinator, entry, description, device)

        name = f"{entry.data.get(CONF_P1_METER_PREFIX) } {description.name.lower()} { entry.data.get(CONF_P1_METER_SUFFIX)}".strip()
        self._attr_name = upper_first(name)


class ToonElectricityMeterDeviceSensor(
    ToonP1MeterSensor, ToonElectricityMeterDeviceEntity
):
    """Defines a Electricity Meter sensor."""


class ToonGasMeterDeviceSensor(ToonP1MeterSensor, ToonGasMeterDeviceEntity):
    """Defines a Gas Meter sensor."""


class ToonSmartPlugDeviceSensor(ToonSensor, ToonDeviceEntity):
    """Defines a Smart Plug sensor"""

    def __init__(
        self,
        coordinator: RootedToonDataUpdateCoordinator,
        entry: ConfigEntry,
        description: ToonSensorEntityDescription,
        device: Any,
    ) -> None:
        super().__init__(coordinator, entry, description, device)

        name = f"{entry.data.get(CONF_P1_METER_PREFIX) } {description.name.lower()} { entry.data.get(CONF_P1_METER_SUFFIX)}"
        self._attr_name = upper_first(name)


class ToonBoilerDeviceSensor(ToonSensor, ToonBoilerDeviceEntity):
    """Defines a Boiler sensor."""

    def __init__(
        self,
        coordinator: RootedToonDataUpdateCoordinator,
        entry: ConfigEntry,
        description: ToonSensorEntityDescription,
        device: Any,
    ) -> None:
        super().__init__(coordinator, entry, description, device)

        name = f"{entry.data.get(CONF_BOILER_PREFIX) } {description.name.lower()} { entry.data.get(CONF_BOILER_SUFFIX)}".strip()
        self._attr_name = upper_first(name)


class ToonThermostatDeviceSensor(ToonSensor, ToonThermostatDeviceEntity):
    """Defines a Thermostat sensor."""

    def __init__(
        self,
        coordinator: RootedToonDataUpdateCoordinator,
        entry: ConfigEntry,
        description: ToonSensorEntityDescription,
        device: Any,
    ) -> None:
        super().__init__(coordinator, entry, description, device)

        name = f"{entry.data.get(CONF_THERMOSTAT_PREFIX) } {description.name.lower()} { entry.data.get(CONF_THERMOSTAT_SUFFIX)}".strip()
        self._attr_name = upper_first(name)


class ToonDeviceSensor(ToonSensor, ToonDeviceEntity):
    """Defines a Toon sensor."""

    def __init__(
        self,
        coordinator: RootedToonDataUpdateCoordinator,
        entry: ConfigEntry,
        description: ToonSensorEntityDescription,
        device: Any,
    ) -> None:
        super().__init__(coordinator, entry, description, device)

        name = f"{entry.data.get(CONF_THERMOSTAT_PREFIX) } {description.name.lower()} { entry.data.get(CONF_THERMOSTAT_SUFFIX)}".strip()
        self._attr_name = upper_first(name)


class ToonThermostatProgramSensor(
    ToonThermostatDeviceSensor, ToonThermostatDeviceEntity
):
    """Defines a Thermostat sensor."""

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        return STATE_TO_PRESET_MODE_MAPPING.get(
            getattr(self.device, self.entity_description.key).state
        )

    @property
    def extra_state_attributes(self):
        return {
            "start": getattr(self.device, self.entity_description.key).start_datetime
        }


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
        state_class=SensorStateClass.TOTAL,
        device_class=SensorDeviceClass.GAS,
        cls=ToonGasMeterDeviceSensor,
    ),
)

ELECTRICITY_SENSOR_ENTITIES: tuple[ToonSensorEntityDescription, ...] = (
    ToonSensorEntityDescription(
        key="electricity_return_high",
        name="Electricity return high",
        native_unit_of_measurement=UnitOfPower.WATT,
        # suggested_display_precision=1,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        cls=ToonElectricityMeterDeviceSensor,
    ),
    ToonSensorEntityDescription(
        key="electricity_return_low",
        name="Electricity return low",
        native_unit_of_measurement=UnitOfPower.WATT,
        # suggested_display_precision=1,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        cls=ToonElectricityMeterDeviceSensor,
    ),
    ToonSensorEntityDescription(
        key="electricity_return",
        name="Electricity return",
        native_unit_of_measurement=UnitOfPower.WATT,
        # suggested_display_precision=1,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        cls=ToonElectricityMeterDeviceSensor,
    ),
    ToonSensorEntityDescription(
        key="electricity_delivery_high",
        name="Electricity delivery high",
        # suggested_display_precision=1,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        cls=ToonElectricityMeterDeviceSensor,
    ),
    ToonSensorEntityDescription(
        key="electricity_delivery_low",
        name="Electricity delivery low",
        # suggested_display_precision=1,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        cls=ToonElectricityMeterDeviceSensor,
    ),
    ToonSensorEntityDescription(
        key="electricity_delivery",
        name="Electricity delivery",
        # suggested_display_precision=1,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        cls=ToonElectricityMeterDeviceSensor,
    ),
    ToonSensorEntityDescription(
        key="electricity_returned_high",
        name="Electricity returned high",
        # suggested_display_precision=3,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR ,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        cls=ToonElectricityMeterDeviceSensor,
    ),
    ToonSensorEntityDescription(
        key="electricity_returned_low",
        name="Electricity returned low",
        # suggested_display_precision=3,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        cls=ToonElectricityMeterDeviceSensor,
    ),
    ToonSensorEntityDescription(
        key="electricity_returned",
        name="Electricity returned",
        # suggested_display_precision=3,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR ,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        cls=ToonElectricityMeterDeviceSensor,
    ),
    ToonSensorEntityDescription(
        key="electricity_delivered_high",
        name="Electricity delivered high",
        # suggested_display_precision=3,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR ,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        cls=ToonElectricityMeterDeviceSensor,
    ),
    ToonSensorEntityDescription(
        key="electricity_delivered_low",
        name="Electricity delivered low",
        # suggested_display_precision=3,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR ,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        cls=ToonElectricityMeterDeviceSensor,
    ),
    ToonSensorEntityDescription(
        key="electricity_delivered",
        name="Electricity delivered",
        # suggested_display_precision=3,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR ,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        cls=ToonElectricityMeterDeviceSensor,
    ),
)

THERMOSTAT_SENSOR_ENTITIES: tuple[ToonSensorEntityDescription, ...] = (
    ToonSensorEntityDescription(
        key="current_modulation_level",
        name="Boiler modulation level",
        # suggested_display_precision=0,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:percent",
        state_class=SensorStateClass.MEASUREMENT,
        cls=ToonBoilerDeviceSensor,
    ),
    ToonSensorEntityDescription(
        key="current_setpoint",
        name="Thermostat Setpoint",
        # suggested_display_precision=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        cls=ToonThermostatDeviceSensor,
    ),
    ToonSensorEntityDescription(
        key="current_display_temperature",
        name="Temperature",
        # suggested_display_precision=2,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        cls=ToonDeviceSensor,
    ),
)
THERMOSTAT_PROGRAM_SENSOR_ENTITIES: tuple[ToonSensorEntityDescription, ...] = (
    ToonSensorEntityDescription(
        key="next_program_state",
        name="Thermostat next program",
        icon="mdi:calendar",
        cls=ToonThermostatProgramSensor,
    ),
)

BOILER_SENSOR_ENTITIES: tuple[ToonSensorEntityDescription, ...] = (
    ToonSensorEntityDescription(
        key="pressure",
        name="Boiler pressure",
        # suggested_display_precision=2,
        native_unit_of_measurement=UnitOfPressure.BAR,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        cls=ToonBoilerDeviceSensor,
    ),
)
