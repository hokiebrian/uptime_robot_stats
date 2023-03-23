import voluptuous as vol
from homeassistant import config_entries
#from homeassistant.const import CONF_API_KEY, CONF_DEVICE_ID
import homeassistant.helpers.config_validation as cv

from . import DOMAIN

class UptimeRobotConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Uptime Robot configuration flow."""

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_DEVICE_ID],
                data=user_input,
        )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("api_key"): str,
                    vol.Required("monitors"): str,
                }
            ),
            errors=errors,
        )
