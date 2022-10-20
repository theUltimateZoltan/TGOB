from typing import Dict
from s3transfer import logger
from models import Distribution, GameRound, GameSession, Phase, Player, ResponseDirective
from backend_base_layer import GameData, ApiRelay


def lambda_handler(event: dict, context: dict) -> dict:
    event_body: dict = ApiRelay.get_event_body(event)
    # session_id: str = event_body.get("session_id")
    # game_session: GameSession = GameData.get_session(session_id=session_id)
    ## ???



    return {"statusCode": 200}


    