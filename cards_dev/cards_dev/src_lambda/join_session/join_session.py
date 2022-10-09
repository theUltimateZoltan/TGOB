import json
from models import GameSession, Phase
from backend_base_layer import GameData, ApiResponse

def lambda_handler(event: dict, context: dict) -> dict:
    session_to_join = json.loads(event.get("body")).get("message").get("session_id")
    connectionId = event.get("requestContext").get("connectionId")
    game_session: GameSession = GameData.get_session(session_id=session_to_join)
    if not game_session:
        ApiResponse.post_to_connection(connectionId ,{"message": "Session id not found."}, is_error=True)
    
    if game_session.phase == Phase.Enrollment:
        game_session.players_connection_ids.append(connectionId)
        GameData.write_session(game_session)
        ApiResponse.post_to_connection(connectionId ,game_session.to_response_object())
    else:
        ApiResponse.post_to_connection(connectionId ,{"message": "The session is not currently open to join."}, is_error=True)

    return {"statusCode": 200}
    