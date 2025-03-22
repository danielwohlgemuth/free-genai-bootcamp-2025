from aws_cdk import (
    Stack,
    aws_apprunner as apprunner,
    aws_certificatemanager as acm,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_ecr_assets as ecr_assets,
    aws_iam as iam,
    CfnOutput,
    Duration
)
from constructs import Construct
from cdk.constants.settings import ROOT_DOMAIN


class PythonFrontendStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        app_name: str,
        subdomain: str,
        source_path: str,
        framework: str,  # 'streamlit' or 'gradio'
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        site_domain = f"{subdomain}.{ROOT_DOMAIN}"

        # Get the hosted zone
        hosted_zone = route53.HostedZone.from_lookup(
            self, "HostedZone",
            domain_name=ROOT_DOMAIN
        )

        # Create ACM Certificate
        certificate = acm.Certificate(
            self, "SiteCertificate",
            domain_name=site_domain,
            validation=acm.CertificateValidation.from_dns(hosted_zone)
        )

        # Create ECR image asset
        image = ecr_assets.DockerImageAsset(
            self, "DockerImage",
            directory=source_path
        )

        # Create App Runner instance role
        instance_role = iam.Role(
            self, "AppRunnerInstanceRole",
            assumed_by=iam.ServicePrincipal("tasks.apprunner.amazonaws.com")
        )

        # Framework-specific configurations
        port = 8501 if framework == "streamlit" else 7860
        health_check_path = "/_stcore/health" if framework == "streamlit" else "/healthz"

        # Create App Runner service
        app_runner_service = apprunner.Service(
            self, "Service",
            service_name=f"{app_name}-service",
            source=apprunner.Source.from_asset(
                image_configuration=apprunner.ImageConfiguration(
                    port=port,
                    environment_variables={
                        "STREAMLIT_SERVER_ADDRESS": "0.0.0.0" if framework == "streamlit" else None,
                        "GRADIO_SERVER_NAME": "0.0.0.0" if framework == "gradio" else None
                    }
                ),
                asset=image
            ),
            instance_role=instance_role,
            cpu=apprunner.Cpu.ONE_VCPU,
            memory=apprunner.Memory.TWO_GB,
            health_check=apprunner.HealthCheck(
                path=health_check_path,
                timeout=Duration.seconds(2),
                interval=Duration.seconds(5),
                healthy_threshold=3,
                unhealthy_threshold=2
            )
        )

        # Add custom domain to App Runner service
        custom_domain = apprunner.CfnService.CustomDomainProperty(
            domain_name=site_domain,
            enable_www_subdomain=False,
            certificate_arn=certificate.certificate_arn
        )

        # Create Route53 alias record
        route53.ARecord(
            self, "SiteAliasRecord",
            zone=hosted_zone,
            record_name=subdomain,
            target=route53.RecordTarget.from_alias(
                targets.ApiGatewayv2DomainProperties(
                    app_runner_service.service_url,
                    "/*"
                )
            )
        )

        # Stack Outputs
        CfnOutput(
            self, "ServiceURL",
            value=app_runner_service.service_url
        )
        CfnOutput(
            self, "DomainName",
            value=site_domain
        )
