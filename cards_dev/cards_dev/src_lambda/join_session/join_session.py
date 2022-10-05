from backend_base_layer import http_response
from models import GameSession
import boto3
from mypy_boto3_dynamodb.service_resource import Table
import json

dynamodb = boto3.resource('dynamodb')
session_table = dynamodb.Table("dev_session_data")

def lambda_handler(event, context, session_table_mock: Table=None) -> str:
    table: Table = session_table_mock if session_table_mock else session_table
    raise NotImplementedError()