from dataclasses import dataclass, field
from enum import Enum, auto


class TimMode(Enum):
    """
    Controls Tim Murphy's level of unsolicited commentary.

    VANILLA:
        Tim behaves as originally intended.

    OFF:
        Tim has been temporarily relieved of his duties.

    UNHINGED:
        Tim has abandoned reason, restraint, and all concern
        for the welfare of local Gallimimus populations.
    """
    VANILLA = auto()
    OFF = auto()
    UNHINGED = auto()

@dataclass
class QoLFlags:
    """
    Quality of life options
    """
    passive_health_regen: bool = False
    infinite_lives: bool = False
    infinite_cattle_prod: bool = False
    infinite_ammo: bool = False
    linked_gates: bool = False

@dataclass
class JPFlags:
    """
    Collection of flags/settings for JPRando
    """
    eggs_required: int = 18
    entrance_rando: bool = False
    qol_flags: QoLFlags = field(default_factory=QoLFlags)
    player_id: bytes = field(default_factory=bytes)
