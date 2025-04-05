from aws_cdk import (
    aws_certificatemanager as acm,
    aws_cognito as cognito,
    aws_route53 as route53,
    aws_route53_targets as targets,
    CfnOutput,
    Duration,
    RemovalPolicy,
    Stack
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
                email=True
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

        # Import hosted zone
        self.hosted_zone = route53.HostedZone.from_lookup(
            self, "HostedZone",
            domain_name="app-dw.net"
        )

        # Create certificate for Cognito
        self.certificate = acm.Certificate(
            self, "Certificate",
            domain_name="auth.app-dw.net",
            validation=acm.CertificateValidation.from_dns(self.hosted_zone)
        )

        # Add Root DNS record to use cognito custom domain
        route53.ARecord(
            self, "RootDomainARecord",
            zone=self.hosted_zone,
            target=route53.RecordTarget.from_ip_addresses(
                "1.1.1.1"
            ),
            record_name="app-dw.net"
        )

        # Add domain for Cognito
        self.domain = self.user_pool.add_domain(
            "CognitoDomain",
            custom_domain=cognito.CustomDomainOptions(
                domain_name="auth.app-dw.net",
                certificate=self.certificate
            ),
            managed_login_version=cognito.ManagedLoginVersion.NEWER_MANAGED_LOGIN
        )

        # Add DNS record for the custom domain
        self.record = route53.ARecord(
            self, "CognitoDomainARecord",
            zone=self.hosted_zone,
            target=route53.RecordTarget.from_alias(
                targets.UserPoolDomainTarget(self.domain)
            ),
            record_name="auth.app-dw.net"
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

        cognito.CfnManagedLoginBranding(
            self, "LangPortalManagedLoginBranding",
            user_pool_id=self.user_pool.user_pool_id,
            client_id=self.lang_portal_client.user_pool_client_id,
            return_merged_resources=True,
            use_cognito_provided_values=True
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
                    "http://localhost:3001/auth/callback",
                    "https://haiku.app-dw.net/auth/callback"
                ],
                logout_urls=[
                    "http://localhost:3001/",
                    "https://haiku.app-dw.net/"
                ]
            ),
            access_token_validity=Duration.hours(1),
            id_token_validity=Duration.hours(1),
            refresh_token_validity=Duration.days(30),
            prevent_user_existence_errors=True
        )

        cognito.CfnManagedLoginBranding(
            self, "HaikuManagedLoginBranding",
            user_pool_id=self.user_pool.user_pool_id,
            client_id=self.haiku_client.user_pool_client_id,
            return_merged_resources=True,
            use_cognito_provided_values=True
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
                    "http://localhost:3002/auth/callback",
                    "https://vocab.app-dw.net/auth/callback"
                ],
                logout_urls=[
                    "http://localhost:3002/",
                    "https://vocab.app-dw.net/"
                ]
            ),
            access_token_validity=Duration.hours(1),
            id_token_validity=Duration.hours(1),
            refresh_token_validity=Duration.days(30),
            prevent_user_existence_errors=True
        )

        cognito.CfnManagedLoginBranding(
            self, "VocabManagedLoginBranding",
            user_pool_id=self.user_pool.user_pool_id,
            client_id=self.vocab_client.user_pool_client_id,
            return_merged_resources=True,
            use_cognito_provided_values=True
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
                    "http://localhost:3003/auth/callback",
                    "https://writing.app-dw.net/auth/callback"
                ],
                logout_urls=[
                    "http://localhost:3003/",
                    "https://writing.app-dw.net/"
                ]
            ),
            access_token_validity=Duration.hours(1),
            id_token_validity=Duration.hours(1),
            refresh_token_validity=Duration.days(30),
            prevent_user_existence_errors=True
        )

        cognito.CfnManagedLoginBranding(
            self, "WritingPracticeManagedLoginBranding",
            user_pool_id=self.user_pool.user_pool_id,
            client_id=self.writing_practice_client.user_pool_client_id,
            return_merged_resources=True,
            use_cognito_provided_values=True
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
        
        CfnOutput(
            self,
            "LangPortalClientId",
            value=self.lang_portal_client.user_pool_client_id,
            description="Lang Portal Client ID",
            export_name=f"{construct_id}-lang-portal-client-id"
        )
        
        CfnOutput(
            self,
            "HaikuClientId",
            value=self.haiku_client.user_pool_client_id,
            description="Haiku Client ID",
            export_name=f"{construct_id}-haiku-client-id"
        )
        
        CfnOutput(
            self,
            "VocabClientId",
            value=self.vocab_client.user_pool_client_id,
            description="Vocab Client ID",
            export_name=f"{construct_id}-vocab-client-id"
        )
        
        CfnOutput(
            self,
            "WritingPracticeClientId",
            value=self.writing_practice_client.user_pool_client_id,
            description="Writing Practice Client ID",
            export_name=f"{construct_id}-writing-practice-client-id"
        )