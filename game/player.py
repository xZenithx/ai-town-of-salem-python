# Player agent logic
from ast import List
from enum import Enum
from game.llm_agent import LLMAgent
from game.parser import PlayerResponse
from game.roles.base import Role, RoleAlignment
from game.personality import pick_random_personality
from game.phase import Phase

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.engine import Game

class PlayerStatus(Enum):
    ALIVE = 1, "alive"
    DEAD = 2, "dead"

class Player:
    def __init__(self, index: int, name: str, game: 'Game', role: Role):
        self.index: int = index
        self._game: 'Game' = game
        self.name: str = name
        self.role: Role = role
        self.status: PlayerStatus = PlayerStatus.ALIVE
        self.personality_trait1: str = pick_random_personality()
        self.personality_trait2: str = pick_random_personality()

        self.system_prompt: str = (
            f"You are {self.name}, a player in Town of Salem.\n"
            "There are three phases.\n"
            "1. Day Phase: Players discuss their findings.\n"
            "2. Vote Phase: Players vote to lynch a player.\n"
            "3. Night Phase: Players perform their roles secretly.\n\n"
            f"You are a {self.role.name}.\n"
            "Nobody knows what role you are, if you expose your role, you may be targeted.\n"
            f"{self.role.get_alignment_prompt()}\n"
            f"{self.role.role_prompt}\n"
            f"Roles in play:\n"
            f"{game.roles_string}\n\n"
            f"You are emotional, {self.personality_trait1} and {self.personality_trait2}. "
            "Use your traits to decide what words you use and how you use them.\n\n"
        )

        self.day_prompt: str = (
            "DAY PHASE RULES:\n"
            "- ONLY speak using: <SPEAK>your sentence here.</SPEAK>\n"
            "- Speak in FIRST PERSON only. No third person or narration.\n"
            "- DO NOT describe your own actions or others’.\n"
            "- DO NOT invent or mention players not listed.\n"
            "- You may stay silent.\n"
            "- <SPEAK> content must be blunt.\n"
            "Examples:\n"
            "Tom is acting strange. I think he might be the mafia. <SPEAK>I don’t trust him.</SPEAK>\n"
            "Hmm, I should stay quiet for now. <SPEAK></SPEAK>\n\n"
        )


        self.history: List[str] = []

        
        self.llm_agent: LLMAgent = LLMAgent(self, system_prompt=self.system_prompt)

    def __repr__(self) -> str:
        return f"<Player {self.name} ({self.role.name})>"
    
    def on_game_start(self, game: 'Game') -> None:
        self._game = game
        self.setup_all_players_prompt()
        self.day_history: List[str] = []

    def on_day_start(self) -> None:
        self.day_history: List[str] = []

        # Check if role has a on_day_start method
        if hasattr(self.role, 'on_day_start'):
            self.role.on_day_start(self._game)

    def on_night_start(self) -> None:
        
        # Check if role has a on_night_start method
        if hasattr(self.role, 'on_night_start'):
            self.role.on_night_start(self._game)

    def setup_all_players_prompt(self) -> None:
        """Set up a prompt with all players' names and roles."""
        # print(f"{self.name} is setting up all players prompt.")
        self.all_players_prompt: str = "Players in the game:\n"
        self.all_players: dict[int, str] = {}
        for player in self._game.players:
            knows_role: bool = player == self

            # If the player is dead, they know their own role
            if player.status == PlayerStatus.DEAD:
                knows_role = True

            # If both players are Mafia, they know each other's roles
            if player.role.alignment == RoleAlignment.MAFIA and self.role.alignment == RoleAlignment.MAFIA:
                knows_role = True

            # If player is a revealed mayor, all players know their role
            from game.roles.mayor import Mayor
            if isinstance(player.role, Mayor) and getattr(player.role, 'revealed', False):
                knows_role = True
            
            self.all_players_prompt += f"{player.index} {player.name} {"Alive" if player.status == PlayerStatus.ALIVE else "Dead"} {player.role.name if knows_role else "Unknown role"}\n"
        self.all_players_prompt += "\n"

    async def chat(self) -> PlayerResponse:
        """Use the LLM agent to generate a chat response."""
        if not self.llm_agent:
            raise ValueError("LLM Agent is not initialized for this player.")
        
        prompt = ""

        # Add day prompt
        prompt += self.day_prompt

        # Add players to the prompt
        self.setup_all_players_prompt()
        prompt += self.all_players_prompt

        prompt += f"\n{self.role.day_prompt}\n" if self._game.is_day() else f"{self.role.night_prompt}\n\n"

        # turn the history into a single string prompt
        prompt += "Full day log:\n"
        if self.day_history:
            prompt += "\n".join(f"{msg}" for msg in self.day_history) + "\n\n"
        else:
            prompt += "Nothing has happened today.\n\n"


        response: PlayerResponse = await self.llm_agent.chat(prompt)
        
        return response

    async def vote(self) -> PlayerResponse:
        """Use the LLM agent to generate a vote action."""
        if not self.llm_agent:
            raise ValueError("LLM Agent is not initialized for this player.")
        
        prompt = ""

        prompt += "VOTE PHASE RULES:\n"
        prompt += "- End your message with <VOTE>player name</VOTE>\n"
        prompt += "- You may NOT vote for yourself.\n"
        prompt += "- You may ONLY vote for living players.\n"
        prompt += "- You may stay silent.\n"
        prompt += "- Put your reasoning outside of your vote tag.\n"
        prompt += "Examples:\n"
        prompt += "I think Tom is suspicious. <VOTE>Tom</VOTE>\n"
        prompt += "I have no idea who to vote for. <VOTE></VOTE>\n\n"

        # Add players to the prompt
        self.setup_all_players_prompt()
        prompt += self.all_players_prompt

        prompt += "\n\nFull day log:\n"
        if self.day_history:
            prompt += "\n".join(f"{msg}" for msg in self.day_history) + "\n\n"
        else:
            prompt += "Nothing has happened today.\n\n"

        prompt += f"Your turn to vote, {self.name}:\n"

        response: PlayerResponse = await self.llm_agent.chat(prompt)
        
        return response

    async def night(self) -> PlayerResponse:
        """Use the LLM agent to generate a night action."""
        if not self.llm_agent:
            raise ValueError("LLM Agent is not initialized for this player.")
        
        prompt = ""

        # Add night prompt
        prompt += self.role.night_prompt + "\n\n"

        # Add players to the prompt
        self.setup_all_players_prompt()
        prompt += self.all_players_prompt

        prompt += "\n\nFull day log:\n"
        if self.day_history:
            prompt += "\n".join(f"{msg}" for msg in self.day_history) + "\n\n"
        else:
            prompt += "Nothing has happened today.\n\n"

        # Get all the player's available actions
        prompt += "Available actions:\n"
        actions = self.role.actions.copy() if hasattr(self.role, 'actions') else []
        if actions and len(actions) > 0:
            for action in actions:
                if action.phase == Phase.NIGHT:
                    prompt += f"- {action.name}, Usage: {action.usage}\n"

        else:
            prompt += "No actions available.\n"
            

        prompt += f"Your turn to act, {self.name}:\n"

        response: PlayerResponse = await self.llm_agent.chat(prompt)
        
        return response

    def add_to_history(self, message: str) -> None:
        """Add a message to the player's history."""
        self.history.append(message)
        self.day_history.append(message)

    def is_alive(self) -> bool:
        """Check if the player is alive."""
        return self.status == PlayerStatus.ALIVE
    
    def set_alive(self, alive: bool) -> None:
        """Set the player as alive."""
        self.status = PlayerStatus.ALIVE if alive else PlayerStatus.DEAD