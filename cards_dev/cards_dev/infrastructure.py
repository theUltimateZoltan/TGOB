from this import d
from aws_cdk import (
    Stack, 
    aws_sns as sns,
    aws_dynamodb as dyndb,
    RemovalPolicy,
    aws_apigateway as api,
    aws_route53 as route53,
    aws_s3 as s3,
    aws_certificatemanager as acm,
    aws_route53_targets as targets,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins
)
from constructs import Construct

class CardsInfra(Stack):

    def __setup_backend_infra(self) -> None:
        event_notifier_topic_name = "CardsEventNotifier"
        session_data_table_name = "SessionData"
        api_gateway_name = "CardsApiGateway"

        self.__event_notifier = sns.Topic(
            self, 
            id=event_notifier_topic_name, 
            topic_name=event_notifier_topic_name
        )

        self.__session_data = dyndb.Table(
            self, 
            session_data_table_name, 
            table_name=session_data_table_name,
            removal_policy=RemovalPolicy.DESTROY,  # destroy data when deleting dev stack. Obviouisly not for production.
            partition_key= dyndb.Attribute(name="session_id", type=dyndb.AttributeType.STRING)
        )

        self.__api_gateway = api.RestApi(self, api_gateway_name,
            default_cors_preflight_options=api.CorsOptions(
                allow_origins=api.Cors.ALL_ORIGINS,
                allow_methods=api.Cors.ALL_METHODS,
                allow_headers=api.Cors.DEFAULT_HEADERS,
                allow_credentials=True
            )
        )



    def __setup_dns(self) -> None:
        self.__hosted_zone = route53.HostedZone.from_lookup(self, "cards_dns", 
            domain_name=self.__base_domain
        )

        self.__api_tls_certificate = acm.Certificate(self, "api_domain_tls_certificate",
            domain_name=self.api_domain,
            validation=acm.CertificateValidation.from_dns(self.__hosted_zone)
        )

        self.api_gateway.add_domain_name("rest_api_domain_name",
            domain_name=self.api_domain,
            certificate=self.__api_tls_certificate
        )

        route53.ARecord(self, "api_domain_alias",
            zone=self.__hosted_zone,
            record_name=self.api_domain,
            target=route53.RecordTarget.from_alias(targets.ApiGateway(self.__api_gateway))
        )

        
    def define_website_bucket(self, s3_bucket_website :s3.Bucket):

        self.__frontend_tls_certificate = acm.DnsValidatedCertificate(self, "frontend_tls_certificate",
            domain_name=self.domain,
            hosted_zone=self.__hosted_zone,
            validation=acm.CertificateValidation.from_dns(self.__hosted_zone),
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
            certificate=self.__frontend_tls_certificate,
            price_class=cloudfront.PriceClass.PRICE_CLASS_100
        )

        route53.ARecord(self, f"{self.__environment_subdomain}_subdomain",
            zone=self.__hosted_zone,
            record_name=self.domain,
            target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(self.__frontend_cloudfront_distribution))
        )


    @property
    def api_domain(self) -> str:
        return ".".join([self.__api_subdomain, self.domain])

    @property
    def api_gateway(self) -> api.RestApi:
        return self.__api_gateway

    @property
    def domain(self) -> str:
        return ".".join([self.__environment_subdomain, self.__base_domain])

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.__base_domain: str = "eladlevy.click"
        self.__api_subdomain: str = "api"
        self.__environment_subdomain: str = "devcards"
        self.__api_gateway = None
        self.__setup_backend_infra()
        self.__setup_dns()


