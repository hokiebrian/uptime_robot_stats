"""The Uptime Robot sensor """
from datetime import timedelta
import aiohttp
import asyncio
import time
from typing import Any, Dict, Optional

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity, SensorStateClass, SensorDeviceClass
from homeassistant.const import CONF_API_KEY, CONF_ID
import homeassistant.helpers.config_validation as cv

SCAN_INTERVAL = timedelta(seconds=120)

BASE_URL = "https://api.uptimerobot.com/v2/getMonitors"

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Uptime Robot sensor from a config entry."""
    api_key = config_entry.data["api_key"]
    monitor_id = config_entry.data["monitor_id"]
    sensor = UptimeRobotSensor(api_key, monitor_id)
    async_add_entities([sensor], True)

class UptimeRobotSensor(SensorEntity):
    """Representation of an Uptime Robot sensor."""

    _attr_icon = "mdi:clock"
    _attr_native_unit_of_measurement = "ms"
    _attr_state_class: SensorStateClass = SensorStateClass.MEASUREMENT

    def __init__(self, api_key: str, monitor_id: str) -> None:
        """Initialize the sensor."""
        self._api_key = api_key
        self._monitor_id = monitor_id
        self._state: Optional[float] = None
        self._extra_attributes: Dict[str, Any] = {}

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"Uptime Robot {str(self._monitor_id)}"

    @property
    def state(self) -> Optional[float]:
        """Return the state of the sensor."""
        return self._state

    @property
    def unique_id(self):
        return f"uptime{str(self._monitor_id)}"

    @property
    def extra_state_attributes(self) -> Optional[Dict[str, Any]]:
        """Return the state attributes of the sensor."""
        return self._extra_attributes

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        start_time = int(time.time()) - 1800
        payload = f"api_key={self._api_key}&monitors={self._monitor_id}&format=json&logs=0&all_time_uptime_ratio=1&custom_uptime_ratios=1&response_times=1&response_times_average=5&response_times_start_date={start_time}"
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "cache-control": "no-cache",
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            try:
                async with session.post(BASE_URL, data=payload, timeout=8) as response:
                    if response.status != 200:
                        self._state = None
                        self._extra_attributes = {
                            "response_time": float(0),
                            "response_avg": float(0),
                            "uptime_percent_24h": float(100),
                            "uptime_percent_all_time": float(100),
                        }
                        return

                    data = await response.json()
                    self._state = float(data["monitors"][0]["response_times"][0]["value"])
                    self._extra_attributes = {
                        "response_time": float(data["monitors"][0]["response_times"][0]["value"]),
                        "response_avg": float(data["monitors"][0]["average_response_time"]),
                        "uptime_percent_24h": float(data["monitors"][0]["custom_uptime_ratio"]),
                        "uptime_percent_all_time": float(data["monitors"][0]["all_time_uptime_ratio"]),
                    }
            except (ValueError, KeyError):
                self._state = None
                self._extra_attributes = {
                    "response_time": float(0),
                    "response_avg": float(0),
                    "uptime_percent_24h": float(100),
                    "uptime_percent_all_time": float(100),
                }
