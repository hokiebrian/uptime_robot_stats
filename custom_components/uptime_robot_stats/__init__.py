"""The uptime_robot component."""
DOMAIN = "uptime_robot_stats"
CONF_API_KEY = "api_key"
CONF_ID = "monitor_id"

async def async_setup_entry(hass, entry):
    """Set up the uptime_robot component from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data[CONF_API_KEY]
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass, entry):
    """Unload the uptime_robot component."""
    await hass.services.async_remove(entry, "sensor")
    return True
