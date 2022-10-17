from models import AnswerCard, GameSession, Phase, Player, ResponseDirective
from backend_base_layer import GameData, ApiRelay, logger


def lambda_handler(event: dict, context: dict) -> dict:
    event_body: dict = ApiRelay.get_event_body(event)
    session_id: str = event_body.get("session_id")
    player_data: dict = event_body.get("player_data")
    answer: str = event_body.get("answer")
    connection_id: str = event.get("requestContext").get("connectionId")
    requesting_player: Player = Player(player_data.get("email"), player_data.get("username"), connection_id)
    logger.debug(f"Player identity {requesting_player.name} has chosen to answer with {answer}")
    game_session: GameSession = GameData.get_session(session_id=session_id)
    if game_session.phase != Phase.InProgress:
        ApiRelay.post_to_connection(requesting_player.connection_id, {"message": "This game is not in a state that accepts answers."}, 
            ResponseDirective.ShowError, is_error=True)
    else:
        game_session.active_round.answer_cards_suggested.append(AnswerCard(answer))
        GameData.write_round(game_session.active_round)
        response = {
            "session": game_session.to_response_object(),
            "round": game_session.active_round.to_response_object()
        }
        ApiRelay.post_to_connection(game_session.coordinator_connection_id, response, ResponseDirective.UpdateRound)

        if len(game_session.active_round.answer_cards_suggested) == len(game_session.players):
            ApiRelay.post_to_connection(game_session.active_round.arbiter.connection_id, response, ResponseDirective.UpdateRound)


    return {"statusCode": 200}


    