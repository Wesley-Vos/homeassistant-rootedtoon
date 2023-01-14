"""DataUpdate Coordinator, and base Entity and Device models for Toon."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.const import CONF_NAME
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import RootedToonDataUpdateCoordinator


class ToonEntity(CoordinatorEntity[RootedToonDataUpdateCoordinator]):
    """Defines a base Toon entity."""


class ToonDisplayDeviceEntity(ToonEntity):
    """Defines a Toon display device entity."""


class ToonElectricityMeterDeviceEntity(ToonEntity):
    """Defines a Electricity Meter device entity."""

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this entity."""
        conf_name = self.coordinator.config.get(CONF_NAME)
        return DeviceInfo(
            name="Electricity Meter",
            identifiers={(DOMAIN, conf_name, "electricity")},  # type: ignore[arg-type]
            via_device=(DOMAIN, conf_name, "p1_meter"),  # type: ignore[typeddict-item]
        )


class ToonGasMeterDeviceEntity(ToonEntity):
    """Defines a Gas Meter device entity."""

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this entity."""
        conf_name = self.coordinator.config.get(CONF_NAME)
        return DeviceInfo(
            name="Gas Meter",
            identifiers={(DOMAIN, conf_name, "gas")},  # type: ignore[arg-type]
            via_device=(DOMAIN, conf_name, "electricity"),  # type: ignore[typeddict-item]
        )


# class ToonWaterMeterDeviceEntity(ToonEntity):
#     """Defines a Water Meter device entity."""

#     @property
#     def device_info(self) -> DeviceInfo:
#         """Return device information about this entity."""
#         return DeviceInfo(
#             name="Water Meter",
#             identifiers={(DOMAIN, "toon", "water")},  # type: ignore[arg-type]
#             via_device=(DOMAIN, "toon", "electricity"),  # type: ignore[typeddict-item]
#         )


# class ToonSolarDeviceEntity(ToonEntity):
#     """Defines a Solar Device device entity."""

#     @property
#     def device_info(self) -> DeviceInfo:
#         """Return device information about this entity."""
#         return DeviceInfo(
#             name="Solar Panels",
#             identifiers={(DOMAIN, "toon", "solar")},  # type: ignore[arg-type]
#             via_device=(DOMAIN, "toon", "meter_adapter"),  # type: ignore[typeddict-item]
#         )


class ToonBoilerModuleDeviceEntity(ToonEntity):
    """Defines a Boiler Module device entity."""

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this entity."""
        conf_name = self.coordinator.config.get(CONF_NAME)
        return DeviceInfo(
            name="Boiler Module",
            manufacturer="Eneco",
            identifiers={(DOMAIN, conf_name, "boiler_module")},  # type: ignore[arg-type]
            via_device=(DOMAIN, conf_name),
        )


class ToonBoilerDeviceEntity(ToonEntity):
    """Defines a Boiler device entity."""

    @property
    def device_info(self) -> DeviceInfo:
        conf_name = self.coordinator.config.get(CONF_NAME)
        """Return device information about this entity."""
        return DeviceInfo(
            name="Boiler",
            identifiers={(DOMAIN, conf_name, "boiler")},  # type: ignore[arg-type]
            via_device=(DOMAIN, conf_name, "boiler_module"),  # type: ignore[typeddict-item]
        )


# @dataclass
# class ToonRequiredKeysMixin:
#     """Mixin for required keys."""

#     section: str
#     measurement: str
