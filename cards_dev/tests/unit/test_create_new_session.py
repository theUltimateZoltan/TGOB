import json
from cards_dev.src_lambda.create_new_session import create_new_session
from moto import mock_dynamodb
from unittest.mock import patch
from cards_dev.src_lambda.backend_base_layer.python.models import GameRound, GameSession, Phase
import boto3
from mypy_boto3_dynamodb.service_resource import Table
import pytest
from backend_base_layer import GameData

@pytest.fixture
def session_table() -> Table:
    with mock_dynamodb():
        dynamodb = boto3.resource('dynamodb')
        yield dynamodb.create_table(
            TableName='dev_session_data',
            KeySchema=[
                {
                    'AttributeName': 'session_id',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'session_id',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )

@pytest.fixture
def arbitrary_game_session() -> GameSession:
    return GameSession("Existingid", Phase.InProgress, "", ["player1", "player2"], active_round=None, recent_rounds=[])

def test_generated_id_unique(session_table: Table, arbitrary_game_session: GameSession):
    with patch("cards_dev.src_lambda.create_new_session.create_new_session.randomword_generator") as randomword_generator_mock:
        with patch("cards_dev.src_lambda.backend_base_layer.GameData.dynamodb") as mock_session_table:
            mock_session_table = session_table  # ??
            number_of_words_in_sequence = 2
            randomword_generator_mock.word.side_effect = (
                [arbitrary_game_session.session_id]+
                [""] * (number_of_words_in_sequence-1)+
                ["AnotherId"]+
                [""] * (number_of_words_in_sequence-1)
            )

            session_table.put_item(Item=arbitrary_game_session.to_dict())
            create_new_session.lambda_handler({"creator_id": "tester"}, {})

            assert GameData.get_session(session_table, "session_id", arbitrary_game_session.id)
            assert GameData.get_session(session_table, "session_id", "Anotherid")  

def test_simple_session_creation(session_table):
    response = create_new_session.lambda_handler({"creator_id": "some_test_user"}, {}, session_table_mock=session_table)
    session_id: str = json.loads(response.get("body")).get("session_id")
    assert GameData.get_session(session_id)


def test_requester_is_added_as_player(session_table):
    response = create_new_session.lambda_handler({"creator_id": "some_test_user"}, {}, session_table_mock=session_table)
    session_id: str = json.loads(response.get("body")).get("session_id")
    assert "some_test_user" in GameData.get_session(session_id)["players_callback"]