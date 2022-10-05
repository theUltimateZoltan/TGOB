from dataclasses import dataclass, asdict, is_dataclass
from enum import Enum
from typing import Iterable, Union

class GameDataClass:
    def __init__(self) -> None:
        assert is_dataclass(self)

    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class Player(GameDataClass):
    name: str
    callback_url: str

@dataclass
class GameRound(GameDataClass):
    class Phase(Enum):
        Open="open"
        Closed="closed"

    phase: Phase
    session_id: str
    winner_id: Union[str,  None]
    question_card_text: str
    answer_cards_suggested: Iterable[str]
    winning_answer_index: int=0

@dataclass
class GameSession(GameDataClass):
    class Phase(Enum):
        Enrollment="enrollment"
        InProgress="inprogress"
        Finished="complete"

    session_id: str  # must be the key in dynamodb sessions table
    phase: Phase
    round: int
    coordinator_callback_url: str
    players_ids: Iterable[str]