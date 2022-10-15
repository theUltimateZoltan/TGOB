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
from decimal import Decimal
from models import GameSession, Phase, Player


def __mock_session_table():
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
    return mock_session_table


def __mock_cards_table():
    dynamodb = boto3.resource('dynamodb')
    mock_cards_table = dynamodb.create_table(
        TableName='dev_cards_data',
        KeySchema=[
            {
                'AttributeName': 'text',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'text',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'type',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'uniform_distribution',
                'AttributeType': 'N'
            }
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'uniform_distribution_index',
                'KeySchema': [
                {
                    'AttributeName': 'type',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'uniform_distribution',
                    'KeyType': 'RANGE'
                }
                ],
                'Projection': {
                'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 1,
                    'WriteCapacityUnits': 1
                }
            }
        ],
        BillingMode='PAY_PER_REQUEST'
    )

    mock_cards_table.put_item(Item={"text": "common_qcard", "uniform_distribution": Decimal("1"), "type": "Q"})
    mock_cards_table.put_item(Item={"text": "uncommon_qcard", "uniform_distribution": Decimal("0.5"), "type": "Q"})
    mock_cards_table.put_item(Item={"text": "rare_qcard", "uniform_distribution": Decimal("0.1"), "type": "Q"})
    
    return mock_cards_table


@pytest.fixture
def game_data() -> Table:
    with mock_dynamodb():
        GameData.session_table = __mock_session_table()
        GameData.cards_table = __mock_cards_table()
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
def dummy_session(game_data) -> GameSession:
    mocked_player = Player("mock_identity_token", "mock_connection_id").to_dynamodb_object()
    arbitrary_game_session = GameSession("Existingid", Phase.InProgress, "", [mocked_player], active_round=None, recent_rounds=[])
    GameData.session_table.put_item(Item=arbitrary_game_session.to_dynamodb_object())
    yield GameData.get_session(arbitrary_game_session.session_id)

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
