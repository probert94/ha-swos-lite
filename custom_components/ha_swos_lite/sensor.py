"""Platform for sensor integration."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_MANUFACTURER, DOMAIN
from .coordinator import MikrotikSwosLiteConfigEntry, MikrotikSwosLiteCoordinator
from .port import Port


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MikrotikSwosLiteConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Setup sensor for Mikrotik SwitchOS Lite component."""
    coordinator = config_entry.runtime_data

    device = {
        "identifiers": {(DOMAIN, coordinator.serial_num)},
        "connections": {("mac", coordinator.mac)},
        "manufacturer": ATTR_MANUFACTURER,
        "model": coordinator.model,
        "name": coordinator.identity,
        "serial_number": coordinator.serial_num,
        "sw_version": coordinator.firmware,
    }

    async_add_entities(
        [
            MikrotikSwosLitePoESensor(coordinator, device, port)
            for port in coordinator.api.ports
        ]
    )


class MikrotikSwosLitePoESensor(
    CoordinatorEntity[MikrotikSwosLiteCoordinator], SensorEntity
):
    """Representation of a Mikrotik SwitchOS Lite PoE Sensor."""

    def __init__(
        self, coordinator: MikrotikSwosLiteCoordinator, device: DeviceInfo, port: Port
    ) -> None:
        """Initialize the sensor entity."""
        super().__init__(coordinator)
        self.port = port
        self._attr_name = f"Port {(port.num + 1):02d} - {port.name} Power"
        self._attr_native_unit_of_measurement = UnitOfPower.WATT
        self._attr_suggested_display_precision = 1
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_unique_id = f"{coordinator.serial_num}_{port.num}_poe_power"
        self._attr_device_info = device

    @property
    def native_value(self) -> float:
        """Returns the current value from the API."""
        return self.coordinator.api.poe.power[self.port.num]
