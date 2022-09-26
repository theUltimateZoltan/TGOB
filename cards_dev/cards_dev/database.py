from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_cognito  as cognito,
    aws_dynamodb as dyndb,
    aws_certificatemanager as acm,
    aws_route53 as route53,
    aws_route53_targets as targets,
    Duration
)
from constructs import Construct

from cards_dev.backend import CardsBackend


class CardsDataBase(Stack):

    def __create_user_pool(self) -> None:
        
        self.__user_pool = cognito.UserPool(self, "dev_user_pool",
            user_pool_name = 'dev_user_pool',
            self_sign_up_enabled = True,
            sign_in_aliases= cognito.SignInAliases(
                email=True
            ),
            auto_verify= cognito.AutoVerifiedAttrs(
                email=True
            ),
            standard_attributes= cognito.StandardAttributes(
                fullname=cognito.StandardAttribute(required=True, mutable=True),
                gender=cognito.StandardAttribute(required=True, mutable=True),
            
            ),
            custom_attributes={
                "city": cognito.StringAttribute(mutable=True),
                "age": cognito.StringAttribute(mutable=True),
                "spirit_animal": cognito.StringAttribute(mutable=True)
            },
            password_policy= cognito.PasswordPolicy(
                min_length=6,
                require_lowercase=False,
                require_digits=False,
                require_uppercase=False,
                require_symbols=False
            ),
            account_recovery= cognito.AccountRecovery.EMAIL_AND_PHONE_WITHOUT_MFA,
            removal_policy= self.__data_resource_removal_policy
        )
        
        self.__user_pool.add_client("dev_user_pool_client",
            user_pool_client_name="dev_user_pool_client",
            access_token_validity=Duration.hours(3),
            id_token_validity=Duration.hours(3),
            o_auth=cognito.OAuthSettings(
                callback_urls=[f"https://{self.__backend.domain}"],
                logout_urls=["https://{self.__backend.domain}"]
            )
        )

        self.__user_pools_tls_certificate = acm.DnsValidatedCertificate(self, "user_pool_tls_certificate",
            domain_name=f"*.{self.__backend.domain}",
            hosted_zone=self.__backend.hosted_zone,
            validation=acm.CertificateValidation.from_dns(self.__backend.hosted_zone),
            region="us-east-1"
        )

        user_pool_domain = self.__user_pool.add_domain("user_pool_domain",
            custom_domain=cognito.CustomDomainOptions(
                domain_name=self.__backend.user_pool_domain,
                certificate=self.__user_pools_tls_certificate
            )
        )

        route53.ARecord(self, "user_pool_dns_record",
            zone=self.__backend.hosted_zone,
            record_name=self.__backend.user_pool_domain,
            target=route53.RecordTarget.from_alias(targets.UserPoolDomainTarget(user_pool_domain))
        )
        

    def __create_session_table(self) -> None:
        self.__session_data = dyndb.Table(self, "session_data", 
            table_name="dev_session_data",
            removal_policy=self.__data_resource_removal_policy,
            partition_key= dyndb.Attribute(name="session_id", type=dyndb.AttributeType.STRING)
        )
        for function in self.__backend.lambdas:
            self.__session_data.grant_read_write_data(function)

    def __init__(self, scope: Construct, construct_id: str, backend: CardsBackend, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.__backend = backend
        retain_on_deletion = False
        self.__data_resource_removal_policy: RemovalPolicy = RemovalPolicy.RETAIN if retain_on_deletion else RemovalPolicy.DESTROY
        self.__create_user_pool()
        self.__create_session_table()
       