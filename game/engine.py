from ast import Dict
import string
import random
from typing import List
from game.parser import GameAction, Parser, PlayerResponse, GameAction
from game.name import pick_multiple_names
from game.player import Player, PlayerStatus
from game.roles.base import AttackingPower, DefensivePower, Role, RoleAlignment
from game.phase import Phase

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.roles.doctor import Doctor

class Game:
    def __init__(self, player_count: int = 15, roles: List[Role] = None) -> None:
        self.history: List[str] = []

        # Settings
        self.first_day_speak_rounds: int = 1
        self.day_speak_rounds: int = 3

        # Pick names for players
        self.unassigned_names: List[str] = pick_multiple_names(player_count)

        # Set up player count and player list
        self.player_count: int = player_count
        self.players: List[Player] = []
        self.alive_players: List[Player] = []
        self.dead_players: List[Player] = []

        self.parser: Parser = Parser()
        self.parser.register_action(GameAction("SPEAK", "<SPEAK>TEXT</SPEAK>", Phase.DAY, parse_speak_action))
        self.parser.register_action(GameAction("VOTE", "<VOTE>NAME</VOTE>", Phase.VOTE, parse_vote_action))

        self.roles_count: Dict[str, int] = {}
        for role in roles:
            role._game = self
            role.setup_actions()
            # Count roles
            if role.name in self.roles_count:
                self.roles_count[role.name] += 1
            else:
                self.roles_count[role.name] = 1

        self.roles_string: str = ", ".join(f"{count}x {role}" for role, count in self.roles_count.items())

        self.roles = roles.copy()  # Keep a copy of the original roles for reference
        self.unassigned_roles: List[Role] = self.roles.copy()
        # Shuffle unassigned roles to randomize player roles
        random.shuffle(self.unassigned_roles)

        self.assigned_roles: List[Role] = []
        self.phase: Phase = Phase.DAY

        for i in range(player_count):
            self.add_player(i + 1)

        random.shuffle(self.assigned_roles)

        self.day_number: int = 0

    def add_player(self, index: int) -> Player:
        # If there are no roles left to assign, return None
        if not self.unassigned_roles:
            return None
        # If there are too many players, return None
        if len(self.players) >= self.player_count:
            return None
        
        # Get a random name from the unassigned names
        name: string = self.unassigned_names.pop()
        # Get a random role from the unassigned roles
        role: Role = self.unassigned_roles.pop()
        # Move it to assigned roles
        self.assigned_roles.append(role)

        # Create a new player with the assigned role
        player: Player = Player(game=self, index=index, name=name, role=role)

        role.set_player(player)

        # Add the player to the list of players
        self.players.append(player)
        self.alive_players.append(player)

    def is_day(self) -> bool:
        return self.phase == Phase.DAY

    async def start(self) -> None:
        self.dead_to_announce: List[Player] = []
        self.votes: dict[str, int] = {}

        self.add_to_history("Game started with the following players:")
        for player in self.players:
            self.add_to_history(f"<{player.index}> {player.name} - {player.role.name}")
            player.on_game_start(game=self)

        # Main game loop
        while not self.is_game_over():
            await self.day_phase()
            if self.is_game_over():
                break
            await self.night_phase()

        self.print_winner()

    def add_to_history(self, message: str) -> None:
        """Add a message to the game history."""
        self.history.append(message)
        print(message)

    def add_to_all_history(self, message: str) -> None:
        """Add a message to the history of all players."""
        for player in self.players:
            player.add_to_history(message)

    async def simulate_chat(self) -> None:
        """Simulate a chat round where each player can speak."""
        # Get a random ordered list of alive players
        players = random.sample(self.alive_players, len(self.alive_players))

        # Use LLM-based chat for each player if available
        for player in players:
            message: PlayerResponse = await player.chat()
            message = self.parser.parse(message)

            for action in message.actions:
                action.invoke(player, self, message)

    def name_to_player(self, name: str) -> Player | None:
        """Find a player by their name."""
        for player in self.players:
            if player.name == name:
                return player
        return None

    async def day_phase(self) -> None:
        # Set the phase to day
        self.phase = Phase.DAY
        self.day_number += 1
        is_first_day: bool = self.day_number == 1

        self.add_to_all_history(f"Day {self.day_number} begins!")
        self.add_to_history(f"Day {self.day_number} begins!")

        for player in self.alive_players:
            player.on_day_start()

        if not is_first_day:
            # Reveal dead players
            dead_players = self.dead_to_announce
            if dead_players and len(dead_players) > 0:
                self.add_to_all_history("The following players have died:")
                self.add_to_history("The following players have died:")
                for player in dead_players:
                    self.add_to_all_history(f"{player.name} was a {player.role.name}.")
                    self.add_to_history(f"{player.name} was a {player.role.name}.")
                    self.on_player_killed(player)
                
                self.dead_to_announce.clear()

        chatting_rounds: int = self.first_day_speak_rounds if is_first_day else self.day_speak_rounds
        # Chat for x rounds
        for i in range(chatting_rounds):
            self.add_to_history(f"Chatting round {i + 1} of {chatting_rounds}.")
            await self.simulate_chat()

        # output the game history into a file
        with open("game_history.txt", "w", encoding="utf-8") as f:
            for entry in self.history:
                f.write(entry + "\n")

        if is_first_day:
            return

        self.add_to_all_history("Voting phase is ongoing. Players are voting.")
        self.add_to_history("Voting phase is ongoing. Players are voting.")
        await self.voting_phase()
        self.add_to_all_history("Voting phase has ended. You may no longer vote.")
        self.add_to_history("Voting phase has ended. You may no longer vote.")
        
        # output the game history into a file
        with open("game_history.txt", "w", encoding="utf-8") as f:
            for entry in self.history:
                f.write(entry + "\n")

    async def voting_phase(self) -> None:
        self.phase = Phase.VOTE
        # Simulate the voting phase where players vote to lynch someone
        await self.get_votes()

    async def get_votes(self) -> Player | None:
        self.votes.clear()  # Clear votes

        # Collect votes from all alive players
        for player in self.alive_players:
            response: PlayerResponse = await player.vote()
            response = self.parser.parse(response)

            for action in response.actions:
                if action.name == "VOTE":
                    action.invoke(player, self, response)
        
        max_votes: int = 0
        voted_out: Player | None = None
        # Determine the player with the most votes
        if self.votes:
            max_votes = max(self.votes.values())
            voted_out_name = [p for p, v in self.votes.items() if v == max_votes][0]
            voted_out = self.name_to_player(voted_out_name) if voted_out_name else None

        if voted_out:
            self.add_to_all_history(f"{voted_out.name} has been lynched!")
            self.add_to_history(f"{voted_out.name} has been lynched!")

            # Find the player who was voted out
            voted_out_player = voted_out
            self.add_to_all_history(f"{voted_out_player.name} was a {voted_out_player.role.name}.")
            self.add_to_history(f"{voted_out_player.name} was a {voted_out_player.role.name}.")
            self.on_player_killed(voted_out_player)
        else:
            self.add_to_all_history("No one was voted out this round.")
        
        self.votes.clear()  # Clear votes for the next round

    async def night_phase(self) -> None:
        # Set the phase to night
        self.phase = Phase.NIGHT
        self.add_to_all_history(f"Night {self.day_number} begins!")
        self.add_to_history(f"Night {self.day_number} begins!")

        # Collect actions from all player roles
        actions: List[tuple[Player, GameAction]] = []
        for player in self.alive_players:
            for action in player.role.actions:
                if action.phase == Phase.NIGHT:
                    # Add the action to the list
                    actions.append((player, action))
        
        # Execute actions in order of priority
        actions.sort(key=lambda x: x[1]._priority)

        has_gone: List[Player] = []
        for player, _ in actions:
            if player in has_gone:
                continue
            has_gone.append(player)

            response: PlayerResponse = await player.night()

            response = self.parser.parse(response)
            for action in response.actions:
                if action.phase == Phase.NIGHT:
                    action.invoke(player, self, response)

    def player_attack(self, attacker: Player, target: Player) -> None:
        """
        Perform an attack action from one player to another.
        This method is called when a player attacks another player.
        """
        if attacker.status != PlayerStatus.ALIVE:
            raise ValueError(f"{attacker.name} is not alive and cannot attack.")
        
        if target.status != PlayerStatus.ALIVE:
            raise ValueError(f"{target.name} is not alive and cannot be attacked.")

        attacker_power: AttackingPower = attacker.role.attacking_power
        target_power: DefensivePower = target.role.defensive_power

        if attacker_power == AttackingPower.NONE:
            raise ValueError(f"{attacker.name} has no attacking power and cannot attack.")
        
        # Convert Enum to int for comparison
        if target_power.value[0] > attacker_power.value[0]:
            attacker.add_to_history(f"Attack on {target.name} was blocked.")
            target.add_to_history(f"You were attacked but your defense blocked it.")
            self.add_to_history(f"{attacker.name}'s attack on {target.name} was blocked by {target.role.name}'s defense.")
            return
        
        # Check if the target is protected by a Doctor
        doctors = [p for p in self.alive_players if p.role.name == "Doctor"]
        if any(doctor.role.is_protecting(target) for doctor in doctors):
            attacker.add_to_history(f"Attack on {target.name} was blocked.")
            target.add_to_history(f"You were attacked but a Doctor saved you.")
            self.add_to_history(f"{attacker.name}'s attack on {target.name} was blocked by a Doctor's protection.")
            return



        # If the attack is successful, mark the target as dead
        target.add_to_history(f"You were attacked and died.")
        self.add_to_history(f"{attacker.name} attacked {target.name} with {attacker_power.name} power.")
        self.on_player_killed(target)
        self.dead_to_announce.append(target)

    def on_player_killed(self, player: Player) -> None:
        player.set_alive(False)

        if player in self.alive_players:
            self.alive_players.remove(player)

        if player not in self.dead_players:
            self.dead_players.append(player)

    def is_game_over(self) -> bool:
        # Check if all Mafia members are dead
        mafia_alive = any(p.role.alignment == RoleAlignment.MAFIA for p in self.alive_players)
        # Check if Town is wiped out.
        town_alive: bool = any(p.role.alignment == RoleAlignment.TOWN for p in self.alive_players)
        
        # Check if there are more Mafia members than Town members
        if mafia_alive and town_alive:
            mafia_count = sum(1 for p in self.alive_players if p.role.alignment == RoleAlignment.MAFIA)
            town_count = sum(1 for p in self.alive_players if p.role.alignment == RoleAlignment.TOWN)
            if mafia_count >= town_count:
                return True

        return not mafia_alive or not town_alive

    def print_winner(self) -> None:
        mafia_alive = [p for p in self.alive_players if p.role.alignment == 'mafia']
        if mafia_alive:
            self.add_to_history("Mafia wins!")
        else:
            self.add_to_history("Town wins!")

        # output the game history into a file
        with open("game_history.txt", "w", encoding="utf-8") as f:
            for entry in self.history:
                f.write(entry + "\n")


