"""Constants for the Toon integration."""
from datetime import timedelta
from homeassistant.const import DEVICE_CLASS_POWER, DEVICE_CLASS_ENERGY
from homeassistant.components.sensor import (
    STATE_CLASS_TOTAL,
    STATE_CLASS_MEASUREMENT,
)


DOMAIN = "rootedtoon"

CONF_MIGRATE = "migrate"

DEFAULT_SCAN_INTERVAL = 10
DEFAULT_MAX_TEMP = 30.0
DEFAULT_MIN_TEMP = 6.0
DEFAULT_NAME = "Toon"
DEFAULT_PORT = 80

CURRENCY_EUR = "EUR"
VOLUME_CM3 = "CM3"
VOLUME_LHOUR = "L/H"
VOLUME_LMIN = "L/MIN"

CONF_THERMOSTAT_PREFIX = "thermostat_prefix"
CONF_THERMOSTAT_SUFFIX = "thermostat_suffix"
CONF_P1_METER_PREFIX = "p1_meter_prefix"
CONF_P1_METER_SUFFIX = "p1_meter_suffix"
