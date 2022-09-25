import enum
from os import path
from shutil import rmtree
import subprocess
import sys
from aws_cdk import (
    Stack,
    aws_apigateway as api,
    aws_lambda as lambda_,
    RemovalPolicy,
    aws_sns as sns,
    aws_dynamodb as dyndb,
    RemovalPolicy,
)
from constructs import Construct

from cards_dev.infrastructure import CardsInfra

class _HttpMethod(enum.Enum):
    POST="POST"
    GET="GET"

class CardsBackend(Stack):
    def __package_dependencies(self, lambda_source_path: str) -> str:
        rmtree(installation_path:=path.join(lambda_source_path, "dependencies", "python"))
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", path.join(lambda_source_path ,"requirements.txt"),
            "-t", installation_path],
            stdout=sys.stdout)
        return path.join(lambda_source_path, "dependencies")

    def __provision_backend_lambda_function(self, main_file_name: str, 
            handler_function: str="lambda_handler", runtime: lambda_.Runtime=lambda_.Runtime.PYTHON_3_9) -> lambda_.Function:
        function_path = path.join(self.__lambda_src_path, main_file_name)

        dependencies_layer = lambda_.LayerVersion(self, f"{main_file_name}_dependencies",
            removal_policy=RemovalPolicy.DESTROY,
            code=lambda_.Code.from_asset(self.__package_dependencies(function_path)),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_9]
        )

        function = lambda_.Function(self, f"{main_file_name}_lambda",
            runtime=runtime,
            handler=f"{main_file_name}.{handler_function}",
            code=lambda_.Code.from_asset(function_path),
            layers=[self.__shared_backend_layer, dependencies_layer]
        )

        self.__session_data.grant_read_write_data(function)

        return function

    def __add_resource_method(self, path: str, method: _HttpMethod, proxy_function: lambda_.Function) -> None:
        assert path in self.__resources, "First create the resource, then add a method to it."
        self.__infra.api_gateway.root.get_resource(path).add_method(method.value, api.LambdaIntegration(proxy_function))

    def __define_api(self) -> None:
        self.__resources = ["session", "inquiry", "answer"]
        
        self.__shared_backend_layer = lambda_.LayerVersion(self, "shared_backend_layer",
            removal_policy=RemovalPolicy.DESTROY,
            code=lambda_.Code.from_asset(self.__lambda_shared_layers_path),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_9]
        )

        for resource in self.__resources:
            self.__infra.api_gateway.root.add_resource(resource)
            
        self.__add_resource_method("session", _HttpMethod.POST, self.__provision_backend_lambda_function("create_new_session"))
        # self.__add_resource_method("session", _HttpMethod.GET, self.__provision_lambda_function("get_session_by_id"))

    @property
    def __lambda_shared_layers_path(self) -> str:
        return path.join(self.__lambda_src_path, "backend_base_layer")

    def __create_backend_resources(self) -> None:
        self.__event_notifier = sns.Topic(self, id="cards_event_notifier", 
            topic_name="cards_event_notifier"
        )

        self.__session_data = dyndb.Table(self, "session_data", 
            table_name="dev_session_data",
            removal_policy=RemovalPolicy.DESTROY,  # destroy data when deleting dev stack. Obviouisly not for production.
            partition_key= dyndb.Attribute(name="session_id", type=dyndb.AttributeType.STRING)
        )

    def __init__(self, scope: Construct, construct_id: str, infrastructure: CardsInfra ,**kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.__lambda_src_path = "cards_dev/src_lambda"
        self.__infra = infrastructure
        self.__create_backend_resources()
        self.__define_api()

