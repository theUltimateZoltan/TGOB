from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_cognito  as cognito,
    aws_certificatemanager as acm,
    Duration
)
from constructs import Construct
from cards_dev.endpoints import CardsEndpoints


class CardsUserData(Stack):
    def __init__(self, scope: Construct, construct_id: str, endpoints_stack: CardsEndpoints, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.__endpoints_stack = endpoints_stack
        retain_on_deletion = False
        self.__data_resource_removal_policy: RemovalPolicy = RemovalPolicy.RETAIN if retain_on_deletion else RemovalPolicy.DESTROY
        self.__create_user_pool()
       
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
                callback_urls=[f"https://{self.__endpoints_stack.domain}"],
                logout_urls=[f"https://{self.__endpoints_stack.domain}"]
            )
        )
        self.__create_secure_alias()
        self.__endpoints_stack.setup_user_pool_endpoints(self.__user_pool_domain)

    def __create_secure_alias(self):
        self.__user_pools_tls_certificate = acm.DnsValidatedCertificate(self, "user_pool_tls_certificate",
            domain_name=f"*.{self.__endpoints_stack.domain}",
            hosted_zone=self.__endpoints_stack.hosted_zone,
            validation=acm.CertificateValidation.from_dns(self.__endpoints_stack.hosted_zone),
            region="us-east-1"
        )

        self.__user_pool_domain = self.__user_pool.add_domain("user_pool_domain",
            custom_domain=cognito.CustomDomainOptions(
                domain_name=self.__endpoints_stack.user_pool_domain,
                certificate=self.__user_pools_tls_certificate
            )
        )