"""Module defines entity descriptions for Victron components."""

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.typing import StateType


@dataclass
class VictronBaseEntityDescription(EntityDescription):
    """An extension of EntityDescription for Victron components."""

    @staticmethod
    def lambda_func():
        """Return an entitydescription."""
        return lambda data, slave, key: data["data"][str(slave) + "." + str(key)]

    slave: int = None
    value_fn: Callable[[dict], StateType] = lambda_func()


@dataclass
class VictronWriteBaseEntityDescription(VictronBaseEntityDescription):
    """An extension of VictronBaseEntityDescription for writeable Victron components."""

    address: int = None
