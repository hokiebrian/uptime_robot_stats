"""The uptime_robot component."""

from homeassistant.core import HomeAssistant
from .const import DOMAIN
CONF_API_KEY = "api_key"
CONF_ID = "monitor_id"

async def async_setup_entry(hass: HomeAssistant, entry):
    """Set up the uptime_robot component from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data[CONF_API_KEY]
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry):
    """Unload the uptime_robot component."""
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    return True
