"""Binary sensor platform for Ryobi GDO."""
from typing import Final, cast

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_DEVICE_ID, COORDINATOR, DOMAIN, LOGGER

BINARY_SENSORS: Final[dict[str, BinarySensorEntityDescription]] = {
    "park_assist": BinarySensorEntityDescription(
        name="Park Assist",
        icon="mdi:parking",
        key="park_assist",
    ),
}


async def async_setup_entry(hass, entry, async_add_devices):
    """Define the binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]

    binary_sensors = []
    for binary_sensor in BINARY_SENSORS:
        binary_sensors.append(
            RyobiBinarySensor(BINARY_SENSORS[binary_sensor], entry, coordinator)
        )

    async_add_devices(binary_sensors, False)


class RyobiBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """integration_blueprint binary_sensor class."""

    def __init__(
        self,
        sensor_description: BinarySensorEntityDescription,
        config_entry: ConfigEntry,
        coordinator: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config = config_entry
        self.entity_description = sensor_description
        self._name = sensor_description.name
        self._key = sensor_description.key
        self.device_id = config_entry.data[CONF_DEVICE_ID]

        self._attr_name = f"ryobi_gdo_{self._name}_{self.device_id}"
        self._attr_unique_id = f"ryobi_gdo_{self._name}_{self.device_id}"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def icon(self) -> str:
        """Return the icon."""
        return self.entity_description.icon

    @property
    def device_info(self) -> DeviceInfo:
        """Return device registry information for this entity."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.device_id)},
            manufacturer="Ryobi",
            model="GDO",
            name="Ryobi Garage Door Opener",
        )

    @property
    def is_on(self) -> bool:
        """Return True if the service is on."""
        data = self.coordinator.data
        if self._key not in data:
            LOGGER.info("binary_sensor [%s] not supported.", self._key)
            return None
        LOGGER.debug("binary_sensor [%s]: %s", self._name, data[self._key])
        return cast(bool, data[self._key] == 1)
