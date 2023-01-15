"""Config flow to configure the Toon component."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import (
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    CONF_BOILER_PREFIX,
    CONF_BOILER_SUFFIX,
    CONF_P1_METER_PREFIX,
    CONF_P1_METER_SUFFIX,
    CONF_THERMOSTAT_PREFIX,
    CONF_THERMOSTAT_SUFFIX,
    DOMAIN,
)

# Validation of the user's configuration
CONFIG_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
        vol.Optional(CONF_BOILER_PREFIX, default=""): str,
        vol.Optional(CONF_BOILER_SUFFIX, default=""): str,
        vol.Optional(CONF_P1_METER_PREFIX, default=""): str,
        vol.Optional(CONF_P1_METER_SUFFIX, default=""): str,
        vol.Optional(CONF_THERMOSTAT_PREFIX, default=""): str,
        vol.Optional(CONF_THERMOSTAT_SUFFIX, default=""): str,
    }
)


class RootedToonFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Toon config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=CONFIG_SCHEMA)

        return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)
