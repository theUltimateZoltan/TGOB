import logging
import json
from typing import Any
from boto3.dynamodb import conditions
from mypy_boto3_dynamodb.service_resource import Table

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

def dynamodb_get_item_by_key(table: Table, key: str ,value: str) -> Any:
    conditional_scan = table.get_item(
        Key={key: value},
        ConsistentRead=True
    )
    return conditional_scan.get("Item")

def dynamodb_key_exists(table: Table, key: str ,value: str) -> bool:
    return bool(dynamodb_get_item_by_key(table, key, value))