"""The Uptime Robot sensor """
from datetime import timedelta
import asyncio
import time
import logging
import aiohttp
from typing import Any, Dict, Optional
from homeassistant.core import HomeAssistant
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from .const import BASE_URL

SCAN_INTERVAL = timedelta(seconds=60)

async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
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
    _LOGGER = logging.getLogger(__name__)

    def __init__(self, api_key: str, monitor_id: str) -> None:
        """Initialize the sensor."""
        self._LOGGER = logging.getLogger(__name__)
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

                    self._state = float(data.get("monitors", [{}])[0].get("response_times", [{}])[0].get("value", 0))
                    self._extra_attributes = {
                        "response_time": float(data.get("monitors", [{}])[0].get("response_times", [{}])[0].get("value", 0)),
                        "response_avg": float(data.get("monitors", [{}])[0].get("average_response_time", 0)),
                        "uptime_percent_24h": float(data.get("monitors", [{}])[0].get("custom_uptime_ratio", 100)),
                        "uptime_percent_all_time": float(data.get("monitors", [{}])[0].get("all_time_uptime_ratio", 100)),
                    }

            except (asyncio.exceptions.TimeoutError):
                _LOGGER.error("Error occurred while updating sensor.")
                return
