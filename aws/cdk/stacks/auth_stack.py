from aws_cdk import (
    Stack,
    aws_cognito as cognito,
    aws_certificatemanager as acm,
    aws_route53 as route53,
    aws_route53_targets as targets,
    Duration,
    CfnOutput
)
from constructs import Construct

class AuthStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Cognito User Pool
        self.user_pool = cognito.UserPool(
            self, "UserPool",
            user_pool_name=f"{construct_id}-user-pool",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(
                email=True,
                username=True
            ),
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(
                    required=True,
                    mutable=True
                )
            ),
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=True
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            sign_in_case_sensitive=False,
            removal_policy=RemovalPolicy.RETAIN
        )

        # Add domain prefix for Cognito hosted UI
        self.user_pool.add_domain(
            "CognitoDomain",
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix=f"{construct_id}-auth"
            )
        )

        # Create app clients
        # Lang Portal app client
        self.lang_portal_client = self.user_pool.add_client(
            "LangPortalClient",
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True,
                    implicit_code_grant=True
                ),
                scopes=[
                    cognito.OAuthScope.OPENID,
                    cognito.OAuthScope.EMAIL,
                    cognito.OAuthScope.PROFILE
                ],
                callback_urls=[
                    "http://localhost:3000/auth/callback",
                    "https://lang-portal.app-dw.net/auth/callback"
                ],
                logout_urls=[
                    "http://localhost:3000/",
                    "https://lang-portal.app-dw.net/"
                ]
            ),
            access_token_validity=Duration.hours(1),
            id_token_validity=Duration.hours(1),
            refresh_token_validity=Duration.days(30),
            prevent_user_existence_errors=True
        )

        # Haiku Generator app client
        self.haiku_client = self.user_pool.add_client(
            "HaikuClient",
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True,
                    implicit_code_grant=True
                ),
                scopes=[
                    cognito.OAuthScope.OPENID,
                    cognito.OAuthScope.EMAIL,
                    cognito.OAuthScope.PROFILE
                ],
                callback_urls=[
                    "http://localhost:3000/auth/callback",
                    "https://haiku.app-dw.net/auth/callback"
                ],
                logout_urls=[
                    "http://localhost:3000/",
                    "https://haiku.app-dw.net/"
                ]
            ),
            access_token_validity=Duration.hours(1),
            id_token_validity=Duration.hours(1),
            refresh_token_validity=Duration.days(30),
            prevent_user_existence_errors=True
        )

        # Vocab Generator app client
        self.vocab_client = self.user_pool.add_client(
            "VocabClient",
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True,
                    implicit_code_grant=True
                ),
                scopes=[
                    cognito.OAuthScope.OPENID,
                    cognito.OAuthScope.EMAIL,
                    cognito.OAuthScope.PROFILE
                ],
                callback_urls=[
                    "http://localhost:8501/auth/callback",
                    "https://vocab.app-dw.net/auth/callback"
                ],
                logout_urls=[
                    "http://localhost:8501/",
                    "https://vocab.app-dw.net/"
                ]
            ),
            access_token_validity=Duration.hours(1),
            id_token_validity=Duration.hours(1),
            refresh_token_validity=Duration.days(30),
            prevent_user_existence_errors=True
        )

        # Writing Practice app client
        self.writing_practice_client = self.user_pool.add_client(
            "WritingPracticeClient",
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True,
                    implicit_code_grant=True
                ),
                scopes=[
                    cognito.OAuthScope.OPENID,
                    cognito.OAuthScope.EMAIL,
                    cognito.OAuthScope.PROFILE
                ],
                callback_urls=[
                    "http://localhost:8501/auth/callback",
                    "https://writing.app-dw.net/auth/callback"
                ],
                logout_urls=[
                    "http://localhost:8501/",
                    "https://writing.app-dw.net/"
                ]
            ),
            access_token_validity=Duration.hours(1),
            id_token_validity=Duration.hours(1),
            refresh_token_validity=Duration.days(30),
            prevent_user_existence_errors=True
        )

        # Add resource server for protected APIs
        self.user_pool.add_resource_server(
            "ResourceServer",
            identifier="api.app-dw.net",
            scopes=[
                cognito.ResourceServerScope(
                    scope_name="read",
                    scope_description="Read access to API"
                ),
                cognito.ResourceServerScope(
                    scope_name="write",
                    scope_description="Write access to API"
                )
            ]
        )

        # Outputs
        CfnOutput(self, "UserPoolId",
            value=self.user_pool.user_pool_id,
            description="User Pool ID",
            export_name=f"{construct_id}-user-pool-id"
        )

        CfnOutput(self, "UserPoolArn",
            value=self.user_pool.user_pool_arn,
            description="User Pool ARN",
            export_name=f"{construct_id}-user-pool-arn"
        )

        for client in [
            ("LangPortal", self.lang_portal_client),
            ("Haiku", self.haiku_client),
            ("Vocab", self.vocab_client),
            ("WritingPractice", self.writing_practice_client)
        ]:
            CfnOutput(
                self,
                f"{client[0]}ClientId",
                value=client[1].user_pool_client_id,
                description=f"{client[0]} Client ID",
                export_name=f"{construct_id}-{client[0].lower()}-client-id"
            )