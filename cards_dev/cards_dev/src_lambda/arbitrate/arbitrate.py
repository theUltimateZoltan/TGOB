from models import AnswerCard, GameSession, Phase, Player, ResponseDirective
from backend_base_layer import GameData, ApiRelay, logger


def lambda_handler(event: dict, context: dict) -> dict:
    event_body: dict = ApiRelay.get_event_body(event)
    session_id: str = event_body.get("session_id")
    player_data: dict = event_body.get("player_data")
    arbitration: str = event_body.get("arbitration")
    connection_id: str = event.get("requestContext").get("connectionId")
    requesting_player: Player = Player(player_data.get("email"), player_data.get("username"), connection_id)
    logger.debug(f"Player {requesting_player.name} has chosen to arbitrate in favor of {arbitration}")
    game_session: GameSession = GameData.get_session(session_id=session_id)
    if game_session.phase != Phase.InProgress:
        ApiRelay.post_to_connection(requesting_player.connection_id, {"message": "This game is not in a state that accepts arbitration."}, 
            ResponseDirective.ShowError, is_error=True)
    elif connection_id != game_session.active_round.arbiter.connection_id:
        ApiRelay.post_to_connection(requesting_player.connection_id, {"message": "You are not this round's arbitrator."}, 
            ResponseDirective.ShowError, is_error=True)
    else:
        game_session.active_round.winning_answer_index = game_session.active_round.answer_cards_suggested.index(AnswerCard(arbitration))
        GameData.write_round(game_session.active_round)
        game_session.phase = Phase.RoundFinished
        GameData.write_session(game_session)

        response = {
            "session": game_session.to_response_object(),
            "round": game_session.active_round.to_response_object()
        }

        ApiRelay.post_to_connection(game_session.coordinator_connection_id, response, ResponseDirective.EndRound)

        for player in game_session.players:
            ApiRelay.post_to_connection(player.connection_id, response, ResponseDirective.EndRound)


    return {"statusCode": 200}


    