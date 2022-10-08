from unittest.mock import MagicMock, patch
from cards_dev.src_lambda.join_session import join_session
from cards_dev.src_lambda.create_new_session import create_new_session
from backend_base_layer import ApiResponse
from .mock_fixtures import session_table, session_archive, post_to_connection


def test_simple_request(session_table, session_archive, post_to_connection) -> None:
    http_response: dict = create_new_session.lambda_handler({}, {})
    session_id = http_response.get("body").get("session_id")
    mocked_connection_id = "123456"
    join_session.lambda_handler({"body": {"session_id": session_id}, "requestContext": {"connectionId": mocked_connection_id}}, {})
    assert ApiResponse.websocket_api_manager.post_to_connection.call_args.kwargs.get("ConnectionId") == mocked_connection_id
        
