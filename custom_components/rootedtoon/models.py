"""DataUpdate Coordinator, and base Entity and Device models for Toon."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.const import CONF_NAME
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_BOILER_PREFIX,
    CONF_BOILER_SUFFIX,
    CONF_P1_METER_PREFIX,
    CONF_P1_METER_SUFFIX,
    DEVICE_BOILER_MODULE,
    DEVICE_ELECTRICITY,
    DEVICE_P1_METER,
    DOMAIN,
    ENECO,
)
from .coordinator import RootedToonDataUpdateCoordinator
from .util import upper_first


class ToonEntity(CoordinatorEntity[RootedToonDataUpdateCoordinator]):
    """Defines a base Toon entity."""


class ToonDisplayDeviceEntity(ToonEntity):
    """Defines a Toon display device entity."""


class ToonElectricityMeterDeviceEntity(ToonEntity):
    """Defines a Electricity Meter device entity."""

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this entity."""
        config = self.coordinator.config
        conf_name = config.get(CONF_NAME)
        name = f"{config.get(CONF_P1_METER_PREFIX)} electricity meter {config.get(CONF_P1_METER_SUFFIX)}"

        return DeviceInfo(
            name=upper_first(name),
            identifiers={(DOMAIN, conf_name, DEVICE_ELECTRICITY)},  # type: ignore[arg-type]
            via_device=(DOMAIN, conf_name, DEVICE_P1_METER),  # type: ignore[typeddict-item]
        )


class ToonGasMeterDeviceEntity(ToonEntity):
    """Defines a Gas Meter device entity."""

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this entity."""
        config = self.coordinator.config
        conf_name = config.get(CONF_NAME)
        name = f"{config.get(CONF_P1_METER_PREFIX)} gas meter {config.get(CONF_P1_METER_SUFFIX)}"

        return DeviceInfo(
            name=upper_first(name),
            identifiers={(DOMAIN, conf_name, "gas")},  # type: ignore[arg-type]
            via_device=(DOMAIN, conf_name, DEVICE_ELECTRICITY),  # type: ignore[typeddict-item]
        )


class ToonBoilerModuleDeviceEntity(ToonEntity):
    """Defines a Boiler Module device entity."""

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this entity."""
        config = self.coordinator.config
        conf_name = config.get(CONF_NAME)
        name = f"{config.get(CONF_BOILER_PREFIX)} boiler module {config.get(CONF_BOILER_SUFFIX)}"

        return DeviceInfo(
            name=upper_first(name),
            manufacturer=ENECO,
            identifiers={(DOMAIN, conf_name, DEVICE_BOILER_MODULE)},  # type: ignore[arg-type]
            via_device=(DOMAIN, conf_name),
        )


class ToonBoilerDeviceEntity(ToonEntity):
    """Defines a Boiler device entity."""

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this entity."""

        config = self.coordinator.config
        conf_name = config.get(CONF_NAME)
        name = (
            f"{config.get(CONF_BOILER_PREFIX)} boiler {config.get(CONF_BOILER_SUFFIX)}"
        )
        return DeviceInfo(
            name=upper_first(name),
            identifiers={(DOMAIN, conf_name, "boiler")},  # type: ignore[arg-type]
            via_device=(DOMAIN, conf_name, DEVICE_BOILER_MODULE),  # type: ignore[typeddict-item]
        )


# @dataclass
# class ToonRequiredKeysMixin:
#     """Mixin for required keys."""

#     section: str
#     measurement: str
