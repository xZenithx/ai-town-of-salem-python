from abc import ABC
from enum import Enum

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.engine import Game
    from game.player import Player
    from game.roles.doctor import Doctor
    from game.parser import GameAction

# Base Role class and interface for actions

class RoleAlignment(Enum):
    TOWN = 1, "town"
    MAFIA = 2, "mafia"
    NEUTRAL = 3, "neutral"

class AttackingPower(Enum):
    NONE = 0, "none"
    BASIC = 1, "basic"
    POWERFUL = 2, "powerful"
    UNSTOPPABLE = 3, "unstoppable"

class DefensivePower(Enum):
    NONE = 0, "none"
    BASIC = 1, "basic"
    POWERFUL = 2, "powerful"
    INVINCIBLE = 3, "invincible"

RoleAlignmentPrompts: dict[RoleAlignment, str] = {
    RoleAlignment.TOWN: "You are a member of the town, working together to eliminate threats.",
    RoleAlignment.MAFIA: "You are part of the Mafia, secretly working to eliminate the town.",
    RoleAlignment.NEUTRAL: "You have your own agenda, neither fully aligned with the town nor the Mafia."
}

def get_role_alignment_prompt(alignment: RoleAlignment) -> str:
    """Get the prompt for a specific role alignment."""
    return RoleAlignmentPrompts.get(alignment, "You have no specific alignment.")

class Role(ABC):
    def __init__(self) -> None:
        self.name: str = "Base Role"
        self.alignment: RoleAlignment = RoleAlignment.TOWN
        self.attacking_power: AttackingPower = AttackingPower.NONE
        self.defensive_power: DefensivePower = DefensivePower.NONE

        self.role_prompt: str = "You are a role in the game. Follow the rules and perform your actions accordingly."
        self.day_prompt: str = "It is the day phase. Discuss and vote to eliminate a player."
        self.night_prompt: str = "It is the night phase. Perform your actions secretly."
        
        self.night_priority: int = -1

        self.player: 'Player' = None
        self.actions: list['GameAction'] = []

        self._game: 'Game' = None

    def setup_actions(self) -> None:
        """Setup the actions for the role. Override in subclasses."""
        pass

    def set_player(self, player: 'Player') -> None:
        """Set the player associated with this role."""
        self.player = player

    def on_lynched(self) -> None:
        """Called when the player is lynched."""
        pass

    def get_alignment_prompt(self) -> str:
        """Get the prompt for the role's alignment."""
        return get_role_alignment_prompt(self.alignment)

    def add_action(self, action: 'GameAction') -> None:
        """Add an action to the role."""
        self.actions.append(action)
        self._game.parser.regiser_role_action(action, self)

    def attack(self, player: 'Player', target: 'Player') -> None:
        """Perform an attack action on the target player."""
        if self.attacking_power == AttackingPower.NONE:
            raise ValueError("This role cannot attack.")
        
        self._game.player_attack(player, target)