import json
from cards_dev.src_lambda.arbitrate import arbitrate
from models import AnswerCard, Distribution, GameRound
from .mock_fixtures import *

def decode_callback_data(encoded_data: bytes) -> dict:
    return json.loads(encoded_data.decode("utf-8"))

def arbitrate_request(session: GameSession, player: Player, arbitration: AnswerCard) -> str:
    return json.dumps({
      "action": "arbitrate",
      "session_id": session.session_id,
      "player_data": {"email": player.email, "username": player.name},
      "arbitration": arbitration.text
    })

def test_simple_request(session_archive, post_to_connection, dummy_session: GameSession, game_data) -> None:
    mocked_connection_id = "123445"
    GameData.append_new_round(dummy_session)
    dummy_session.phase = Phase.InProgress
    dummy_session.active_round.answer_cards_suggested = GameData.get_answer_cards(Distribution.Uniform, 3)
    dummy_session.active_round.arbiter = dummy_session.players[0]
    GameData.write_session(dummy_session)
    arbitrate.lambda_handler({"body":arbitrate_request(dummy_session, dummy_session.players[0], dummy_session.active_round.answer_cards_suggested[0]), "requestContext": {"connectionId": mocked_connection_id}}, {})
