from aws_cdk import (
    Stack,
    aws_certificatemanager as acm,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
)
from constructs import Construct

class CardsEndpoints(Stack):
    def __init__(self, scope: Construct, construct_id: str ,**kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.__base_domain: str = "eladlevy.click"
        self.__rest_api_subdomain: str = "restapi"
        self.__websocket_api_subdomain: str = "wsapi"
        self.__user_pool_subdomain: str = "auth"
        self.__environment_subdomain: str = "devcards"

        self.__setup_hosted_zone()
        self.__setup_user_pool_endpoints()


    @property
    def rest_api_domain(self) -> str:
        return ".".join([self.__rest_api_subdomain, self.domain])

    @property
    def websocket_api_domain(self) -> str:
        return ".".join([self.__websocket_api_subdomain, self.domain])

    @property
    def user_pool_domain(self) -> str:
        return ".".join([self.__user_pool_subdomain, self.domain])

    @property
    def domain(self) -> str:
        return ".".join([self.__environment_subdomain, self.__base_domain])

    @property
    def hosted_zone(self) -> route53.HostedZone:
        return self.__hosted_zone

    @property
    def user_pools_tls_certificate(self) -> acm.Certificate:
        return self.__user_pools_tls_certificate

    def __setup_hosted_zone(self) -> None:
        self.__hosted_zone = route53.HostedZone.from_lookup(self, "cards_dns", 
            domain_name=self.__base_domain
        )

    def setup_frontend_endpoints(self, s3_bucket_website :s3.Bucket) -> None:
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


    def __setup_user_pool_endpoints(self) -> None:
        self.__user_pools_tls_certificate = acm.DnsValidatedCertificate(self, "user_pool_tls_certificate",
            domain_name=f"*.{self.domain}",
            hosted_zone=self.hosted_zone,
            validation=acm.CertificateValidation.from_dns(self.hosted_zone),
            region="us-east-1"
        )
