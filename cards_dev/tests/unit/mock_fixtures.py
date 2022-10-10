import pytest
from moto import mock_dynamodb, mock_s3
from backend_base_layer import GameData, ApiRelay
from unittest.mock import MagicMock
import boto3
from mypy_boto3_dynamodb.service_resource import Table
from mypy_boto3_s3.service_resource import Bucket
from mypy_boto3_apigatewaymanagementapi import ApiGatewayManagementApiClient
from cards_dev.src_lambda.create_new_session import create_new_session
import wonderwords

from models import GameSession, Phase, Player


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
def session_archive() -> Bucket:
    with mock_s3():
        s3 = boto3.resource('s3')
        
        mock_archive_bucket = s3.create_bucket(
            Bucket="dev.session-archive", 
            CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
            )
        GameData.session_archive = mock_archive_bucket
        yield

@pytest.fixture
def post_to_connection() -> ApiGatewayManagementApiClient:
    ApiRelay.websocket_api_manager = MagicMock()
    ApiRelay.websocket_api_manager.post_to_connection = MagicMock()
    yield

@pytest.fixture
def dummy_session(session_table) -> GameSession:
    mocked_player = Player("mock_identity_token", "mock_connection_id").to_dynamodb_object()
    arbitrary_game_session = GameSession("Existingid", Phase.InProgress, "", [mocked_player], active_round=None, recent_rounds=[])
    GameData.session_table.put_item(Item=arbitrary_game_session.to_dynamodb_object())
    yield arbitrary_game_session

@pytest.fixture
def predictable_word_generator(dummy_session) -> wonderwords.RandomWord:
    number_of_words_in_sequence = 2
    original_generator = create_new_session.randomword_generator
    create_new_session.randomword_generator = MagicMock()
    create_new_session.randomword_generator.word.side_effect = (
        [dummy_session.session_id]+
        [""] * (number_of_words_in_sequence-1)+
        ["AnotherId"]+
        [""] * (number_of_words_in_sequence-1)
    )
    yield
    create_new_session.randomword_generator = original_generator
