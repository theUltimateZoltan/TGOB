import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context) -> str:
    print("request:", event)
    return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "body": json.dumps(f"Hello, CDK!"),
            "headers": {
                "Access-Control-Allow-Headers": 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                "Access-Control-Allow-Methods": 'OPTIONS,POST,GET',
                "Access-Control-Allow-Origin": 'https://devcards.eladlevy.click'
            }
        }
