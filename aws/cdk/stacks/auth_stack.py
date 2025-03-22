from aws_cdk import (
    Stack,
    aws_cognito as cognito,
    aws_certificatemanager as acm,
    aws_route53 as route53,
    aws_route53_targets as targets,
    CfnOutput,
)
from constructs import Construct
from cdk.constants.settings import (
    ROOT_DOMAIN,
    AUTH_SUBDOMAIN,
    APPLICATIONS
)


class AuthStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get or create hosted zone
        hosted_zone = route53.HostedZone.from_lookup(
            self, "HostedZone",
            domain_name=ROOT_DOMAIN
        )

        # Create ACM certificate for auth domain
        auth_domain = f"{AUTH_SUBDOMAIN}.{ROOT_DOMAIN}"
        certificate = acm.Certificate(
            self, "AuthCertificate",
            domain_name=auth_domain,
            validation=acm.CertificateValidation.from_dns(hosted_zone)
        )

        # Create Cognito User Pool
        user_pool = cognito.UserPool(
            self, "UserPool",
            user_pool_name="language-apps-user-pool",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(
                email=True
            ),
            auto_verify=cognito.AutoVerifiedAttrs(
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
            )
        )

        # Add domain prefix
        domain = user_pool.add_domain(
            "CognitoDomain",
            custom_domain=cognito.CustomDomainOptions(
                domain_name=auth_domain,
                certificate=certificate
            )
        )

        # Create DNS record for auth domain
        route53.ARecord(
            self, "AuthDomainRecord",
            zone=hosted_zone,
            record_name=AUTH_SUBDOMAIN,
            target=route53.RecordTarget.from_alias(
                targets.UserPoolDomainTarget(domain)
            )
        )

        # Create app clients for each frontend application
        for app_name, app_config in APPLICATIONS.items():
            if "frontend" in app_config:
                frontend_config = app_config["frontend"]
                app_domain = f"{frontend_config.subdomain}.{ROOT_DOMAIN}"
                
                client = user_pool.add_client(
                    f"{app_name}-client",
                    o_auth=cognito.OAuthSettings(
                        flows=cognito.OAuthFlows(
                            authorization_code_grant=True
                        ),
                        scopes=[cognito.OAuthScope.EMAIL, 
                               cognito.OAuthScope.OPENID, 
                               cognito.OAuthScope.PROFILE],
                        callback_urls=[
                            f"https://{app_domain}/",
                            f"http://localhost:{frontend_config.dev_port}/"  # App-specific dev port
                        ],
                        logout_urls=[
                            f"https://{app_domain}/",
                            f"http://localhost:{frontend_config.dev_port}/"  # App-specific dev port
                        ]
                    ),
                    prevent_user_existence_errors=True
                )

        # Outputs
        CfnOutput(
            self, "UserPoolId",
            value=user_pool.user_pool_id,
            description="Cognito User Pool ID"
        )
        CfnOutput(
            self, "UserPoolDomain",
            value=auth_domain,
            description="Cognito User Pool Domain"
        )
