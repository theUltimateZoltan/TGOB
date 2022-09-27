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
    aws_sns as sns,
    aws_certificatemanager as acm,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    RemovalPolicy
)
from constructs import Construct

class CardsEndpoints(Stack):

    def setup_bucket_secure_access(self, s3_bucket_website :s3.Bucket) -> None:
        self.__tls_certificate_cloudfront = acm.DnsValidatedCertificate(self, "tls_certificate_cloudfront",
            domain_name=self.domain,
            hosted_zone=self.hosted_zone,
            validation=acm.CertificateValidation.from_dns(self.hosted_zone),
            region="us-east-1"  # required for cloudfront distribution
        )

        self.__frontend_cloudfront_distribution = cloudfront.Distribution(self, "frontend_cloudfront_distribution",
            default_behavior=cloudfront.BehaviorOptions(
                    origin=origins.S3Origin(s3_bucket_website),
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED  # Enable cache in production
                ),
            domain_names=[self.domain],
            certificate=self.__tls_certificate_cloudfront,
            price_class=cloudfront.PriceClass.PRICE_CLASS_100
        )

        route53.ARecord(self, f"{self.domain}_subdomain",
            zone=self.hosted_zone,
            record_name=self.domain,
            target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(self.__frontend_cloudfront_distribution))
        )


    def __create_tls_certificates(self) -> None:
        self.__tls_certificate_us_west_2 = acm.DnsValidatedCertificate(self, "tls_certificate_subdomains_us_west_2",
            domain_name=f"*.{self.domain}",
            hosted_zone=self.__hosted_zone,
            validation=acm.CertificateValidation.from_dns(self.__hosted_zone),
            region="us-west-2"
        )

        self.__api_gateway = api.RestApi(self, "cards_api_gateway",
            default_cors_preflight_options=api.CorsOptions(
                allow_origins=api.Cors.ALL_ORIGINS,
                allow_methods=api.Cors.ALL_METHODS,
                allow_headers=api.Cors.DEFAULT_HEADERS,
                allow_credentials=True
            )
        )
        self.define_rest_api(self.__api_gateway)

    def __setup_hosted_zone(self) -> None:
        self.__hosted_zone = route53.HostedZone.from_lookup(self, "cards_dns", 
            domain_name=self.__base_domain
        )

    def define_rest_api(self, api_gw: api.RestApi) -> None:
        api_gw.add_domain_name("rest_api_domain_name",
            domain_name=self.api_domain,
            certificate=self.__tls_certificate_us_west_2
        )

        route53.ARecord(self, "api_domain_alias",
            zone=self.__hosted_zone,
            record_name=self.api_domain,
            target=route53.RecordTarget.from_alias(targets.ApiGateway(api_gw))
        )

    @property
    def api_domain(self) -> str:
        return ".".join([self.__api_subdomain, self.domain])

    @property
    def user_pool_domain(self) -> str:
        return ".".join([self.__user_pool_subdomain, self.domain])

    @property
    def domain(self) -> str:
        return ".".join([self.__environment_subdomain, self.__base_domain])

    @property
    def hosted_zone(self) -> route53.HostedZone:
        return self.__hosted_zone


    def __init__(self, scope: Construct, construct_id: str ,**kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.__base_domain: str = "eladlevy.click"
        self.__api_subdomain: str = "api"
        self.__user_pool_subdomain: str = "auth"
        self.__environment_subdomain: str = "devcards"

        self.__setup_hosted_zone()
        self.__create_tls_certificates()

