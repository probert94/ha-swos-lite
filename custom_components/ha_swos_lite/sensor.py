"""Platform for sensor integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
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


@dataclass(frozen=True, kw_only=True)
class MikrotikSwOSLiteEntityDescription(SensorEntityDescription):
    """Describes a Mikrotik SwitchOS Lite Sensor."""

    endpoint: str
    property: str


PORT_SENSORS: tuple[MikrotikSwOSLiteEntityDescription, ...] = (
    MikrotikSwOSLiteEntityDescription(
        key="poe_power",
        translation_key="poe_power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=1,
        endpoint="poe",
        property="power",
    ),
    MikrotikSwOSLiteEntityDescription(
        key="poe_current",
        translation_key="poe_current",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE,
        suggested_display_precision=1,
        endpoint="poe",
        property="current",
    ),
    MikrotikSwOSLiteEntityDescription(
        key="poe_voltage",
        translation_key="poe_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=1,
        endpoint="poe",
        property="voltage",
    ),
)


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

    async_add_entities(
        [
            MikrotikSwosLitePortSensor(coordinator, device, port_sensor, port)
            for port_sensor in PORT_SENSORS
            for port in coordinator.api.ports
        ]
    )


class MikrotikSwosLitePortSensor(
    CoordinatorEntity[MikrotikSwosLiteCoordinator], SensorEntity
):
    """Representation of a Mikrotik SwitchOS Lite Port Sensor."""

    entity_description: MikrotikSwOSLiteEntityDescription

    def __init__(
        self,
        coordinator: MikrotikSwosLiteCoordinator,
        device: DeviceInfo,
        entity_description: MikrotikSwOSLiteEntityDescription,
        port: Port,
    ) -> None:
        """Initialize the sensor entity."""
        super().__init__(coordinator)
        self.port = port
        self.entity_description = entity_description
        self.has_entity_name = True
        self._attr_translation_placeholders = {
            "port_num": f"{(port.num + 1):02d}",
            "port_name": port.name,
        }
        self._attr_unique_id = (
            f"{coordinator.serial_num}_{port.num}_{entity_description.key}"
        )
        self._attr_device_info = device

    @property
    def native_value(self) -> float:
        """Returns the current value from the API."""
        return getattr(
            getattr(self.coordinator.api, self.entity_description.endpoint),
            self.entity_description.property,
        )[self.port.num]
