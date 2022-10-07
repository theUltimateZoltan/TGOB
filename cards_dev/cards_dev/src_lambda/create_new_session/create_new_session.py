from backend_base_layer import http_response, dynamodb_key_exists
from models import GameSession
import wonderwords
from mypy_boto3_dynamodb.service_resource import Table

randomword_generator = wonderwords.RandomWord()

def __generate_new_session_id(table: Table) -> str:
    def __new_word_sequence() -> str:
        return "".join([
            str(randomword_generator.word(include_parts_of_speech=[speech_part])).capitalize() 
            for speech_part in ("adjectives", "nouns")
        ])

    attempt: str = __new_word_sequence()
    while dynamodb_key_exists(table, "session_id" ,attempt):
        attempt = __new_word_sequence()

    return attempt

def lambda_handler(event, context, session_table_mock: Table=None) -> str:
    table: Table = session_table_mock if session_table_mock else session_table
    new_session_id: str = __generate_new_session_id(table)
    new_session: GameSession = GameSession(new_session_id, GameSession.Phase.Enrollment, 0, [])
    table.put_item(Item=new_session.to_dict())
    return http_response(new_session.to_dict())