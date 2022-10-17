from typing import List
import json
from cards_dev.src_lambda.choose_answer import choose_answer
from models import AnswerCard, Distribution, GameRound
from .mock_fixtures import *

def decode_callback_data(encoded_data: bytes) -> dict:
    return json.loads(encoded_data.decode("utf-8"))

def session_start_request(session: GameSession, player: Player, answer: AnswerCard) -> str:
    return json.dumps({
      "action": "answer",
      "session_id": session.session_id,
      "player_data": {"email": player.email, "username": player.name},
      "answer": answer.text
    })

def test_simple_request(session_archive, post_to_connection, dummy_session: GameSession, game_data) -> None:
    mocked_connection_id = "123445"
    GameData.append_new_round(dummy_session)
    dummy_session.phase = Phase.InProgress
    GameData.write_session(dummy_session)
    answers: List[AnswerCard] = GameData.get_answer_cards(Distribution.Uniform, 1)
    choose_answer.lambda_handler({"body":session_start_request(dummy_session, dummy_session.players[0], answers[0]), "requestContext": {"connectionId": mocked_connection_id}}, {})
