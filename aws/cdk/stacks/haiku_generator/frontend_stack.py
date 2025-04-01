from aws_cdk import (
    aws_certificatemanager as acm,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_iam as iam,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_s3 as s3,
    CfnOutput,
    Duration,
    RemovalPolicy,
    Stack
)
from constructs import Construct

class HaikuGeneratorFrontendStack(Stack):
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

        # Create S3 bucket for access logging
        self.logging_bucket = s3.Bucket(
            self, "LoggingBucket",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.RETAIN,
            object_ownership=s3.ObjectOwnership.BUCKET_OWNER_PREFERRED,  
            lifecycle_rules=[
                s3.LifecycleRule(
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.INTELLIGENT_TIERING,
                            transition_after=Duration.days(90)
                        )
                    ],
                    expiration=Duration.days(365)
                )
            ]
        )

        # Grant CloudFront permission to write logs
        self.logging_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                sid="AllowCloudFrontLogDelivery",
                actions=["s3:PutObject"],
                principals=[iam.ServicePrincipal("delivery.logs.amazonaws.com")],
                resources=[f"{self.logging_bucket.bucket_arn}/*"]
            )
        )

        # Create S3 bucket for Haiku Generator frontend
        self.bucket = s3.Bucket(
            self, "Bucket",
            website_index_document="index.html",
            website_error_document="index.html",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.RETAIN,
            server_access_logs_bucket=self.logging_bucket,
            server_access_logs_prefix="haiku-logs/",
            cors=[
                s3.CorsRule(
                    allowed_methods=[s3.HttpMethods.GET],
                    allowed_origins=[
                        "https://haiku.app-dw.net",
                        "http://localhost:3001"
                    ],
                    allowed_headers=["*"],
                    max_age=86400
                )
            ]
        )

        # Create CloudFront distribution for Haiku Generator
        self.distribution = cloudfront.Distribution(
            self, "Distribution",
            certificate=self.certificate,
            domain_names=["haiku.app-dw.net"],
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(
                    self.bucket,
                    origin_access_levels=[cloudfront.AccessLevel.READ]
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
                origin_request_policy=cloudfront.OriginRequestPolicy.CORS_S3_ORIGIN
            ),
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
            ],
            default_root_object="index.html",
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,
            enable_logging=True,
            log_bucket=self.logging_bucket,
            log_file_prefix="haiku-cf-logs/",
            log_includes_cookies=False
        )

        # Create Route53 record
        route53.ARecord(
            self, "SiteAliasRecord",
            zone=self.hosted_zone,
            target=route53.RecordTarget.from_alias(
                targets.CloudFrontTarget(self.distribution)
            ),
            record_name="haiku.app-dw.net"
        )

        # Outputs
        CfnOutput(self, "DomainName",
            value="https://haiku.app-dw.net",
            description="Haiku Generator frontend URL",
            export_name=f"{construct_id}-domain-name"
        )

        CfnOutput(self, "BucketName",
            value=self.bucket.bucket_name,
            description="Haiku Generator S3 bucket name",
            export_name=f"{construct_id}-bucket-name"
        )

        CfnOutput(self, "DistributionId",
            value=self.distribution.distribution_id,
            description="Haiku Generator CloudFront distribution ID",
            export_name=f"{construct_id}-distribution-id"
        )

        CfnOutput(self, "DistributionDomain",
            value=self.distribution.domain_name,
            description="Haiku Generator CloudFront domain name",
            export_name=f"{construct_id}-distribution-domain"
        )