# Mafioso role (formerly Mafia)
from game.player import Player
from .base import AttackingPower, DefensivePower, Role, _GameAction, RoleAlignment
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

        self.add_action(_GameAction("KILL", "<KILL>NAME</KILL>", Phase.NIGHT, 99))

    def kill_action(self, game: Game, player: Player, target: Player) -> None:
        """
        Perform the kill action on the target player.
        """
        player.add_to_history(f"Voted to kill {target.name} at night.")
        game.add_to_history(f"{player.name} voted to kill {target.name} at night.")

        # See if the Godfather is alive
        godfather = next((p for p in game.alive_players if p.role.name == "Godfather"), None)
        if godfather:
            godfather.add_to_history(f"{player.name} voted to kill {target.name}.")
            return
        
        # If no Godfather, Mafioso can kill
        self.attack(game, player, target)