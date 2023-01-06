from typing import Dict
from s3transfer import logger
from models import Distribution, GameRound, GameSession, Phase, Player, ResponseDirective
from backend_base_layer import GameData, ApiRelay


def lambda_handler(event: dict, context: dict) -> dict:
    print(f"event: {event}")
    print(f"context: {context}")
    pass ##  filter by TTL event, parse event and check connection status
    ## also remember to add a TTL property to table items in the correct format


    return {"statusCode": 200}


    