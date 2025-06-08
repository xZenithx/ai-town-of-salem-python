# Entry point for running the simulation
from game.engine import Game

from game.roles.godfather import Godfather
from game.roles.mafioso import Mafioso
from game.roles.innocent import Innocent
from game.roles.sheriff import Sheriff
from game.roles.doctor import Doctor
import os
import glob

if __name__ == "__main__":
    # Delete the contents of prompts and response folders
    for folder in ["prompts", "response"]:
        for file in glob.glob(os.path.join(folder, "*.txt")):
            try:
                os.remove(file)
            except Exception as e:
                print(f"Failed to delete {file}: {e}")

    # Initialize the game with a specific number of players and roles
    player_count = 15
    roles = [
        Godfather(),    # 1 Mafia leader
        Mafioso(),      # 2 Regular Mafia member
        Innocent(),     # 3 Innocent townsperson
        Innocent(),     # 4 Innocent townsperson
        Innocent(),     # 5 Innocent townsperson
        Innocent(),     # 6 Innocent townsperson
        Innocent(),     # 7 Innocent townsperson
        Innocent(),     # 8 Innocent townsperson
        Innocent(),     # 9 Innocent townsperson
        Innocent(),     # 10 Innocent townsperson
        Innocent(),     # 11 Innocent townsperson
        Innocent(),     # 12 Innocent townsperson
        Innocent(),     # 13 Innocent townsperson
        Sheriff(),      # 14 Sheriff townsperson
        Doctor()        # 15 Innocent townsperson
    ]
    
    # Create a new game instance
    game = Game(player_count=player_count, roles=roles)
    
    # Start the game
    import asyncio

    try:
        asyncio.run(game.start())
    except Exception as e:
        print(f"An error occurred while starting the game: {e}")