def parse_speak_action(player: Player, game: Game, content: str, response: PlayerResponse) -> None:
    """
    Parse the <SPEAK> action from the player's response.
    This function is called when a player speaks during the day phase.
    """
    
    # Content is the text inside <SPEAK> tags
    game.add_to_all_history(f"{player.name}: {content}")
    game.add_to_history(f"{player.name}: {content}")

def parse_vote_action(player: Player, game: Game, content: str, response: PlayerResponse) -> None:
    """
    Parse the <VOTE> action from the player's response.
    This function is called when a player votes during the voting phase.
    """
    
    # Target's name is content
    target_name = content.strip()
    target_player = game.name_to_player(target_name)
    if not target_player:
        game.add_to_all_history(f"{player.name} has abstained from voting.")
        game.add_to_history(f"{player.name} has abstained from voting.")
        return None
    
    if target_player.status != PlayerStatus.ALIVE:
        game.add_to_all_history(f"{player.name} has abstained from voting.")
        game.add_to_history(f"{player.name} has abstained from voting.")
        return None
    
    game.add_to_all_history(f"{player.name} voted to lynch {target_player.name}.")
    game.add_to_history(f"{player.name} voted to lynch {target_player.name}.")
    if target_player.name in game.votes:
        game.votes[target_player.name] += 1
    else:
        game.votes[target_player.name] = 1