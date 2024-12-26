from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.typing import StateType


@dataclass
class VictronBaseEntityDescription(EntityDescription):
    @staticmethod
    def lambda_func():
        return lambda data, slave, key: data["data"][str(slave) + "." + str(key)]

    slave: int = None
    value_fn: Callable[[dict], StateType] = lambda_func()


@dataclass
class VictronWriteBaseEntityDescription(VictronBaseEntityDescription):
    address: int = None
