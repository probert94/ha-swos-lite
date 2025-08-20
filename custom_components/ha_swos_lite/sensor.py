"""Platform for sensor integration."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_MANUFACTURER, DOMAIN
from .coordinator import MikrotikSwosLiteConfigEntry, MikrotikSwosLiteCoordinator
from .port import Port


async def async_setup_entry(
    _: HomeAssistant,
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

    port_sensors = [
        MikrotikSwosLitePoEPowerSensor,
        MikrotikSwosLitePoECurrentSensor,
        MikrotikSwosLitePoEVoltageSensor,
    ]
    async_add_entities(
        [
            port_sensor(coordinator, device, port)
            for port_sensor in port_sensors
            for port in coordinator.api.ports
        ]
    )


class MikrotikSwosLitePoEPowerSensor(
    CoordinatorEntity[MikrotikSwosLiteCoordinator], SensorEntity
):
    """Representation of a Mikrotik SwitchOS Lite PoE Power Sensor."""

    def __init__(
        self, coordinator: MikrotikSwosLiteCoordinator, device: DeviceInfo, port: Port
    ) -> None:
        """Initialize the sensor entity."""
        super().__init__(coordinator)
        self.port = port
        self._attr_name = f"P{(port.num + 1):02d} - {port.name} Power"
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


class MikrotikSwosLitePoECurrentSensor(
    CoordinatorEntity[MikrotikSwosLiteCoordinator], SensorEntity
):
    """Representation of a Mikrotik SwitchOS Lite PoE Current Sensor."""

    def __init__(
        self, coordinator: MikrotikSwosLiteCoordinator, device: DeviceInfo, port: Port
    ) -> None:
        """Initialize the sensor entity."""
        super().__init__(coordinator)
        self.port = port
        self._attr_name = f"P{(port.num + 1):02d} - {port.name} Current"
        self._attr_native_unit_of_measurement = UnitOfElectricCurrent.MILLIAMPERE
        self._attr_suggested_display_precision = 1
        self._attr_device_class = SensorDeviceClass.CURRENT
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_unique_id = f"{coordinator.serial_num}_{port.num}_poe_current"
        self._attr_device_info = device

    @property
    def native_value(self) -> float:
        """Returns the current value from the API."""
        return self.coordinator.api.poe.current[self.port.num]


class MikrotikSwosLitePoEVoltageSensor(
    CoordinatorEntity[MikrotikSwosLiteCoordinator], SensorEntity
):
    """Representation of a Mikrotik SwitchOS Lite PoE Current Sensor."""

    def __init__(
        self, coordinator: MikrotikSwosLiteCoordinator, device: DeviceInfo, port: Port
    ) -> None:
        """Initialize the sensor entity."""
        super().__init__(coordinator)
        self.port = port
        self._attr_name = f"P{(port.num + 1):02d} - {port.name} Voltage"
        self._attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
        self._attr_suggested_display_precision = 1
        self._attr_device_class = SensorDeviceClass.VOLTAGE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_unique_id = f"{coordinator.serial_num}_{port.num}_poe_voltage"
        self._attr_device_info = device

    @property
    def native_value(self) -> float:
        """Returns the current value from the API."""
        return self.coordinator.api.poe.voltage[self.port.num]
