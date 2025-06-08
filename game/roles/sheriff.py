# Sheriff role
from .base import AttackingPower, DefensivePower, Role, RoleAlignment
from game.player import Player
from game.llm_agent import LLMAgent
from game.engine import Game
import random

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
            "Select a player to investigate with <INVESTIGATE:NAME>.\n"
        )

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
            options = [p.name for p in game.alive_players if p.name != player.name]
            return random.choice(options) if options else None

    def perform_action(self, game: Game, player: Player) -> None:
        pass
