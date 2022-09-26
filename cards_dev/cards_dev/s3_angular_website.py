from aws_cdk import (
    Stack,
    aws_s3 as s3,
    RemovalPolicy,
    aws_certificatemanager as acm,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_route53 as route53,
    aws_route53_targets as targets
)
from aws_cdk.aws_s3_deployment import BucketDeployment, Source
from constructs import Construct

from cards_dev.backend import CardsBackend


class CardsFrontEnd(Stack):

    def setup_bucket_secure_access(self, s3_bucket_website :s3.Bucket) -> None:
        self.__tls_certificate_cloudfront = acm.DnsValidatedCertificate(self, "tls_certificate_cloudfront",
            domain_name=self.__backend.domain,
            hosted_zone=self.__backend.hosted_zone,
            validation=acm.CertificateValidation.from_dns(self.__backend.hosted_zone),
            region="us-east-1"  # required for cloudfront distribution
        )

        self.__frontend_cloudfront_distribution = cloudfront.Distribution(self, "frontend_cloudfront_distribution",
            default_behavior=cloudfront.BehaviorOptions(
                    origin=origins.S3Origin(s3_bucket_website),
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED  # Enable cache in production
                ),
            domain_names=[self.__backend.domain],
            certificate=self.__tls_certificate_cloudfront,
            price_class=cloudfront.PriceClass.PRICE_CLASS_100
        )

        route53.ARecord(self, f"{self.__backend.domain}_subdomain",
            zone=self.__backend.hosted_zone,
            record_name=self.__backend.domain,
            target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(self.__frontend_cloudfront_distribution))
        )

    def __create_angular_website_bucket(self) -> s3.Bucket:
        website_bucket = s3.Bucket(self, "cards_website", 
            versioned=False, 
            website_index_document="index.html", 
            public_read_access=True,
            bucket_name=self.__backend.domain,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )
        
        website_deployment = BucketDeployment(self, "website_deployment", 
            sources=[Source.asset("website/dist/cards_fe")],
            destination_bucket=website_bucket
        )

        return website_bucket

    def __init__(self, scope: Construct, construct_id: str, backend: CardsBackend, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.__backend = backend
        website_bucket = self.__create_angular_website_bucket()
        self.setup_bucket_secure_access(website_bucket)
       