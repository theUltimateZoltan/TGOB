from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_dynamodb as dyndb,
    aws_s3 as s3
)
from constructs import Construct
from cards_dev.back_end import CardsBackend


class CardsGameData(Stack):
    def __init__(self, scope: Construct, construct_id: str, backend_stack: CardsBackend, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.__backend = backend_stack
        retain_on_deletion = False
        self.__data_resource_removal_policy: RemovalPolicy = RemovalPolicy.RETAIN if retain_on_deletion else RemovalPolicy.DESTROY
        self.__create_session_table()
        self.__create_cards_table()
        self.__create_session_archive()

    def __create_session_table(self) -> None:
        self.__session_data = dyndb.Table(self, "dev_session_data", 
            table_name="dev_session_data",
            removal_policy=self.__data_resource_removal_policy,
            partition_key= dyndb.Attribute(name="session_id", type=dyndb.AttributeType.STRING),
            sort_key=dyndb.Attribute(name="round", type=dyndb.AttributeType.NUMBER)
        )
        for function in self.__backend.lambdas:
            self.__session_data.grant_read_write_data(function)

    
    def __create_cards_table(self) -> None:
        self.__cards_data = dyndb.Table(self, "dev_cards_data", 
            table_name="dev_cards_data",
            removal_policy=self.__data_resource_removal_policy,
            partition_key=dyndb.Attribute(name="text", type=dyndb.AttributeType.STRING)
        )
        for function in self.__backend.lambdas:
            self.__session_data.grant_read_write_data(function)

        self.__cards_data.add_global_secondary_index(
            index_name="uniform_distribution_index",
            partition_key=dyndb.Attribute(name="type", type=dyndb.AttributeType.STRING),
            sort_key=dyndb.Attribute(name="uniform_distribution", type=dyndb.AttributeType.NUMBER),
        )

    def __create_session_archive(self) -> None:
        self.__session_archive = s3.Bucket(self, "dev_session_archive",
            bucket_name="dev.session-archive",
            versioned=False,
            removal_policy=self.__data_resource_removal_policy,
            auto_delete_objects=True
        )