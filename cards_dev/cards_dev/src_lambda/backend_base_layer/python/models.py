from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass, asdict
from enum import Enum
from typing import List, Union


class Phase(Enum):
    Enrollment="enrollment"
    InProgress="inprogress"
    Complete="complete"

class Distribution(Enum):
    Uniform="uniform_distribution"

class ResponseDirective(Enum):
    UpdateSession="update_session"
    UpdateRound="update_round"
    UpdateEnrollment="update_enrollment"
    ShowError="show_error"
    Pass="pass"

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
class AnswerCard(SessionDataClass):
    text: str

    @staticmethod
    def from_dynamodb_object(dynamodb_obj: dict) -> AnswerCard:
        return AnswerCard(dynamodb_obj.get("text"))

    def to_response_object(self) -> dict:
        return super().to_response_object([], {})


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

    @staticmethod
    def from_dynamodb_object(dynamodb_obj: dict) -> QuestionCard:
        return QuestionCard(dynamodb_obj.get("text"))

@dataclass
class Player(SessionDataClass):
    identity_token: str
    connection_id: str

    def to_dynamodb_object(self) -> dict:
        return super().to_dynamodb_object([], {})

    @staticmethod
    def from_dynamodb_object(dynamodb_obj: dict) -> Player:
        return Player(dynamodb_obj.get("identity_token"), dynamodb_obj.get("connection_id"))

    def to_response_object(self) -> dict:
        return super().to_response_object(["connection_id"], {})


##
## When changing property names, keep in mind the table key names (they need to be identical)
##

@dataclass
class GameRound(SessionDataClass):
    session_id: str
    round: int
    arbiter: Player
    question_card: QuestionCard
    answer_cards_suggested: List[AnswerCard]
    winner: Union[Player,  None]
    winning_answer_index: Union[int, None]

    def to_dynamodb_object(self) -> dict:
        return super().to_dynamodb_object(["question_card"], {"question_card": self.question_card.text})

    def to_archive_object(self) -> dict:
        return self.to_dict()  # TODO what should be stored in archive?

    def to_response_object(self) -> dict:
        return super().to_response_object(["question_card", "winner", "arbiter", "answer_cards_suggested"], {
            "question_card": self.question_card.text,
            "winner": self.winner.identity_token if self.winner else None,
            "arbiter": self.arbiter.identity_token,
            "answer_cards_suggested": [card.text for card in self.answer_cards_suggested]
            })


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