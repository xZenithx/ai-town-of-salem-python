# Innocent (Town) role with basic actions
from game.player import Player
from .base import AttackingPower, DefensivePower, Role, RoleAlignment

class Innocent(Role):
    def __init__(self) -> None:
        super().__init__()
        
        self.name: str = "Innocent"
        self.alignment: RoleAlignment = RoleAlignment.TOWN
        self.attacking_power: AttackingPower = AttackingPower.NONE
        self.defensive_power: DefensivePower = DefensivePower.NONE

        self.role_prompt: str = (
            "You are an innocent bystander.\n"
        )

        self.day_prompt: str = ""

        self.night_prompt: str = ""