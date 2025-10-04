"""Config Flow for Uptime Robot Monitor Component."""

from __future__ import annotations

import asyncio
import logging

import voluptuous as vol
import aiohttp
import async_timeout

from homeassistant import config_entries
from homeassistant.helpers import aiohttp_client

from .const import (
    BASE_API_URL,
    BASE_URL,
    CONF_API_KEY,
    CONF_MONITOR_ID,
    DOMAIN,
    RESPONSE_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)


class UptimeRobotConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Uptime Robot configuration flow."""

    _HEADERS = {
        "content-type": "application/x-www-form-urlencoded",
        "cache-control": "no-cache",
    }

    async def _validate_data(self, url: str, payload: str) -> bool:
        """Validate user input by contacting the API."""
        session = aiohttp_client.async_get_clientsession(self.hass)
        try:
            async with async_timeout.timeout(RESPONSE_TIMEOUT):
                response = await session.post(
                    url,
                    data=payload,
                    headers=self._HEADERS,
                )
        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.debug("Validation request failed: %s", err)
            return False

        if response.status != 200:
            _LOGGER.debug("Validation request failed with status: %s", response.status)
            return False

        try:
            data = await response.json()
        except aiohttp.ContentTypeError as err:
            _LOGGER.debug("Unexpected response payload: %s", err)
            return False

        return data.get("stat") == "ok"

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            # Validate the API key
            api_key = user_input[CONF_API_KEY]
            url = f"{BASE_API_URL}/getAccountDetails"
            payload = f"api_key={api_key}&format=json"
            if not await self._validate_data(url, payload):
                errors["api_key"] = "Unable to validate API key"

            # Validate the monitor ID
            monitor_id = user_input[CONF_MONITOR_ID]
            url = BASE_URL
            payload = f"api_key={api_key}&monitors={monitor_id}&format=json"
            if not await self._validate_data(url, payload):
                errors["monitor_id"] = "Unable to validate monitor ID"

            if not errors:
                return self.async_create_entry(
                    title=user_input[CONF_MONITOR_ID],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): str,
                    vol.Required(CONF_MONITOR_ID): str,
                }
            ),
            errors=errors,
        )
