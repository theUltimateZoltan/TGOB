from cards_dev.src_lambda.create_new_session import create_new_session
from moto import mock_dynamodb
from unittest.mock import patch
from cards_dev.src_lambda.backend_base_layer.python.models import GameSession
import boto3
from mypy_boto3_dynamodb.service_resource import Table
import pytest
from backend_base_layer import dynamodb_key_exists

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
    return GameSession("Existingid", GameSession.Phase.Inquiry, 42, ["player1", "player2"])

def test_generated_id_unique(session_table: Table, arbitrary_game_session: GameSession):
    with patch("cards_dev.src_lambda.create_new_session.create_new_session.randomword_generator") as randomword_generator_mock:
        number_of_words_in_sequence = 2
        randomword_generator_mock.word.side_effect = (
            [arbitrary_game_session.id]+
            [""] * (number_of_words_in_sequence-1)+
            ["AnotherId"]+
            [""] * (number_of_words_in_sequence-1)
        )

        session_table.put_item(Item=arbitrary_game_session.to_dict())
        create_new_session.lambda_handler({"creator_id": "tester"}, {}, session_table_mock=session_table)

        assert dynamodb_key_exists(session_table, "session_id", arbitrary_game_session.id)
        assert dynamodb_key_exists(session_table, "session_id", "Anotherid")  #Item exists, why does't it return true?

