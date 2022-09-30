import enum
from os import path
from shutil import rmtree
import subprocess
import sys
from typing import List
from aws_cdk import (
    Stack,
    aws_apigateway as api,
    aws_lambda as lambda_,
    RemovalPolicy,
    aws_certificatemanager as acm,
    aws_route53 as route53,
    aws_route53_targets as targets,
    RemovalPolicy
)
from constructs import Construct
from cards_dev.endpoints import CardsEndpoints
from cards_dev.user_data import CardsUserData


class _HttpMethod(enum.Enum):
    POST="POST"
    GET="GET"


class CardsBackend(Stack):
    def __init__(self, scope: Construct, construct_id: str, endpoints_stack: CardsEndpoints , user_data_stack: CardsUserData, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.__lambda_src_path = "cards_dev/src_lambda"
        self.__lambdas: List[lambda_.Function] = list()
        self.__endpoints_stack = endpoints_stack
        self.__user_data_stack = user_data_stack
        self.__create_backend_resources()
        self.__define_api()

    @property
    def __lambda_shared_layers_path(self) -> str:
        return path.join(self.__lambda_src_path, "backend_base_layer")

    @property
    def lambdas(self) -> List[lambda_.Function]:
        return self.__lambdas

    def __create_backend_resources(self) -> None:
        self.__api_gateway = api.RestApi(self, "cards_api_gateway",
            default_cors_preflight_options=api.CorsOptions(
                allow_origins=api.Cors.ALL_ORIGINS,
                allow_methods=api.Cors.ALL_METHODS,
                allow_headers=api.Cors.DEFAULT_HEADERS,
                allow_credentials=True
            )
        )

        self.__api_tls_certificate = acm.DnsValidatedCertificate(self, "api_tls_certificate",
            domain_name=f"*.{self.__endpoints_stack.domain}",
            hosted_zone=self.__endpoints_stack.hosted_zone,
            validation=acm.CertificateValidation.from_dns(self.__endpoints_stack.hosted_zone),
            region="us-west-2"
        )

        self.__api_gateway.add_domain_name("rest_api_domain_name",
            domain_name=self.__endpoints_stack.api_domain,
            certificate=self.__api_tls_certificate
        )

        route53.ARecord(self, "api_domain_alias",
            zone=self.__endpoints_stack.hosted_zone,
            record_name=self.__endpoints_stack.api_domain,
            target=route53.RecordTarget.from_alias(targets.ApiGateway(self.__api_gateway))
        )

        self.__cognito_authorizer = api.CognitoUserPoolsAuthorizer(self, "user_pool_rest_api_authorizer",
            authorizer_name="user_pool_rest_api_authorizer",
            cognito_user_pools=[self.__user_data_stack.user_pool]
        )

    def __define_api(self) -> None:
        self.__resources = ["session", "inquiry", "answer"]
        
        self.__shared_backend_layer = lambda_.LayerVersion(self, "shared_backend_layer",
            removal_policy=RemovalPolicy.DESTROY,
            code=lambda_.Code.from_asset(self.__lambda_shared_layers_path),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_9]
        )

        for resource in self.__resources:
            self.__api_gateway.root.add_resource(resource)
            
        self.__add_resource_method("session", _HttpMethod.POST, self.__provision_backend_lambda_function("create_new_session"))
        # self.__add_resource_method("session", _HttpMethod.GET, self.__provision_lambda_function("get_session_by_id"))

    def __add_resource_method(self, path: str, method: _HttpMethod, proxy_function: lambda_.Function) -> None:
        assert path in self.__resources, "First create the resource, then add a method to it."
        self.__api_gateway.root.get_resource(path).add_method(method.value, api.LambdaIntegration(proxy_function), 
            authorizer=self.__cognito_authorizer, authorization_type=api.AuthorizationType.COGNITO)

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

        self.__lambdas.append(function)

        return function

