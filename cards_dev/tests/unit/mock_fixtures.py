import pytest
from moto import mock_dynamodb, mock_s3
from requests import patch
from backend_base_layer import GameData, ApiResponse
from unittest.mock import MagicMock
import boto3
from mypy_boto3_dynamodb.service_resource import Table
from mypy_boto3_s3.service_resource import Bucket
from mypy_boto3_apigatewaymanagementapi import ApiGatewayManagementApiClient

from models import GameSession, Phase


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
    ApiResponse.websocket_api_manager = MagicMock()
    ApiResponse.websocket_api_manager.post_to_connection = MagicMock()
    yield

@pytest.fixture
def dummy_session(session_table) -> GameSession:
    arbitrary_game_session = GameSession("Existingid", Phase.InProgress, "", ["player1", "player2"], active_round=None, recent_rounds=[])
    GameData.session_table.put_item(Item=arbitrary_game_session.to_dynamodb_object())
    yield arbitrary_game_session