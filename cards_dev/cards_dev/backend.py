import enum
from os import path
from aws_cdk import (
    Stack,
    aws_apigateway as api,
    aws_lambda as lambda_,
)
from constructs import Construct

from cards_dev.infrastructure import CardsInfra

class _HttpMethod(enum.Enum):
    POST="POST"
    GET="GET"

class CardsBackend(Stack):
    def __provision_lambda_function(self, main_file_name: str, 
            handler_function: str="lambda_handler", runtime: lambda_.Runtime=lambda_.Runtime.PYTHON_3_9) -> lambda_.Function:
        return lambda_.Function(self, f"{main_file_name}_lambda",
            runtime=runtime,
            handler=f"{main_file_name}.{handler_function}",
            code=lambda_.Code.from_asset(path.join(self.__lambda_src_path, main_file_name))
        )

    def __add_resource_method(self, path: str, method: _HttpMethod, proxy_function: lambda_.Function) -> None:
        assert path in self.__resources, "First create the resource, then add a method to it."
        self.__infra.api_gateway.root.get_resource(path).add_method(method.value, api.LambdaIntegration(proxy_function))

    def __define_api(self) -> None:
        self.__resources = ["session", "inquiry", "answer"]
        
        for resource in self.__resources:
            self.__infra.api_gateway.root.add_resource(resource)
            
        self.__add_resource_method("session", _HttpMethod.POST, self.__provision_lambda_function("create_new_session"))
        # self.__add_resource_method("session", _HttpMethod.GET, self.__provision_lambda_function("get_session_by_id"))


    def __init__(self, scope: Construct, construct_id: str, infrastructure: CardsInfra ,**kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.__lambda_src_path = "cards_dev/src_lambda"
        self.__infra = infrastructure
        self.__define_api()

