"""The uptime_robot component."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.const import Platform

from .api import UptimeRobotApiError, UptimeRobotClient
from .const import (
    CONF_API_KEY,
    CONF_MONITOR_ID,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the uptime_robot component from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    session = aiohttp_client.async_get_clientsession(hass)
    client = UptimeRobotClient(
        session,
        entry.data[CONF_API_KEY],
        entry.data[CONF_MONITOR_ID],
    )
    coordinator = UptimeRobotDataUpdateCoordinator(hass, client)

    try:
        await coordinator.async_config_entry_first_refresh()
    except UptimeRobotApiError as err:
        raise ConfigEntryNotReady(err) from err

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "client": client,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the uptime_robot component."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


class UptimeRobotDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate data updates from the Uptime Robot API."""

    def __init__(self, hass: HomeAssistant, client: UptimeRobotClient) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="uptime_robot_stats",
            update_interval=DEFAULT_UPDATE_INTERVAL,
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.client.async_get_monitor_stats()
        except UptimeRobotApiError as err:
            raise UpdateFailed(str(err)) from err
