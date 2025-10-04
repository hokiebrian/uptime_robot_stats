"""API client for the Uptime Robot Stats integration."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict

import aiohttp
import async_timeout

from .const import BASE_URL, LOOKBACK_PERIOD, RESPONSE_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class UptimeRobotApiError(Exception):
    """Raise when the Uptime Robot API returns an error."""


class UptimeRobotClient:
    """Backward-compatible lightweight API client."""

    _HEADERS = {
        "content-type": "application/x-www-form-urlencoded",
        "cache-control": "no-cache",
    }

    def __init__(self, session: aiohttp.ClientSession, api_key: str, monitor_id: str) -> None:
        self._session = session
        self._api_key = api_key
        self._monitor_id = monitor_id

    async def async_get_monitor_stats(self) -> Dict[str, Any]:
        """Return processed monitor statistics for a configured monitor."""
        payload = self._build_payload()

        try:
            async with async_timeout.timeout(RESPONSE_TIMEOUT):
                async with self._session.post(
                    BASE_URL,
                    data=payload,
                    headers=self._HEADERS,
                ) as response:
                    if response.status != 200:
                        body = await response.text()
                        raise UptimeRobotApiError(
                            f"Unexpected response status {response.status}: {body}"
                        )

                    data = await response.json()
        except asyncio.TimeoutError as err:
            raise UptimeRobotApiError("Timeout while contacting Uptime Robot") from err
        except aiohttp.ClientError as err:
            raise UptimeRobotApiError("HTTP error while contacting Uptime Robot") from err

        if data.get("stat") != "ok":
            raise UptimeRobotApiError(
                f"API returned error status: {data.get('error', {}).get('message', 'unknown')}"
            )

        return self._parse_monitor_payload(data)

    def _build_payload(self) -> Dict[str, str]:
        """Build the payload for the API call."""
        start_time = int(time.time()) - LOOKBACK_PERIOD
        return {
            "api_key": self._api_key,
            "monitors": self._monitor_id,
            "format": "json",
            "logs": "0",
            "all_time_uptime_ratio": "1",
            "custom_uptime_ratios": "1",
            "response_times": "1",
            "response_times_average": "5",
            "response_times_start_date": str(start_time),
        }

    def _parse_monitor_payload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse API monitor data into coordinator-friendly values."""
        monitors = data.get("monitors") or []
        if not monitors:
            raise UptimeRobotApiError("Monitor response missing monitors list")

        monitor = monitors[0]
        response_times = monitor.get("response_times") or []
        latest_response_value = None
        if response_times:
            latest_response_value = response_times[0].get("value")

        if latest_response_value is not None:
            state = float(latest_response_value)
        else:
            state = None

        attributes = {
            "response_time": float(latest_response_value or 0),
            "response_avg": float(monitor.get("average_response_time", 0)),
            "uptime_percent_24h": float(monitor.get("custom_uptime_ratio", 0)),
            "uptime_percent_all_time": float(monitor.get("all_time_uptime_ratio", 0)),
        }

        return {
            "state": state,
            "attributes": attributes,
            "raw": monitor,
        }
