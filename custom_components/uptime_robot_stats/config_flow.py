import voluptuous as vol
import aiohttp
from homeassistant import config_entries
from .const import DOMAIN


class UptimeRobotConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Uptime Robot configuration flow."""

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            # Validate the API key
            api_key = user_input["api_key"]
            headers = {
                "content-type": "application/x-www-form-urlencoded",
                "cache-control": "no-cache",
            }
            async with aiohttp.ClientSession(headers=headers) as session:
                try:
                    url = "https://api.uptimerobot.com/v2/getAccountDetails"
                    payload = f"api_key={api_key}&format=json"
                    async with session.post(url, data=payload, timeout=8) as response:
                        data = await response.json()
                        if not data["stat"] == "ok":
                            errors["api_key"] = "Invalid API key"
                except:
                    errors["api_key"] = "Unable to validate API key"

            # Validate the monitor ID
            monitor_id = user_input["monitor_id"]
            async with aiohttp.ClientSession(headers=headers) as session:
                try:
                    url = "https://api.uptimerobot.com/v2/getMonitors"
                    payload = f"api_key={api_key}&monitors={monitor_id}&format=json"
                    async with session.post(url, data=payload, timeout=8) as response:
                        data = await response.json()
                        if not data["stat"] == "ok":
                            errors["monitor_id"] = "Invalid monitor ID"
                except:
                    errors["monitor_id"] = "Unable to validate monitor ID"

            if not errors:
                return self.async_create_entry(
                    title=user_input["monitor_id"],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("api_key"): str,
                    vol.Required("monitor_id"): str,
                }
            ),
            errors=errors,
        )
