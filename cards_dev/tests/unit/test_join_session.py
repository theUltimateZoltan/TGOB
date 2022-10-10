import json
from cards_dev.src_lambda.join_session import join_session
from backend_base_layer import ApiRelay
from .mock_fixtures import *

def decode_callback_data(encoded_data: bytes) -> dict:
    return json.loads(encoded_data.decode("utf-8"))

def session_join_request(session_id: GameSession) -> str:
    return json.dumps({"session_id": session_id, "is_coordinator": False, "player_data": "some_mocked_data"})

def test_simple_request(session_archive, post_to_connection, dummy_session: GameSession) -> None:
    mocked_connection_id = "123456"
    dummy_session.phase = Phase.Enrollment
    GameData.write_session(dummy_session)
    join_session.lambda_handler({"body": session_join_request(dummy_session.session_id), "requestContext": {"connectionId": mocked_connection_id}}, {})
    assert ApiRelay.websocket_api_manager.post_to_connection.call_args.kwargs.get("ConnectionId") == mocked_connection_id
    connection_ids = [player.connection_id for player in GameData.get_session(dummy_session.session_id).players]
    assert mocked_connection_id in connection_ids

        
def test_join_to_non_enrolling_fails(dummy_session: GameSession, session_archive, post_to_connection) -> None:
    mocked_connection_id = "123456"
    dummy_session.phase = Phase.InProgress
    GameData.write_session(dummy_session)
    return_value: dict = join_session.lambda_handler({"body": session_join_request(dummy_session.session_id), "requestContext": {"connectionId": mocked_connection_id}}, {})
    response_data = ApiRelay.websocket_api_manager.post_to_connection.call_args.kwargs.get("Data")
    assert decode_callback_data(response_data).get("success") == False

def test_join_to_non_existing_fails(session_table, session_archive, post_to_connection) -> None:
    mocked_connection_id = "123456"
    return_value: dict = join_session.lambda_handler({"body": session_join_request("something_that_doesnt_exist"), "requestContext": {"connectionId": mocked_connection_id}}, {})
    response_data = ApiRelay.websocket_api_manager.post_to_connection.call_args.kwargs.get("Data")
    assert decode_callback_data(response_data).get("success") == False
