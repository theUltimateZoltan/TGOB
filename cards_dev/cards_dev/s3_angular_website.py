from aws_cdk import (
    Stack,
    aws_s3 as s3, RemovalPolicy
)
from aws_cdk.aws_s3_deployment import BucketDeployment, Source
from constructs import Construct

from cards_dev.infrastructure import CardsInfra


class CardsFrontEnd(Stack):

    def __create_angular_website_bucket(self) -> s3.Bucket:
        website_bucket = s3.Bucket(self, "cards-website", 
            versioned=False, 
            website_index_document="index.html", 
            public_read_access=True,
            bucket_name=self.__infra.domain,
            removal_policy=RemovalPolicy.RETAIN
        )
        
        website_deployment = BucketDeployment(self, "website-deployment", 
            sources=[Source.asset("website/dist/cards_fe")],
            destination_bucket=website_bucket
        )

        return website_bucket

    def __init__(self, scope: Construct, construct_id: str, infrastructure: CardsInfra, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.__infra = infrastructure
        website_bucket = self.__create_angular_website_bucket()
        self.__infra.define_website_bucket(website_bucket)
       