from datetime import datetime
import logging
import json
from typing import List, Union
from mypy_boto3_dynamodb.service_resource import Table
from mypy_boto3_s3.service_resource import Bucket
from mypy_boto3_apigatewaymanagementapi import ApiGatewayManagementApiClient
from models import GameRound, GameSession, Phase, QuestionCard
import boto3
from boto3.dynamodb.conditions import Key


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class ApiRelay:
    websocket_api_manager: ApiGatewayManagementApiClient = boto3.client('apigatewaymanagementapi', endpoint_url="https://wsapi.devcards.eladlevy.click")

    @staticmethod
    def format_http_response(body: dict, status_code: int=200) -> dict:
        logger.debug(f"Formatting http response for return value: {body}")
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

    @staticmethod
    def _format_websocket_callback_content(body: dict, successful=True) -> dict:
        return {
            "success": successful,
            "body": json.dumps(body)
        }

    @staticmethod
    def post_to_connection(connection_id: str, body: dict, is_error: bool=False) -> None:
        logger.debug(f"websocket callback with return value: {body} {'marked as ERROR.' if is_error else ''}")
        if is_error and "message" not in body.keys():
            body["message"] = "An error occured."
        data: dict = ApiRelay._format_websocket_callback_content(body, successful=not is_error)
        encoded_data = json.dumps(data).encode("utf-8")
        ApiRelay.websocket_api_manager.post_to_connection(ConnectionId=connection_id ,Data=encoded_data)

    @staticmethod
    def get_event_body(event: dict) -> dict:
        return json.loads(event.get("body"))

class GameData:
##
## Before changing database related methods, consult the wiki: https://github.com/theUltimateZoltan/TGOB/wiki/Database-design.
##
    
    dynamodb = boto3.resource('dynamodb')
    s3_resource = boto3.resource('s3')
    session_table: Table = dynamodb.Table("dev_session_data")
    cards_table: Table = dynamodb.Table("dev_cards_data")
    session_archive: Bucket = s3_resource.Bucket("dev.session-archive")
    recent_rounds_buffer_size = 4

    @staticmethod
    def get_round(session_id: str ,round: int) -> Union[GameRound, None]:
        assert round > 0, "Round 0 is reserved for game metadata."
        query_result: dict = GameData.session_table.get_item(
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
        query_result: dict = GameData.session_table.query(
            KeyConditionExpression=Key("session_id").eq(session_id),
            ConsistentRead=True
        )

        if query_result.get("Count"):
            retrieved_round_objects: list = query_result.get("Items", None)
            retrieved_round_objects.sort(key=lambda round_obj: round_obj.get("round"))
            metadata_object: dict = retrieved_round_objects[0]
            return GameSession(
                session_id=metadata_object.get("session_id"),
                phase=Phase(metadata_object.get("phase")),
                coordinator_connection_id=metadata_object.get("coordinator_connection_id"),
                players=metadata_object.get("players"),
                active_round=retrieved_round_objects[-1] if len(retrieved_round_objects) > 1 else None,
                recent_rounds=retrieved_round_objects[1:-1] if len(retrieved_round_objects) > 2 else [],
            )

    @staticmethod
    def create_new_session(session_id: str) -> GameSession:
        initial_session: GameSession = GameSession(
            session_id=session_id, 
            phase=Phase.Enrollment,
            coordinator_connection_id=None,
            players=[],
            active_round=None,
            recent_rounds=[]
            )
        GameData.write_session(initial_session)
        return initial_session

    @staticmethod
    def append_new_round(session_id: str) -> GameRound:
        def pick_question_card() -> QuestionCard:
            pass  # follow the DynamoDB Categorized example here: https://bahr.dev/2021/01/07/serverless-random-records/#dynamodb-fully-random

        extended_session: GameSession = GameData.get_session(session_id)
        current_round: GameRound = extended_session.active_round
        new_round = GameRound(
            session_id=current_round.session_id,
            round=current_round.round + 1,
            winner_id= None,
            question_card_text=pick_question_card().text,
            answer_cards_suggested=[],
        )
        GameData.session_table.put_item(new_round.to_dynamodb_object())
        extended_session.recent_rounds.append(extended_session.active_round)
        extended_session.active_round = new_round
        if len(extended_session.recent_rounds) >= GameData.recent_rounds_buffer_size:
            GameData.archive_rounds(extended_session.recent_rounds)
            extended_session.recent_rounds = []

        return new_round

    @staticmethod
    def archive_rounds(session_id: str ,rounds: List[GameRound]) -> None:
        dict_representation: List[dict] = [r.to_archive_object() for r in rounds]
        GameData.session_archive.put_object(
            Key=f"{datetime.now().year}-{datetime.now().month}/{session_id}/{rounds[0].round}_to_{rounds[-1].round}.json",
            Body=json.dumps(dict_representation)
        )
        with GameData.session_table.batch_writer() as batch: 
            for r in rounds:
                batch.delete_item(
                    Key={
                        "session_id": session_id,
                        "round": r.round
                    }
                )

    @staticmethod
    def write_session(session: GameSession) -> None:
        GameData.session_table.put_item(Item=session.to_dynamodb_object())