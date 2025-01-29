"""
This module defines entity descriptions for Victron components.

Classes:
    VictronBaseEntityDescription: Describes a base entity for Victron components.
    VictronWriteBaseEntityDescription: Describes a writable base entity for Victron components.

VictronBaseEntityDescription:
    Attributes:
        slave (int): The slave identifier.
        value_fn (Callable[[dict], StateType]): A function to extract the value from data.

    Methods:
        lambda_func(): Returns a lambda function to extract data based on slave and key.

VictronWriteBaseEntityDescription:
    Attributes:
        address (int): The address for the writable entity.
"""
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
