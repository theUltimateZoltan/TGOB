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

from cards_dev.back_end import CardsBackend
from cards_dev.endpoints import CardsEndpoints


class CardsFrontEnd(Stack):
   
    def __create_angular_website_bucket(self) -> s3.Bucket:
        website_bucket = s3.Bucket(self, "cards_website", 
            versioned=False, 
            website_index_document="index.html", 
            public_read_access=True,
            bucket_name=self.__endpoints_stack.domain,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )
        
        website_deployment = BucketDeployment(self, "website_deployment", 
            sources=[Source.asset("website/dist/cards_fe")],
            destination_bucket=website_bucket
        )

        return website_bucket

    def __init__(self, scope: Construct, construct_id: str, endpoints_stack: CardsEndpoints, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        website_bucket = self.__create_angular_website_bucket()
        self.__endpoints_stack = endpoints_stack
        self.__endpoints_stack.setup_bucket_secure_access(website_bucket)
       