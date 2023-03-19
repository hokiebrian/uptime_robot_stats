from datetime import timedelta, date
import time
import json
import aiohttp
import asyncio

from typing import Any, Dict, Optional

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import CONF_API_KEY, CONF_DEVICE_ID
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from homeassistant.components.sensor import (
    SensorStateClass,
    SensorDeviceClass
)

SCAN_INTERVAL = timedelta(seconds=150)

BASE_URL = "https://api.uptimerobot.com/v2/getMonitors"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_KEY): cv.string,
        vol.Required(CONF_DEVICE_ID): cv.string,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Uptime Robot sensor."""
    sensors = []
    for monitor in config:
        api_key = monitor[CONF_API_KEY]
        monitors = monitor[CONF_DEVICE_ID]
        sensor = UptimeRobotSensor(api_key, monitors)
        sensors.append(sensor)

    async_add_entities(sensors)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Uptime Robot sensor from a config entry."""
    api_key = config_entry.data[CONF_API_KEY]
    monitors = config_entry.data[CONF_DEVICE_ID]
    sensor = UptimeRobotSensor(api_key, monitors)
    async_add_entities([sensor])


class UptimeRobotSensor(SensorEntity):
    """Representation of an Uptime Robot sensor."""

    def __init__(self, api_key: str, monitors: str) -> None:
        """Initialize the sensor."""
        self._api_key = api_key
        self._monitors = monitors
        self._state: Optional[float] = None
        self._extra_attributes: Dict[str, Any] = {}

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Uptime Robot"

    @property
    def state(self) -> Optional[float]:
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return "ms"

    @property
    def state_class(self):
        """Return the state class of the sensor."""
        return SensorStateClass.MEASUREMENT

    @property
    def unique_id(self):
        return "bv-asdasd-123123r5"

    @property
    def extra_state_attributes(self) -> Optional[Dict[str, Any]]:
        """Return the state attributes of the sensor."""
        return self._extra_attributes

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        start_time = int(time.time()) - 1800
        payload = f"api_key={self._api_key}&monitors={self._monitors}&format=json&logs=0&all_time_uptime_ratio=1&custom_uptime_ratios=1&response_times=1&response_times_average=5&response_times_start_date={start_time}"
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "cache-control": "no-cache",
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(BASE_URL, data=payload, timeout=30) as response:
                if response.status != 200:
                    self._state = float(0)
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