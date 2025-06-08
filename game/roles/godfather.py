# Godfather role
from .base import AttackingPower, DefensivePower, Role, RoleAlignment
from game.parser import GameAction, PlayerResponse
from game.player import Player
from game.engine import Game
from game.phase import Phase

class Godfather(Role):
    def __init__(self) -> None:
        super().__init__()
        
        self.name: str = "Godfather"
        self.alignment: RoleAlignment = RoleAlignment.MAFIA
        self.attacking_power: AttackingPower = AttackingPower.BASIC
        self.defensive_power: DefensivePower = DefensivePower.BASIC

        self.role_prompt = (
            "You are the Godfather, the leader of the Mafia. You control the Mafia's actions at night and must avoid suspicion during the day. "
            "You appear innocent to investigative roles."
        )
        self.day_prompt = (
            "It is the day phase. Blend in with the town, direct your Mafia, and avoid being voted out. "
            "You may want to defend yourself or accuse others, but do not reveal you are Mafia."
        )
        self.night_prompt = (
            "It is the night phase. Secretly choose a town member to eliminate. You have the final say on the Mafia's target."
        )

    def parse_kill_action(self, player: Player, game: 'Game', content: str, response: PlayerResponse) -> None:
        """
        Perform the kill action on the target player.
        """
        target = game.name_to_player(content)
        if not target:
            player.add_to_history("Invalid kill target.")
            game.add_to_history(f"{player.name} attempted to kill an invalid target: {content}.")
            return
        
        attacker: Player = player

        # If a mafioso exists, they will carry out the kill
        for _player in game.alive_players:
            if _player.role.name == "Mafioso":
                attacker = _player
                break

        game.add_to_history(f"Godfather {player.name} is attacking {target.name}.")
        # Perform the attack
        game.player_attack(attacker, target)

    def setup_actions(self):
        """
        Setup the actions for the Godfather role.
        """
        self.kill_action = GameAction("KILL", "<KILL>NAME</KILL>", Phase.NIGHT, self.parse_kill_action)
        self.kill_action.set_priority(100)
        self.add_action(self.kill_action)