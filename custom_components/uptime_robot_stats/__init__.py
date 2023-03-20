"""The uptime_robot component."""
DOMAIN = "uptime_robot_stats"
CONF_API_KEY = "api_key"
CONF_DEVICE_ID = "monitors"

#async def async_setup(hass, config):
#    """Set up the uptime_robot component."""
#    hass.async_create_task(
#        hass.config_entries.flow.async_init(
#            DOMAIN, context={"source": "hass_config"}, data=None
#        )
#    )
#    return True

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
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    return True
