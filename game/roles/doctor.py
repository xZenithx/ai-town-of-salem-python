# Doctor role
from game.player import Player
from .base import AttackingPower, DefensivePower, Role, RoleAlignment
from game.parser import GameAction, PlayerResponse
from game.phase import Phase

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.engine import Game

class Doctor(Role):
    def __init__(self) -> None:
        super().__init__()

        self.name: str = "Doctor"
        self.alignment: RoleAlignment = RoleAlignment.TOWN
        self.attacking_power: AttackingPower = AttackingPower.NONE
        self.defensive_power: DefensivePower = DefensivePower.NONE

        self.role_prompt = (
            "You are the Doctor. Each night, you may choose one player to heal, protecting them from attacks. "
            "You cannot heal yourself two nights in a row."
        )
        self.day_prompt = (
            "It is the day phase. Blend in with the town and try to identify who needs protection."
        )
        self.night_prompt = (
            "It is the night phase. Secretly choose a player to heal."
        )

        self.last_healed = None  # Track the last player healed to prevent healing the same player consecutively
 
    def parse_heal_action(self, player: Player, game: 'Game', content: str, response: PlayerResponse) -> None:
        """
        Perform the heal action on the target player.
        """
        target = game.name_to_player(content)
        if not target:
            player.add_to_history("Invalid heal target.")
            game.add_to_history(f"{player.name} attempted to heal an invalid target: {content}.")
            return
        
        self.last_healed = target
        game.add_to_history(f"{player.name} is healing {target.name}.")
        player.add_to_history(f"Healed {target.name} at night.")

    def setup_actions(self):
        """
        Setup the actions for the Doctor role.
        """
        self.heal_action = GameAction("HEAL", "<HEAL>NAME</HEAL>", Phase.NIGHT, self.parse_heal_action)
        self.heal_action.set_priority(1)
        self.add_action(self.heal_action)

    def on_day_start(self, game: 'Game'):
        """
        Reset the heal status at the start of each day.
        """
        self.last_healed = None

    def is_protecting(self, player: Player) -> bool:
        """
        Check if the Doctor is protecting a specific player.
        """
        return self.last_healed == player