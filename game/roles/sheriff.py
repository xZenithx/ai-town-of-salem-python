# Sheriff role
from game.parser import GameAction, PlayerResponse
from game.phase import Phase
from .base import AttackingPower, DefensivePower, Role, RoleAlignment
from game.player import Player
from game.engine import Game

class Sheriff(Role):
    def __init__(self) -> None:
        super().__init__()
        
        self.name: str = "Sheriff"
        self.alignment: RoleAlignment = RoleAlignment.TOWN
        self.attacking_power: AttackingPower = AttackingPower.NONE
        self.defensive_power: DefensivePower = DefensivePower.NONE

        self.role_prompt = (
            "You are the Sheriff. Each night, you may investigate a player to determine if they are suspicious (Mafia) or not.\n"
            "Mafiosos will be identified as suspicious, while Innocents and godfathers will be identified as not suspicious.\n"
        )
        self.day_prompt = (
            "It is the day phase. Act with the town, share your findings carefully, and try to find the Mafia.\n"
        )
        self.night_prompt = (
            "It is the night phase. Secretly choose a player to investigate.\n"
        )

    def parse_interrogate_action(self, player: Player, game: 'Game', content: str, response: PlayerResponse) -> None:
        """
        Perform the interrogation action on the target player.
        """
        target = game.name_to_player(content)
        if not target:
            player.add_to_history("Invalid interrogation target.")
            game.add_to_history(f"{player.name} attempted to interrogate an invalid target: {content}.")
            return
        
        # Check if the target is suspicious (Mafia)
        is_suspicious = target.role.alignment == RoleAlignment.MAFIA and target.role.name != "Godfather"
        
        if is_suspicious:
            player.add_to_history(f"{target.name} is suspicious (Mafia).")
            game.add_to_history(f"{player.name} interrogated {target.name} and found them suspicious.")
        else:
            player.add_to_history(f"{target.name} is not suspicious (Innocent or Godfather).")
            game.add_to_history(f"{player.name} interrogated {target.name} and found them not suspicious.")

    def setup_actions(self):
        """
        Setup the actions for the Sheriff role.
        """
        self.interrogate_action = GameAction("INTERROGATE", "<INTERROGATE>NAME</INTERROGATE>", Phase.NIGHT, self.parse_interrogate_action)
        self.interrogate_action.set_priority(10)
        self.add_action(self.interrogate_action)