from models import GameSession, Phase
from backend_base_layer import GameData, ApiRelay

def __register_new_session(game_session: GameSession, connection_id: str, is_coordinator: bool) -> None:
    if is_coordinator:
        game_session.coordinator_connection_id = connection_id
    else:
        game_session.players.append(connection_id)
    GameData.write_session(game_session)
    ApiRelay.post_to_connection(connection_id ,game_session.to_response_object())

def lambda_handler(event: dict, context: dict) -> dict:
    event_body = ApiRelay.get_event_body(event)
    session_to_join = event_body.get("session_id")
    is_coordinator = event_body.get("is_coordinator")
    connection_id = event.get("requestContext").get("connectionId")
    game_session: GameSession = GameData.get_session(session_id=session_to_join)
    if game_session:
        if game_session.phase == Phase.Enrollment:
            __register_new_session(game_session, connection_id, is_coordinator)
        else:
            ApiRelay.post_to_connection(connection_id ,{"message": "The session is not currently open to join."}, is_error=True)
    else:
         ApiRelay.post_to_connection(connection_id ,{"message": "Session id not found."}, is_error=True)

    return {"statusCode": 200}
    