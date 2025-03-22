from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_certificatemanager as acm,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_s3_deployment as s3deploy,
    CfnOutput,
    RemovalPolicy
)
from constructs import Construct
from cdk.constants.settings import ROOT_DOMAIN


class SPAFrontendStack(Stack):
    def __init__(
        self, 
        scope: Construct, 
        construct_id: str, 
        app_name: str,
        subdomain: str,
        source_path: str,
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

        # Create S3 bucket for website
        website_bucket = s3.Bucket(
            self, "WebsiteBucket",
            bucket_name=site_domain,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # Create CloudFront Origin Access Identity
        origin_access_identity = cloudfront.OriginAccessIdentity(
            self, "OAI",
            comment=f"OAI for {site_domain}"
        )
        website_bucket.grant_read(origin_access_identity)

        # Create CloudFront distribution
        distribution = cloudfront.Distribution(
            self, "Distribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(
                    website_bucket,
                    origin_access_identity=origin_access_identity
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
            ),
            domain_names=[site_domain],
            certificate=certificate,
            default_root_object="index.html",
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html"
                ),
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html"
                )
            ]
        )

        # Create Route53 alias record
        route53.ARecord(
            self, "SiteAliasRecord",
            zone=hosted_zone,
            record_name=subdomain,
            target=route53.RecordTarget.from_alias(
                targets.CloudFrontTarget(distribution)
            )
        )

        # Deploy site contents
        s3deploy.BucketDeployment(
            self, "DeployWebsite",
            sources=[s3deploy.Source.asset(source_path)],
            destination_bucket=website_bucket,
            distribution=distribution,
            distribution_paths=["/*"]
        )

        # Stack Outputs
        CfnOutput(
            self, "BucketName",
            value=website_bucket.bucket_name
        )
        CfnOutput(
            self, "DistributionId",
            value=distribution.distribution_id
        )
        CfnOutput(
            self, "DomainName",
            value=site_domain
        )
