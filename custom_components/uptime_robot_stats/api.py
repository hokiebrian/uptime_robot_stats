"""API client for the Uptime Robot Stats integration."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict, Optional

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

        state = self._extract_latest_response_time(response_times)
        if state is None:
            fallback_avg = self._to_float(monitor.get("average_response_time"))
            if fallback_avg is not None and fallback_avg > 0:
                state = fallback_avg

        attributes = {
            "response_time": self._first_response_value(response_times),
            "response_avg": self._to_float(monitor.get("average_response_time")),
            "uptime_percent_24h": self._to_float(monitor.get("custom_uptime_ratio")),
            "uptime_percent_all_time": self._to_float(
                monitor.get("all_time_uptime_ratio")
            ),
        }

        return {
            "state": state,
            "attributes": attributes,
            "raw": monitor,
        }

    def _extract_latest_response_time(
        self, response_times: list[Dict[str, Any]]
    ) -> Optional[float]:
        """Return the most recent non-zero response time from the API payload."""
        if not response_times:
            return None

        for point in response_times:
            value = self._to_float(point.get("value"))
            if value is not None and value > 0:
                return value

        for point in response_times:
            value = self._to_float(point.get("value"))
            if value is not None:
                return value

        return None

    def _first_response_value(
        self, response_times: list[Dict[str, Any]]
    ) -> Optional[float]:
        """Return the raw first response time value from the API, if present."""
        if not response_times:
            return None

        return self._to_float(response_times[0].get("value"))

    @staticmethod
    def _to_float(value: Any) -> Optional[float]:
        """Safely coerce API values to float."""
        if value is None or value == "":
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None
