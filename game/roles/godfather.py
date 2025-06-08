# Godfather role
from .base import AttackingPower, DefensivePower, Role, RoleAlignment, _GameAction
from game.player import Player
from game.llm_agent import LLMAgent
from game.engine import Game
from game.phase import Phase
import random

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

        self.add_action(_GameAction("KILL", "<KILL>NAME</KILL>", Phase.NIGHT, 100))

    def day_action(self, game: Game, player: Player, llm_agent: LLMAgent = None) -> str:
        if llm_agent:
            return player.choose_target(game, llm_agent)
        else:
            options = [p.name for p in game.alive_players if p.name != player.name]
            return random.choice(options) if options else None

    def night_action(self, game: Game, player: Player, llm_agent: LLMAgent = None) -> str:
        if llm_agent:
            return player.choose_target(game, llm_agent)
        else:
            options = [p.name for p in game.alive_players if p.name != player.name and getattr(p.role, 'alignment', None) != 'mafia']
            return random.choice(options) if options else None

    def perform_action(self, game: Game, player: Player) -> None:
        pass
