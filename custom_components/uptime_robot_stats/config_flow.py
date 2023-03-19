import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_DEVICE_ID
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN


class UptimeRobotConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Uptime Robot configuration flow."""

    async def async_step_user(self, user_input=None):
        """Handle a flow start."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_API_KEY): str,
                        vol.Required(CONF_DEVICE_ID): str,
                    }
                ),
            )

        return self.async_create_entry(
            title=user_input[CONF_DEVICE_ID],
            data=user_input,
        )

    async def async_step_hass_config(self, user_input=None):
        """Handle a Home Assistant configuration request."""
        return await self.async_step_user(user_input)