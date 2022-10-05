from abc import abstractclassmethod
from dataclasses import dataclass, asdict, is_dataclass
from enum import Enum
from mimetypes import init
from typing import Iterable, Mapping
import json

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
class GameSession(GameDataClass):
    class Phase(Enum):
        Enrollment="enrollment"
        Inquiry="inquiry"
        Applaud="applaud"

    session_id: str  # must be the key in dynamodb sessions table
    phase: Phase
    round: int
    coordinator_callback_url: str
    players_ids: Iterable[str]