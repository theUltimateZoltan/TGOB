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
        mock_session_table = dynamodb.create_table(
            TableName='dev_session_data',
            KeySchema=[
                {
                    'AttributeName': 'session_id',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'round',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'session_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'round',
                    'AttributeType': 'N'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        GameData.session_table = mock_session_table
        yield


@pytest.fixture
def arbitrary_game_session() -> GameSession:
    return GameSession("Existingid", Phase.InProgress, "", ["player1", "player2"], active_round=None, recent_rounds=[])

def test_generated_id_unique(session_table: Table, arbitrary_game_session: GameSession):
    # Keep in mind the race condition not being tested here. See https://advancedweb.hu/how-to-properly-implement-unique-constraints-in-dynamodb/
    with patch("cards_dev.src_lambda.create_new_session.create_new_session.randomword_generator") as randomword_generator_mock:
        number_of_words_in_sequence = 2
        randomword_generator_mock.word.side_effect = (
            [arbitrary_game_session.session_id]+
            [""] * (number_of_words_in_sequence-1)+
            ["AnotherId"]+
            [""] * (number_of_words_in_sequence-1)
        )

        GameData.session_table.put_item(Item=arbitrary_game_session.to_dynamodb_object())
        create_new_session.lambda_handler({}, {})

        assert GameData.get_session(arbitrary_game_session.session_id)
        assert GameData.get_session("Anotherid")  

def test_simple_session_creation(session_table):
    response = create_new_session.lambda_handler({}, {})
    session_id: str = json.loads(response.get("body")).get("session_id")
    assert GameData.get_session(session_id)
