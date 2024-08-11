"""Store definitions used across multiple importers."""

from enum import StrEnum


class PlayerRole(StrEnum):
    """The available roles for a player."""

    GOALKEEPER = "G"
    DEFENDER = "D"
    MIDFIELDER = "M"
    ATTACKER = "A"
