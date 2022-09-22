import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context) -> str:
    print("request:", event)
    return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "body": json.dumps(f"Hello, CDK!")
        }
