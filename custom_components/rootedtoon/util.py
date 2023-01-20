from dataclasses import dataclass

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from rootedtoonapi import Toon


def upper_first(text: str):
    text = text.strip()
    return text[0].upper() + text[1:]


@dataclass
class DataStruct:
    coordinators: dict[str, DataUpdateCoordinator]
    toon: Toon
