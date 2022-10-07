import logging
import json
import re
from typing import Any, Union
from mypy_boto3_dynamodb.service_resource import Table
from models import GameRound, GameSession, Phase
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def http_response(body: dict, status_code: int=200) -> dict:
    return {
            "isBase64Encoded": False,
            "statusCode": status_code,
            "body": json.dumps(body),
            "headers": {
                "Access-Control-Allow-Headers": 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                "Access-Control-Allow-Methods": 'OPTIONS,POST,GET',
                "Access-Control-Allow-Origin": 'https://devcards.eladlevy.click'
            }
        }


class SessionData:
##
## Before changing database related methods, consult the wiki: https://github.com/theUltimateZoltan/TGOB/wiki/Database-design.
##
    
    dynamodb = boto3.resource('dynamodb')
    session_table = dynamodb.Table("dev_session_data")
    initial_session = GameSession("", GameSession.Phase.Enrollment)

    @staticmethod
    def get_round(session_id: str ,round: int) -> Union[GameRound, None]:
        assert round > 0, "Round 0 is reserved for game metadata."
        query_result: dict = SessionData.session_table.get_item(
            Key={"session_id": session_id, "round": round},
            ConsistentRead=True
        )
        round_db_object: dict = query_result.get("Item", None)
        return GameRound(
            session_id=round_db_object.get("session_id"),
            round=round_db_object.get("round"),
            winner_id=round_db_object.get("winner_id"),
            question_card_text=round_db_object.get("question_card_text"),
            answer_cards_suggested=round_db_object.get("answer_cards_suggested"),
            winning_answer_index=round_db_object.get("winning_answer_index"),
        ) if round_db_object else None

    @staticmethod
    def get_session(session_id: str) -> Union[GameSession, None]:
        query_result: dict = SessionData.session_table.query(
            KeyConditionExpression='session_id = :session_id',
            ExpressionAttributeValues={
                ':session_id': {'S': session_id}
            }
        )
        if query_result.get("Count"):
            retrieved_round_objects: list = query_result.get("Items", None)
            retrieved_round_objects.sort(key=lambda round_obj: round_obj.get("round"))
            metadata_object: dict = retrieved_round_objects[0]
            return GameSession(
                session_id=metadata_object.get("session_id"),
                phase=Phase[metadata_object.get("phase")],
                coordinator_callback_url=metadata_object.get("coordinator_callback_url"),
                players_ids=metadata_object.get("players_ids"),
                active_round=retrieved_round_objects[-1] if len(retrieved_round_objects) > 1 else None,
                recent_rounds=retrieved_round_objects[1:-1] if len(retrieved_round_objects) > 2 else [],
            )

    @staticmethod
    def create_new_session(session_id: str, coordinator_callback_url) -> GameSession:
        initial_session: GameSession = GameSession(
            session_id=session_id, 
            phase=Phase.Enrollment,
            coordinator_callback_url=coordinator_callback_url,
            players_ids=[],
            active_round=None,
            recent_rounds=[]
            )
        SessionData.session_table.put_item(initial_session.to_dynamodb_object())
        return initial_session
