from dataclasses import dataclass, asdict
from enum import Enum
from typing import Iterable, List, Union


class Phase(Enum):
        Enrollment="enrollment"
        InProgress="inprogress"
        Complete="complete"

class GameDataClass:
    def to_dict(self) -> dict:
        return asdict(self)

    def to_dynamodb_object(self, fluff_attributes: List[str], extra_attributes: dict) -> dict:
        object_dict: dict = self.to_dict()
        for attr in fluff_attributes:
            object_dict.pop(attr)
        object_dict.update(extra_attributes)
        return object_dict


@dataclass
class Player(GameDataClass):
    name: str
    callback_url: str


##
## When changing property names, keep in mind the table key names (they need to be identical)
##

@dataclass
class GameRound(GameDataClass):
    session_id: str
    round: int
    winner_id: Union[str,  None]
    question_card_text: str
    answer_cards_suggested: Iterable[str]
    winning_answer_index: int=0

    def to_dynamodb_object(self) -> dict:
         return super().to_dynamodb_object([], {})


@dataclass
class GameSession(GameDataClass):
    session_id: str
    phase: Phase
    coordinator_callback_url: str
    players_ids: Iterable[str]
    active_round: Union[GameRound, None]
    recent_rounds: List[GameRound]

    def to_dynamodb_object(self) -> dict:
         return super().to_dynamodb_object(["active_round", "recent_rounds"], {"round": 0})