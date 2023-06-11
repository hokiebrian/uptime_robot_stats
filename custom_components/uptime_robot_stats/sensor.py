from datetime import timedelta
import asyncio
import time
import logging
from typing import Any, Dict, Optional
import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from .const import BASE_URL

SCAN_INTERVAL = timedelta(seconds=60)
RESPONSE_TIMEOUT = 8
LOOKBACK_PERIOD = 1800

_LOGGER = logging.getLogger(__name__)


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
        await self._fetch_sensor_data()

    async def _fetch_sensor_data(self):
        """Fetch the data from the API and update the state and attributes."""
        start_time = int(time.time()) - LOOKBACK_PERIOD
        payload = self._generate_payload(start_time)
        headers = self._generate_headers()

        async with aiohttp.ClientSession(headers=headers) as session:
            try:
                async with session.post(
                    BASE_URL, data=payload, timeout=RESPONSE_TIMEOUT
                ) as response:
                    if response.status != 200:
                        self._reset_state_and_attributes()
                        return

                    data = await response.json()
                    self._update_state_and_attributes(data)

            except asyncio.exceptions.TimeoutError:
                _LOGGER.error("Error occurred while updating sensor.")
                return

    def _generate_payload(self, start_time):
        """Generate the payload for the API request."""
        return f"api_key={self._api_key}&monitors={self._monitor_id}&format=json&logs=0&all_time_uptime_ratio=1&custom_uptime_ratios=1&response_times=1&response_times_average=5&response_times_start_date={start_time}"

    def _generate_headers(self):
        """Generate the headers for the API request."""
        return {
            "content-type": "application/x-www-form-urlencoded",
            "cache-control": "no-cache",
        }

    def _reset_state_and_attributes(self):
        """Reset the state and attributes when the API response is not 200."""
        self._state = None
        self._extra_attributes = {
            "response_time": float(0),
            "response_avg": float(0),
            "uptime_percent_24h": float(100),
            "uptime_percent_all_time": float(100),
        }

    def _update_state_and_attributes(self, data):
        """Update the state and attributes based on the data returned by the API."""
        try:
            monitors = data.get("monitors", [])
            if len(monitors) > 0:
                response_times = monitors[0].get("response_times", [])
                if len(response_times) > 0:
                    self._state = float(response_times[0].get("value", 0))
                    self._extra_attributes = {
                        "response_time": float(response_times[0].get("value", 0)),
                        "response_avg": float(
                            monitors[0].get("average_response_time", 0)
                        ),
                        "uptime_percent_24h": float(
                            monitors[0].get("custom_uptime_ratio", 0)
                        ),
                        "uptime_percent_all_time": float(
                            monitors[0].get("all_time_uptime_ratio", 0)
                        ),
                    }
        except IndexError:
            _LOGGER.error("Error with sensor data.")
