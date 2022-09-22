from logging import root
from os import path
from aws_cdk import (
    Stack,
    aws_apigateway as api,
    aws_lambda as lambda_,
)
from constructs import Construct

from cards_dev.infrastructure import CardsInfra

LAMBDA_SRC_PATH = "cards_dev/src_lambda"

class CardsBackend(Stack):

    def __get_session_by_id_lambda(self) -> lambda_.Function:
        pass

    def __create_new_session_lambda(self) -> lambda_.Function:
        return lambda_.Function(self, "new_session_lambda",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="create_new_session.lambda_handler",
            code=lambda_.Code.from_asset(path.join(LAMBDA_SRC_PATH, "create_new_session"))
        )

    def __define_api(self) -> None:
        self.__base_resources = ["session", "inquiry", "answer"]
        
        for resource in self.__base_resources:
            self.__infra.api_gateway.root.add_resource(resource)
            
        self.__infra.api_gateway.root.get_resource("session").add_method(
            "POST",
            api.LambdaIntegration(self.__create_new_session_lambda())
        )

        # self.__api_gateway.root.get_resource("session").add_method(
        #     "GET",
        #     api.LambdaIntegration(self.__get_session_by_id_lambda())
        # )

    def __init__(self, scope: Construct, construct_id: str, infrastructure: CardsInfra ,**kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.__infra = infrastructure
        self.__define_api()

