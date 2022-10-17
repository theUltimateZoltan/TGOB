import json
from cards_dev.src_lambda.start_session import start_session
from .mock_fixtures import *

def decode_callback_data(encoded_data: bytes) -> dict:
    return json.loads(encoded_data.decode("utf-8"))

def session_start_request(session: GameSession, player: Player) -> str:
    return json.dumps({
      "action": "start",
      "session_id": session.session_id,
      "player_data":  {"email": player.email, "username": player.name}
    })

def test_simple_request(session_archive, post_to_connection, dummy_session: GameSession, game_data) -> None:
    mocked_connection_id = "123445"
    dummy_session.phase = Phase.Enrollment
    GameData.write_session(dummy_session)
    start_session.lambda_handler({"body":session_start_request(dummy_session, dummy_session.players[0]), "requestContext": {"connectionId": mocked_connection_id}}, {})
