from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    CfnOutput
)
from constructs import Construct

class NetworkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC with 3 AZs
        self.vpc = ec2.Vpc(
            self, "VPC",
            max_azs=3,
            nat_gateways=3,
            enable_dns_hostnames=True,
            enable_dns_support=True,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Isolated",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24
                )
            ],
            vpc_name=f"{construct_id}-vpc"
        )

        # Create VPC endpoints for AWS services
        self.vpc.add_gateway_endpoint(
            "S3Endpoint",
            service=ec2.GatewayVpcEndpointAwsService.S3
        )

        self.vpc.add_interface_endpoint(
            "EcrDockerEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER
        )

        self.vpc.add_interface_endpoint(
            "EcrEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.ECR
        )

        self.vpc.add_interface_endpoint(
            "CloudWatchLogsEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS
        )

        self.vpc.add_interface_endpoint(
            "SecretsManagerEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER
        )

        # Outputs
        CfnOutput(self, "VPCId",
            value=self.vpc.vpc_id,
            description="VPC ID",
            export_name=f"{construct_id}-vpc-id"
        )

        CfnOutput(self, "PublicSubnets",
            value=",".join(self.vpc.select_subnets(
                subnet_type=ec2.SubnetType.PUBLIC
            ).subnet_ids),
            description="Public Subnet IDs",
            export_name=f"{construct_id}-public-subnets"
        )

        CfnOutput(self, "PrivateSubnets",
            value=",".join(self.vpc.select_subnets(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ).subnet_ids),
            description="Private Subnet IDs", 
            export_name=f"{construct_id}-private-subnets"
        )

        CfnOutput(self, "IsolatedSubnets",
            value=",".join(self.vpc.select_subnets(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ).subnet_ids),
            description="Isolated Subnet IDs",
            export_name=f"{construct_id}-isolated-subnets"
        )