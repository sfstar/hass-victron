from collections.abc import Callable
from homeassistant.helpers.typing import StateType

from dataclasses import dataclass
from homeassistant.helpers.entity import EntityDescription

@dataclass
class VictronBaseEntityDescription(EntityDescription):
    slave: int = None 
    value_fn: Callable[[dict], StateType] = lambda data, slave, key: data["data"][str(slave) + "." + str(key)]

@dataclass 
class VictronWriteBaseEntityDescription(VictronBaseEntityDescription):
    address: int = None