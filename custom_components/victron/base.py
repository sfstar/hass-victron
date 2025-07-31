"""Module defines entity descriptions for Victron components."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.typing import StateType


@dataclass(frozen=True)
class VictronBaseEntityDescription(EntityDescription):  # type: ignore[misc]
    """An extension of EntityDescription for Victron components."""

    @staticmethod
    def lambda_func() -> Any:
        """Return an entitydescription."""
        return lambda data, slave, key: data["data"][str(slave) + "." + str(key)]

    slave: int | None = None
    value_fn: Callable[[dict], StateType] = lambda_func()


@dataclass(frozen=True)
class VictronWriteBaseEntityDescription(VictronBaseEntityDescription):
    """An extension of VictronBaseEntityDescription for writeable Victron components."""

    address: int | None = None
