from typing import Dict
from s3transfer import logger
from models import Distribution, GameRound, GameSession, Phase, Player, ResponseDirective
from backend_base_layer import GameData, ApiRelay


def lambda_handler(event: dict, context: dict) -> dict:
    event_body: dict = ApiRelay.get_event_body(event)
    session_id: str = event_body.get("session_id")
    player_data: Dict[str, str] = event_body.get("player_data")
    connection_id: str = event.get("requestContext").get("connectionId")
    requesting_player: Player = Player(player_data.get("email"), player_data.get("username"), connection_id)
    logger.debug(f"Player with email {requesting_player.email}... has requested to start game {session_id}")
    game_session: GameSession = GameData.get_session(session_id=session_id)
    if game_session.phase != Phase.Enrollment:
        ApiRelay.post_to_connection(requesting_player.connection_id, {"message": "This game is not in a state that allows starting."}, 
            ResponseDirective.ShowError, is_error=True)
    else:
        first_round: GameRound = GameData.append_new_round(game_session)
        game_session.phase = Phase.InProgress
        GameData.write_session(game_session)
        response = {
            "session": game_session.to_response_object(),
            "round": first_round.to_response_object()
        }
        ApiRelay.post_to_connection(game_session.coordinator_connection_id, response, ResponseDirective.UpdateRound)
        for player in game_session.players:
            ApiRelay.post_to_connection(player.connection_id, {
                "acards": [card.to_response_object() for card in GameData.get_answer_cards(Distribution.Uniform, 5)],
                **response
            }, ResponseDirective.UpdateRound)
            

    return {"statusCode": 200}


    