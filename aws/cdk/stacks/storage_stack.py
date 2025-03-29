from aws_cdk import (
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_s3 as s3,
    CfnOutput,
    Duration,
    RemovalPolicy,
    Stack
)
from constructs import Construct

class StorageStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create S3 bucket for access logging
        self.logging_bucket = s3.Bucket(
            self, "LoggingBucket",
            bucket_name=f"{construct_id.lower()}-logs",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.RETAIN,
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

        # Create S3 bucket for Lang Portal frontend
        self.lang_portal_bucket = s3.Bucket(
            self, "LangPortalBucket",
            bucket_name=f"{construct_id.lower()}-lang-portal",
            website_index_document="index.html",
            website_error_document="index.html",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.RETAIN,
            server_access_logs_bucket=self.logging_bucket,
            server_access_logs_prefix="lang-portal-logs/",
            cors=[
                s3.CorsRule(
                    allowed_methods=[s3.HttpMethods.GET],
                    allowed_origins=["https://lang-portal.app-dw.net"],
                    allowed_headers=["*"],
                    max_age=86400
                )
            ]
        )

        # Create S3 bucket for Haiku Generator frontend
        self.haiku_bucket = s3.Bucket(
            self, "HaikuBucket",
            bucket_name=f"{construct_id.lower()}-haiku",
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
                    allowed_origins=["https://haiku.app-dw.net"],
                    allowed_headers=["*"],
                    max_age=86400
                )
            ]
        )

        # Create CloudFront distribution for Lang Portal
        self.lang_portal_distribution = cloudfront.Distribution(
            self, "LangPortalDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin(self.lang_portal_bucket),
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
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,
            enable_logging=True,
            log_bucket=self.logging_bucket,
            log_file_prefix="lang-portal-cf-logs/"
        )

        # Create CloudFront distribution for Haiku Generator
        self.haiku_distribution = cloudfront.Distribution(
            self, "HaikuDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin(self.haiku_bucket),
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
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,
            enable_logging=True,
            log_bucket=self.logging_bucket,
            log_file_prefix="haiku-cf-logs/"
        )

        # Outputs
        CfnOutput(self, "LangPortalBucketName",
            value=self.lang_portal_bucket.bucket_name,
            description="Lang Portal S3 bucket name",
            export_name=f"{construct_id}-lang-portal-bucket-name"
        )

        CfnOutput(self, "LangPortalDistributionId",
            value=self.lang_portal_distribution.distribution_id,
            description="Lang Portal CloudFront distribution ID",
            export_name=f"{construct_id}-lang-portal-distribution-id"
        )

        CfnOutput(self, "LangPortalDistributionDomain",
            value=self.lang_portal_distribution.domain_name,
            description="Lang Portal CloudFront domain name",
            export_name=f"{construct_id}-lang-portal-distribution-domain"
        )

        CfnOutput(self, "HaikuBucketName",
            value=self.haiku_bucket.bucket_name,
            description="Haiku Generator S3 bucket name",
            export_name=f"{construct_id}-haiku-bucket-name"
        )

        CfnOutput(self, "HaikuDistributionId",
            value=self.haiku_distribution.distribution_id,
            description="Haiku Generator CloudFront distribution ID",
            export_name=f"{construct_id}-haiku-distribution-id"
        )

        CfnOutput(self, "HaikuDistributionDomain",
            value=self.haiku_distribution.domain_name,
            description="Haiku Generator CloudFront domain name",
            export_name=f"{construct_id}-haiku-distribution-domain"
        )