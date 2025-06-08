from enum import Enum

class Phase(Enum):
    DAY = 1, "day"
    VOTE = 2, "vote"
    NIGHT = 3, "night"