"""Constants for the Toon integration."""
from datetime import timedelta

from rootedtoonapi import (
    ACTIVE_STATE_AWAY,
    ACTIVE_STATE_COMFORT,
    ACTIVE_STATE_HOME,
    ACTIVE_STATE_SLEEP,
)

from homeassistant.components.climate import (
    PRESET_AWAY,
    PRESET_COMFORT,
    PRESET_HOME,
    PRESET_SLEEP,
)

DOMAIN = "rootedtoon"

CONF_BOILER_PREFIX = "boiler_prefix"
CONF_BOILER_SUFFIX = "boiler_suffix"
CONF_ENABLE_P1_METER = "conf_enable_p1_meter"
CONF_ENABLE_BOILER = "conf_enable_boiler"
CONF_ENABLE_PROGRAM = "conf_enable_program"
CONF_MIGRATE = "migrate"
CONF_P1_METER_PREFIX = "p1_meter_prefix"
CONF_P1_METER_SUFFIX = "p1_meter_suffix"
CONF_SCAN_INTERVAL_BOILER = "scan_interval_boiler"
CONF_SCAN_INTERVAL_P1_METER = "scan_interval_p1_meter"
CONF_SCAN_INTERVAL_PROGRAM = "scan_interval_program"
CONF_SCAN_INTERVAL_THERMOSTAT = "scan_interval_thermostat"
CONF_THERMOSTAT_SUFFIX = "thermostat_suffix"
CONF_THERMOSTAT_PREFIX = "thermostat_prefix"

CURRENCY_EUR = "EUR"

DEFAULT_SCAN_INTERVAL = 10
DEFAULT_MAX_TEMP = 30.0
DEFAULT_MIN_TEMP = 6.0
DEFAULT_NAME = "Toon"
DEFAULT_PORT = 80

DEVICE_BOILER = "boiler"
DEVICE_BOILER_MODULE = "boiler_module"
DEVICE_ELECTRICITY = "electricity"
DEVICE_P1_METER = "p1_meter"
DEVICE_THERMOSTAT = "thermostat"

ENECO = "Eneco"

UPDATE_FUNC = "update_func"
UPDATE_INTERVAL = "update_interval"

STATE_TO_PRESET_MODE_MAPPING = {
    ACTIVE_STATE_AWAY: PRESET_AWAY,
    ACTIVE_STATE_COMFORT: PRESET_COMFORT,
    ACTIVE_STATE_HOME: PRESET_HOME,
    ACTIVE_STATE_SLEEP: PRESET_SLEEP,
}

PRESET_MODE_TO_STATE_MAPPING = {
    value: key for key, value in STATE_TO_PRESET_MODE_MAPPING.items()
}

VOLUME_CM3 = "CM3"
VOLUME_LHOUR = "L/H"
VOLUME_LMIN = "L/MIN"
