"""The Mikrotik SwitchOS Lite integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import MikrotikSwosLiteConfigEntry, MikrotikSwosLiteCoordinator

_PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(
    hass: HomeAssistant, config_entry: MikrotikSwosLiteConfigEntry
) -> bool:
    """Set up Mikrotik SwitchOS Lite from a config entry."""

    coordinator = MikrotikSwosLiteCoordinator(hass, config_entry)

    await coordinator.async_config_entry_first_refresh()

    config_entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(config_entry, _PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
