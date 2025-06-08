# Mayor role
from .base import AttackingPower, DefensivePower, Role, RoleAlignment
from game.player import Player
from game.llm_agent import LLMAgent
from game.engine import Game

class Mayor(Role):
    def __init__(self) -> None:
        super().__init__()
        

        self.name: str = "Mayor"
        self.alignment: RoleAlignment = RoleAlignment.TOWN
        self.attacking_power: AttackingPower = AttackingPower.NONE
        self.defensive_power: DefensivePower = DefensivePower.NONE

        self.role_prompt = (
            "You are the Mayor. You may reveal yourself to the town once per game, doubling your vote power. "
            "Use your power wisely to help the town win."
        )
        self.day_prompt = (
            "It is the day phase. You may choose to reveal yourself as Mayor, doubling your vote power. "
            "Lead the town to victory."
            "You can reveal yourself with <REVEAL> but it may turn you into a target."
        )
        self.night_prompt = (
            "It is the night phase. Stay alert and try to deduce who is trustworthy."
        )

        self.revealed = False

    def day_action(self, game: Game, player: Player, llm_agent: LLMAgent = None) -> str:
        # Mayor may choose to reveal or not
        if llm_agent:
            return player.choose_target(game, llm_agent)
        else:
            return ""

    def night_action(self, game: Game, player: Player, llm_agent: LLMAgent = None) -> str:
        # Mayor does not act at night
        return ""

    def perform_action(self, game: Game, player: Player) -> None:
        pass
