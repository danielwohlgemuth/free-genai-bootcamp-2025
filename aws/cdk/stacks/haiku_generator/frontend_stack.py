from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_certificatemanager as acm,
    CfnOutput
)
from constructs import Construct

class HaikuGeneratorFrontendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, 
                 user_pool, storage_bucket, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Store references
        self.user_pool = user_pool
        self.storage_bucket = storage_bucket

        # Import hosted zone
        self.hosted_zone = route53.HostedZone.from_lookup(
            self, "HostedZone",
            domain_name="app-dw.net"
        )

        # Create certificate for CloudFront
        self.certificate = acm.Certificate(
            self, "Certificate",
            domain_name="haiku.app-dw.net",
            validation=acm.CertificateValidation.from_dns(self.hosted_zone)
        )

        # Create Route53 record
        route53.ARecord(
            self, "SiteAliasRecord",
            zone=self.hosted_zone,
            target=route53.RecordTarget.from_alias(
                targets.CloudFrontTarget(self.storage_bucket)
            ),
            record_name="haiku.app-dw.net"
        )

        # Outputs
        CfnOutput(self, "DomainName",
            value="https://haiku.app-dw.net",
            description="Haiku Generator frontend URL",
            export_name=f"{construct_id}-domain-name"
        )