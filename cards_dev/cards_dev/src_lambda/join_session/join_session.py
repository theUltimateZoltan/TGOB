import json
from models import GameSession, Phase
from backend_base_layer import GameData, ApiResponse

def lambda_handler(event: dict, context: dict) -> dict:
    session_to_join = json.loads(event.get("body")).get("message").get("session_id")
    connectionId = json.loads(event.get("body")).get("requestContext").get("connectionId")
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
    

    {'requestContext': 
    {'routeKey': 'join', 'messageId': 'Zs8V9e6mPHcCJIA=', 'eventType': 'MESSAGE', 'extendedRequestId': 'Zs8V9HBmPHcFwYQ=', 'requestTime': '08/Oct/2022:20:16:12 +0000', 'messageDirection': 'IN', 'stage': 'prod', 'connectedAt': 1665259785684, 'requestTimeEpoch': 1665260172351, 'identity': 
    {'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36', 'sourceIp': '147.235.204.93'}, 'requestId': 'Zs8V9HBmPHcFwYQ=', 'domainName': 'jjvxibvv07.execute-api.us-west-2.amazonaws.com', 'connectionId': 'Zs7ZidY9PHcCJIA=', 'apiId': 'jjvxibvv07'}
    , 'body': '{"action": "join", "message": {"session_id": "123"}}', 'isBase64Encoded': False}
