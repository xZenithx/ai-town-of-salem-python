# parser.py
# Parser for the llm response.

import re
from typing import Callable

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.roles.base import Role

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
        self.role_specific_actions: dict['Role', list[GameAction]] = {}
        self.action_tags: dict[str, GameAction] = {}
    
    def register_action(self, action: GameAction) -> None:
        """Register a new action to be recognized by the parser."""
        self.registered_actions.append(action)
        self.action_tags[action.name] = action

    def regiser_role_action(self, action: GameAction, role: 'Role') -> None:
        """Register an action for a specific role."""
        if role not in self.role_specific_actions:
            self.role_specific_actions[role] = []
        
        self.role_specific_actions[role].append(action)
        self.action_tags[action.name] = action

    def has_tag(self, tag: str) -> bool:
        """Check if the parser has a registered action with the given tag."""
        for action in self.registered_actions:
            if action.name == tag:
                return True
        
        return False

    def parse(self, response: PlayerResponse) -> PlayerResponse:
        """Parse the response and extract the action."""
        response_text: str = response.raw
        
        # Find all tags in the response
        # Example: <KILL>PLAYER_NAME</KILL>
        tags = re.findall(r'<(\w+)>(.*?)<\/(\w+)>', response_text, re.DOTALL)
        for tag, content, _ in tags:
            if tag in self.action_tags:
                action = self.action_tags[tag]
                action._content = content.strip()

                response.actions.append(action)
        
        return response
    
    def get_phase_actions(self, phase: str) -> list[GameAction]:
        """Get all actions registered for a specific phase."""
        return [action for action in self.registered_actions if action.phase == phase]
    
    def get_phase_actions_for_role(self, phase: str, role: 'Role') -> list[GameAction]:
        """Get all actions registered for a specific phase and role."""
        actions: list[GameAction] = []

        # Check for general actions
        for action in self.get_phase_actions(phase):
            actions.append(action)

        # Check for role-specific actions
        if role in self.role_specific_actions:
            for action in self.role_specific_actions[role]:
                if action.phase == phase:
                    actions.append(action)

        return actions