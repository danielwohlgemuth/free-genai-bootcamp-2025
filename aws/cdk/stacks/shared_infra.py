from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs
)
from constructs import Construct

class SharedInfraStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Shared VPC
        self.vpc = ec2.Vpc(
            self, "SharedVPC",
            max_azs=2,
            nat_gateways=1
        )

        # Shared ECS Cluster
        self.cluster = ecs.Cluster(
            self, "SharedCluster",
            vpc=self.vpc,
            container_insights=True
        )