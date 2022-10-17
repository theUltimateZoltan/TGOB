import enum
from os import path
import os
from shutil import rmtree
import subprocess
import sys
from typing import List
from aws_cdk import (
    Duration,
    Stack,
    aws_apigateway as api,
    aws_apigatewayv2_alpha as apiv2,
    aws_apigatewayv2_integrations_alpha as apiv2_integrations,
    aws_lambda as lambda_,
    RemovalPolicy,
    aws_certificatemanager as acm,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_iam as iam,
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

        self.__api_tls_certificate = acm.DnsValidatedCertificate(self, "api_tls_certificate",
            domain_name=f"*.{self.__endpoints_stack.domain}",
            hosted_zone=self.__endpoints_stack.hosted_zone,
            validation=acm.CertificateValidation.from_dns(self.__endpoints_stack.hosted_zone),
            region="us-west-2"
        )

        self.__rest_api_gateway = api.RestApi(self, "cards_rest_api",
            default_cors_preflight_options=api.CorsOptions(
                allow_origins=api.Cors.ALL_ORIGINS,
                allow_methods=api.Cors.ALL_METHODS,
                allow_headers=api.Cors.DEFAULT_HEADERS,
                allow_credentials=True
            )
        )

        self.__websocket_api = apiv2.WebSocketApi(self, "cards_websocket_api")
        self.__websocket_prod_stage: apiv2.WebSocketStage = apiv2.WebSocketStage(self, 'cards_websocket_api_prod_stage', 
            stage_name="prod",
            web_socket_api=self.__websocket_api,
            auto_deploy=True,
        )

        self.__setup_custom_websocket_domain()
        self.__setup_custom_rest_api_domain()

        self.__cognito_authorizer = api.CognitoUserPoolsAuthorizer(self, "user_pool_rest_api_authorizer",
            authorizer_name="user_pool_rest_api_authorizer",
            cognito_user_pools=[self.__user_data_stack.user_pool]
        )
        
        common_dependencies = self.__package_dependencies(layer_path:=path.join(self.__lambda_src_path, "backend_base_layer"),
            custom_packaging_path=path.join(self.__lambda_src_path, "common_dependencies_layer")
        )
        self.__common_dependencies_layer =  lambda_.LayerVersion(self, f"common_dependencies",
                removal_policy=RemovalPolicy.DESTROY,
                code=lambda_.Code.from_asset(common_dependencies),
                compatible_runtimes=[lambda_.Runtime.PYTHON_3_9]
            )

    def __setup_custom_websocket_domain(self) -> None:
        domainName = apiv2.DomainName(self, 'websocket_api_domain_name', 
            certificate=self.__api_tls_certificate,
            domain_name=self.__endpoints_stack.websocket_api_domain,
        )
        apiMapping = apiv2.ApiMapping(self, 'websocket_api_alias_mapping', 
            api=self.__websocket_api,
            domain_name=domainName,
            stage=self.__websocket_prod_stage
        )
        apiMapping.node.add_dependency(domainName)

        route53.ARecord(self, 'websocket_api_alias', 
            record_name= self.__endpoints_stack.websocket_api_domain,
            zone= self.__endpoints_stack.hosted_zone,
            target= route53.RecordTarget.from_alias(
                targets.ApiGatewayv2DomainProperties(
                    domainName.regional_domain_name,
                    domainName.regional_hosted_zone_id,
                ),
            ),
        )

    def __setup_custom_rest_api_domain(self) -> None:
        self.__rest_api_gateway.add_domain_name("rest_api_domain_name",
            domain_name=self.__endpoints_stack.rest_api_domain,
            certificate=self.__api_tls_certificate
        )

        route53.ARecord(self, "rest_api_domain_alias",
            zone=self.__endpoints_stack.hosted_zone,
            record_name=self.__endpoints_stack.rest_api_domain,
            target=route53.RecordTarget.from_alias(targets.ApiGateway(self.__rest_api_gateway))
        )

    def __define_api(self) -> None:
        self.__rest_resources = ["session"]
        
        self.__shared_backend_layer = lambda_.LayerVersion(self, "shared_backend_layer",
            removal_policy=RemovalPolicy.DESTROY,
            code=lambda_.Code.from_asset(self.__lambda_shared_layers_path),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_9]
        )

        for resource in self.__rest_resources:
            self.__rest_api_gateway.root.add_resource(resource)
            
        self.__add_rest_resource_method("session", _HttpMethod.POST, self.__provision_backend_lambda_function("create_new_session"))
        self.__add_websocket_route_method("$connect", self.__provision_backend_lambda_function("new_connection"))
        self.__add_websocket_route_method("join", self.__provision_backend_lambda_function("join_session"))
        self.__add_websocket_route_method("start", self.__provision_backend_lambda_function("start_round"))
        self.__add_websocket_route_method("answer", self.__provision_backend_lambda_function("choose_answer"))
        self.__add_websocket_route_method("arbitrate", self.__provision_backend_lambda_function("arbitrate"))

    def __add_rest_resource_method(self, path: str, method: _HttpMethod, proxy_function: lambda_.Function) -> None:
        assert path in self.__rest_resources, "First create the resource, then add a method to it."
        self.__rest_api_gateway.root.get_resource(path).add_method(method.value, api.LambdaIntegration(proxy_function), 
            authorizer=self.__cognito_authorizer, authorization_type=api.AuthorizationType.COGNITO)

    def __add_websocket_route_method(self, path: str, proxy_function: lambda_.Function) -> None:
        route = self.__websocket_api.add_route(
            route_key=path,
            integration=apiv2_integrations.WebSocketLambdaIntegration(f"websocket_{path}_proxy_integration", proxy_function),
           # authorizer=self.__cognito_authorizer TODO add on connect only
            )
        

    def __package_dependencies(self, lambda_source_path: str, custom_packaging_path: path=None) -> str:
        packaging_path = custom_packaging_path or path.join(lambda_source_path, "dependencies")
        rmtree(packaging_path)
        os.makedirs(installation_path:=path.join(packaging_path, "python"))
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", path.join(lambda_source_path ,"requirements.txt"),
            "-t", installation_path],
            stdout=sys.stdout)
        return path.join(installation_path, "..")

    def __provision_backend_lambda_function(self, main_file_name: str, 
            handler_function: str="lambda_handler", runtime: lambda_.Runtime=lambda_.Runtime.PYTHON_3_9) -> lambda_.Function:
        function_path = path.join(self.__lambda_src_path, main_file_name)

        if has_requirements:=os.path.exists(path.join(function_path ,"requirements.txt")):
            dependencies_layer = lambda_.LayerVersion(self, f"{main_file_name}_dependencies",
                removal_policy=RemovalPolicy.DESTROY,
                code=lambda_.Code.from_asset(self.__package_dependencies(function_path)),
                compatible_runtimes=[lambda_.Runtime.PYTHON_3_9]
            )


        function = lambda_.Function(self, f"{main_file_name}_lambda",
            runtime=runtime,
            handler=f"{main_file_name}.{handler_function}",
            code=lambda_.Code.from_asset(function_path),
            layers=[self.__common_dependencies_layer ,self.__shared_backend_layer ,dependencies_layer] if has_requirements else [self.__common_dependencies_layer, self.__shared_backend_layer],
            timeout=Duration.minutes(5),
        )
        
        function.role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonAPIGatewayInvokeFullAccess"))

        self.__lambdas.append(function)

        return function

