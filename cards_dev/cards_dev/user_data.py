from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_cognito  as cognito,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_iam as iam,
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
        self.__create_identity_pool()
    
    @property
    def user_pool(self) -> cognito.UserPool:
        return self.__user_pool

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

        self.__user_pool_client = self.__user_pool.add_client("dev_user_pool_client",
            user_pool_client_name="dev_user_pool_client",
            access_token_validity=Duration.hours(3),
            id_token_validity=Duration.hours(3),
            o_auth=cognito.OAuthSettings(
                callback_urls=[f"https://{self.__endpoints_stack.domain}"],
                logout_urls=[f"https://{self.__endpoints_stack.domain}"]
            )
        )

        self.__user_pool_domain = self.__user_pool.add_domain("user_pool_domain",
            custom_domain=cognito.CustomDomainOptions(
                domain_name=self.__endpoints_stack.user_pool_domain,
                certificate=self.__endpoints_stack.user_pools_tls_certificate
            )
        )
        
        route53.ARecord(self, "user_pool_dns_record",
            zone=self.__endpoints_stack.hosted_zone,
            record_name=self.__endpoints_stack.user_pool_domain,
            target=route53.RecordTarget.from_alias(targets.UserPoolDomainTarget(self.__user_pool_domain))
        )

    def __create_identity_pool(self) -> None:
        # implementation based on https://stackoverflow.com/questions/55784746/how-to-create-cognito-identitypool-with-cognito-userpool-as-one-of-the-authentic
        self.__identity_pool = cognito.CfnIdentityPool(self, "dev_identity_pool",
            identity_pool_name="dev_identity_pool",
            allow_unauthenticated_identities=False,
            cognito_identity_providers=[{
                    "clientId": self.__user_pool_client.user_pool_client_id,
                    "providerName": self.user_pool.user_pool_provider_name,
                }],
            )

        dummy_unauthenticated_role = iam.Role(self, "dummy_unauth_role",
            assumed_by=iam.FederatedPrincipal('cognito-identity.amazonaws.com', 
                { 
                    "StringEquals": { "cognito-identity.amazonaws.com:aud": self.__identity_pool.ref },
                    "ForAnyValue:StringLike": { "cognito-identity.amazonaws.com:amr": "authenticated" },
                }, 
                "sts:AssumeRoleWithWebIdentity")
        )

        authenticated_role = iam.Role(self, "user_pool_logged_in_role",
            assumed_by=iam.FederatedPrincipal('cognito-identity.amazonaws.com', 
                { 
                    "StringEquals": { "cognito-identity.amazonaws.com:aud": self.__identity_pool.ref },
                    "ForAnyValue:StringLike": { "cognito-identity.amazonaws.com:amr": "authenticated" },
                }, 
                "sts:AssumeRoleWithWebIdentity")
            )

        authenticated_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "sns:Subscribe",
            ],
            resources=[
                self.__endpoints_stack.progress_notification_topic.topic_arn
            ]
        ))

        identity_pool_policy = cognito.CfnIdentityPoolRoleAttachment(self, "identity_pool_role_attachment", 
            identity_pool_id=self.__identity_pool.ref,
            roles={
                "authenticated": authenticated_role.role_arn,
                "unauthenticated": dummy_unauthenticated_role.role_arn
            }
        )
        
        


        