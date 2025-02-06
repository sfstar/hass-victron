"""Module defines entity descriptions for Victron components."""

from collections.abc import Callable
from typing import Any, dataclass_transform

from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.typing import StateType


@dataclass_transform(frozen_default=True)
class VictronBaseEntityDescription(EntityDescription):  # type: ignore[misc]
    """An extension of EntityDescription for Victron components."""

    @staticmethod
    def lambda_func() -> Any:
        """Return an entitydescription."""
        return lambda data, slave, key: data["data"][str(slave) + "." + str(key)]

    slave: int | None = None
    value_fn: Callable[[dict], StateType] = lambda_func()


@dataclass_transform(frozen_default=True)
class VictronWriteBaseEntityDescription(VictronBaseEntityDescription):
    """An extension of VictronBaseEntityDescription for writeable Victron components."""

    address: float | None = None
