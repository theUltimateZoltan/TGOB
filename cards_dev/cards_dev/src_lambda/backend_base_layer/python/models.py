from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping
import json

@dataclass
class Player:
    pass

@dataclass
class GameSession:
    class Phase(Enum):
        Enrollment="enrollment"
        Inquiry="inquiry"
        Applaud="applaud"

    id: str
    phase: Phase
    round: int
    players_ids: Iterable[str]

    def __init__(self, id: str, phase: Phase, round: int, players_ids: Iterable[str]) -> None:
        self.id = id
        self.phase = phase
        self.round = round
        self.players_ids = players_ids

    def to_dict(self) -> dict:
        return {
            "session_id": self.id,  # must be the key in dynamodb sessions table
            "phase": self.phase.value,
            "round": self.round,
            "players_ids": list(self.players_ids)
        }