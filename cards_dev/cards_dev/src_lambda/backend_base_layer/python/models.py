from abc import abstractmethod
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Iterable, List, Set, Union


class Phase(Enum):
        Enrollment="enrollment"
        InProgress="inprogress"
        Complete="complete"

class SessionDataClass:
    def to_dict(self, fluff_attributes: List[str], extra_attributes: dict) -> dict:
        object_dict: dict = asdict(self)
        for attr in fluff_attributes:
            object_dict.pop(attr)
        object_dict.update(extra_attributes)
        return object_dict

    @abstractmethod
    def to_dynamodb_object(self, fluff_attributes: List[str], extra_attributes: dict) -> dict:
        return self.to_dict(fluff_attributes, extra_attributes)

    @abstractmethod
    def to_response_object(self, fluff_attributes: List[str], extra_attributes: dict) -> dict:
        return self.to_dict(fluff_attributes, extra_attributes)



@dataclass
class AnswerCard:
    text: str


class QuestionCard:
    defualt_blank_format: str = "{$}"

    def __init__(self, text: str, custom_blank_format: str=None) -> None:
        self.__text = text
        self.__blank_format = custom_blank_format or QuestionCard.defualt_blank_format

    @property
    def text(self):
        return self.__text.replace(self.__blank_format, "___")

    def answer_with(self, answers: List[AnswerCard]) -> str:
        filled_in_text = self.__text
        for answer in answers:
            filled_in_text = filled_in_text.replace(self.__blank_format, answer.text, count=1)
        return filled_in_text.replace(self.__blank_format, "")


@dataclass
class Player(SessionDataClass):
    identity_token: str
    connection_id: str

    def to_dynamodb_object(self) -> dict:
         return super().to_dynamodb_object([], {})


##
## When changing property names, keep in mind the table key names (they need to be identical)
##

@dataclass
class GameRound(SessionDataClass):
    session_id: str
    round: int
    winner_id: Union[str,  None]
    question_card_text: str
    answer_cards_suggested: List[str]
    winning_answer_index: int=0

    def to_dynamodb_object(self) -> dict:
         return super().to_dynamodb_object([], {})

    def to_archive_object(self) -> dict:
        return self.to_dict()  # TODO what should be stored in archive?


@dataclass
class GameSession(SessionDataClass):
    session_id: str
    phase: Phase
    coordinator_connection_id: str
    players: List[Player]
    active_round: Union[GameRound, None]
    recent_rounds: List[GameRound]

    def to_dynamodb_object(self) -> dict:
         return super().to_dynamodb_object(["active_round", "recent_rounds", "phase"], 
         {"round": 0, "phase": self.phase.value})

    def to_response_object(self) -> dict:
        return super().to_response_object(["active_round", "recent_rounds", "phase", "players"], 
        {"phase": self.phase.value, "players": [p.to_dynamodb_object() for p in self.players]})