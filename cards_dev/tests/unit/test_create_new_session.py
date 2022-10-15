import json
from cards_dev.src_lambda.create_new_session import create_new_session
from cards_dev.src_lambda.backend_base_layer.python.models import GameSession
from mypy_boto3_dynamodb.service_resource import Table
from backend_base_layer import GameData
from .mock_fixtures import *


def test_generated_id_unique(game_data, dummy_session: GameSession, predictable_word_generator):
    # Keep in mind the race condition not being tested here. See https://advancedweb.hu/how-to-properly-implement-unique-constraints-in-dynamodb/
    
    create_new_session.lambda_handler({}, {})

    assert GameData.get_session(dummy_session.session_id)
    assert GameData.get_session("Anotherid")  

def test_simple_session_creation(game_data):
    response = create_new_session.lambda_handler({}, {})
    session_id: str = json.loads(response.get("body")).get("session_id")
    assert GameData.get_session(session_id)
