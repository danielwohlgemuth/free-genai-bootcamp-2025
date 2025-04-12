from aws_cdk import (
    aws_certificatemanager as acm,
    aws_route53 as route53,
    Stack
)
from constructs import Construct

class HaikuGeneratorCertificateStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

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