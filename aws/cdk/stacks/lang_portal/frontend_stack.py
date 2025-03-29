from aws_cdk import (
    aws_certificatemanager as acm,
    aws_route53 as route53,
    aws_route53_targets as targets,
    CfnOutput,
    Stack
)
from constructs import Construct

class LangPortalFrontendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, 
                 distribution, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Import hosted zone
        self.hosted_zone = route53.HostedZone.from_lookup(
            self, "HostedZone",
            domain_name="app-dw.net"
        )

        # Create certificate for CloudFront
        self.certificate = acm.Certificate(
            self, "Certificate",
            domain_name="lang-portal.app-dw.net",
            validation=acm.CertificateValidation.from_dns(self.hosted_zone)
        )

        # Create Route53 record
        route53.ARecord(
            self, "SiteAliasRecord",
            zone=self.hosted_zone,
            target=route53.RecordTarget.from_alias(
                targets.CloudFrontTarget(distribution)
            ),
            record_name="lang-portal.app-dw.net"
        )

        # Outputs
        CfnOutput(self, "DomainName",
            value="https://lang-portal.app-dw.net",
            description="Lang Portal frontend URL",
            export_name=f"{construct_id}-domain-name"
        )