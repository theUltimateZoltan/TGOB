from backend_base_layer import http_response, GameData
from models import GameSession
import wonderwords

randomword_generator = wonderwords.RandomWord()

def __generate_new_session_id() -> str:
    def __new_word_sequence() -> str:
        return "".join([
            str(randomword_generator.word(include_parts_of_speech=[speech_part])).capitalize() 
            for speech_part in ("adjectives", "nouns")
        ])

    attempt: str = __new_word_sequence()
    while GameData.get_session(attempt):
        attempt = __new_word_sequence()

    return attempt

def lambda_handler(event: dict, context: dict) -> str:
    new_session_id: str = __generate_new_session_id()
    new_session: GameSession = GameData.create_new_session(new_session_id)
    return http_response(new_session.to_response_object())