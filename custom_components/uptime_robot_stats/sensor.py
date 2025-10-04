from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_MONITOR_ID, DOMAIN

if TYPE_CHECKING:
    from . import UptimeRobotDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up the Uptime Robot sensor from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    monitor_id = config_entry.data[CONF_MONITOR_ID]
    async_add_entities(
        [UptimeRobotSensor(coordinator, monitor_id)],
        True,
    )


class UptimeRobotSensor(CoordinatorEntity, SensorEntity):
    """Representation of an Uptime Robot sensor."""

    _attr_icon = "mdi:clock"
    _attr_native_unit_of_measurement = "ms"
    _attr_state_class: SensorStateClass = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: "UptimeRobotDataUpdateCoordinator",
        monitor_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._monitor_id = monitor_id
        self._attr_unique_id = f"uptime_robot_{monitor_id}"
        self._attr_name = f"Uptime Robot {monitor_id}"

    @property
    def native_value(self) -> Optional[float]:
        """Return the current response time returned by the API."""
        state = self.coordinator.data.get("state") if self.coordinator.data else None
        return state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose additional statistics from the coordinator payload."""
        if not self.coordinator.data:
            return {}
        return self.coordinator.data.get("attributes", {})
