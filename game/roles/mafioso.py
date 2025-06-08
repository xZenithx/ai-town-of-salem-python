# Mafioso role (formerly Mafia)
from game.player import Player
from .base import AttackingPower, DefensivePower, Role, RoleAlignment
from game.parser import GameAction, PlayerResponse
from game.engine import Game, Phase

class Mafioso(Role):
    def __init__(self) -> None:
        super().__init__()

        self.name: str = "Mafioso"
        self.alignment: RoleAlignment = RoleAlignment.MAFIA
        self.attacking_power: AttackingPower = AttackingPower.BASIC
        self.defensive_power: DefensivePower = DefensivePower.NONE

        self.role_prompt = (
            "You are the Mafioso, an enforcer for the Mafia. You carry out the Godfather's orders at night. "
            "If the Godfather dies, you become the new Godfather."
        )
        self.day_prompt = (
            "It is the day phase. Blend in with the town, cast suspicion on others, and avoid being voted out. "
            "You may want to defend yourself or accuse others, but do not reveal you are Mafia."
        )
        self.night_prompt = (
            "It is the night phase. Await the Godfather's orders to eliminate a target. "
            "If there is no Godfather, you choose the target."
        )

    def parse_kill_action(self, player: Player, game: 'Game', content: str, response: PlayerResponse) -> None:
        """
        Perform the kill action on the target player.
        """
        
        # If a Godfather exists, dont bother with the Mafioso
        for _player in game.alive_players:
            if _player.role.name == "Godfather":
                return
            
        # If no Godfather, proceed with the Mafioso's kill action
        target = game.name_to_player(content)
        if not target:
            player.add_to_history("Invalid kill target.")
            game.add_to_history(f"{player.name} attempted to kill an invalid target: {content}.")
            return
        
        attacker: Player = player

        # Perform the attack
        game.player_attack(attacker, target)

    def setup_actions(self):
        """
        Setup the actions for the Mafioso role.
        """
        self.kill_action = GameAction("VOTEKILL", "<VOTEKILL>NAME</VOTEKILL>", Phase.NIGHT, self.parse_kill_action)
        self.kill_action.set_priority(99)
        self.add_action(self.kill_action)