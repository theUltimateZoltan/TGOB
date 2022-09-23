import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def http_response(body: dict, status_code: int=200) -> dict:
    return {
            "isBase64Encoded": False,
            "statusCode": status_code,
            "body": json.dumps(body),
            "headers": {
                "Access-Control-Allow-Headers": 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                "Access-Control-Allow-Methods": 'OPTIONS,POST,GET',
                "Access-Control-Allow-Origin": 'https://devcards.eladlevy.click'
            }
        }