from models import GameSession, Phase, Player, ResponseDirective
from backend_base_layer import GameData, ApiRelay

def __register_coordinator(game_session: GameSession, connection_id: str) -> None:
    game_session.coordinator_connection_id = connection_id
    GameData.write_session(game_session)
    ApiRelay.post_to_connection(connection_id ,game_session.to_response_object(), ResponseDirective.UpdateSession)

def __enroll_player(game_session: GameSession, player: Player) -> None:
    game_session.players.append(player)
    GameData.write_session(game_session)
    ApiRelay.post_to_connection(player.connection_id ,game_session.to_response_object(), ResponseDirective.UpdateSession)
    ApiRelay.post_to_connection(game_session.coordinator_connection_id ,player.to_response_object(), ResponseDirective.UpdateEnrollment)

def __update_session_metadata(is_coordinator: bool, player_id_token: str, connection_id: str, game_session: GameSession) -> None:
    if game_session.phase == Phase.Enrollment:
        if is_coordinator:
            __register_coordinator(game_session, connection_id)
        else:
            __enroll_player(game_session, Player(player_id_token, connection_id))
    else:
        ApiRelay.post_to_connection(connection_id ,{"message": "The session is not currently open to join."}, ResponseDirective.ShowError, is_error=True)

def lambda_handler(event: dict, context: dict) -> dict:
    event_body = ApiRelay.get_event_body(event)
    session_to_join = event_body.get("session_id")
    is_coordinator = event_body.get("is_coordinator")
    player_id_token = event_body.get("player_data")
    connection_id = event.get("requestContext").get("connectionId")
    game_session: GameSession = GameData.get_session(session_id=session_to_join)
    if game_session:
        __update_session_metadata(is_coordinator, player_id_token, connection_id, game_session)
    else:
         ApiRelay.post_to_connection(connection_id ,{"message": "Session id not found."}, ResponseDirective.ShowError ,is_error=True)

    return {"statusCode": 200}


    