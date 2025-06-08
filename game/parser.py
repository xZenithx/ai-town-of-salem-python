# parser.py
# Parser for the llm response.

import re
from typing import Callable

class GameAction:
    def __init__(self, name: str, tag: str, phase: str, callback: Callable | None = None):
        self.name: str = name
        self.tag: str = tag
        self.phase: str = phase
        self._content: str = ""
        self._priority: int = 0  # Default priority, can be set later
        # Callback args: (player, game, content, response)
        self.callback: Callable | None = callback

    def invoke(self, player, game, response) -> None:
        """Invoke the action's callback if it exists."""
        if self.callback:
            self.callback(player, game, self._content, response)
        
        self._content = ""  # Clear content after invoking

    def set_priority(self, priority: int) -> None:
        """Set the priority of the action."""
        self._priority = priority

    def __repr__(self):
        return f"<GameAction {self.name} tag={self.tag} phase={self.phase}>"

class PlayerResponse:
    def __init__(self, raw: str):
        self.raw = raw.strip()
        self.valid: bool = True
        self.actions: list[GameAction] = []
    
    def add_action(self, action: GameAction) -> None:
        """Add an action to the response."""
        self.actions.append(action)

    def __repr__(self):
        return f"<PlayerResponse valid={self.valid} actions={len(self.actions)} raw={self.raw[:20]}>"

class Parser:
    def __init__(self):
        self.registered_actions: list[GameAction] = []
        self.action_tags: dict[str, GameAction] = {}
    
    def register_action(self, action: GameAction) -> None:
        """Register a new action to be recognized by the parser."""
        self.registered_actions.append(action)
        self.action_tags[action.tag] = action

    def parse(self, response: PlayerResponse) -> PlayerResponse:
        """Parse the response and extract the action."""
        response_text: str = response.raw
        
        # Find all tags in the response
        # Example: <KILL>PLAYER_NAME</KILL>
        tags = re.findall(r'<(\w+)>(.*?)<\/(\w+)>', response_text, re.DOTALL)
        for tag, content, _ in tags:
            if tag in self.action_tags:
                action = self.action_tags[tag]
                action.content = content.strip()

                response.actions.append(action)
        
        return response