from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
)
from constructs import Construct

class HaikuGeneratorBackendStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # VPC for all services
        vpc = ec2.Vpc(self, "HaikuVPC", max_azs=2)

        # RDS PostgreSQL Instance
        db = rds.DatabaseInstance(self, "HaikuDB",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_15
            ),
            vpc=vpc,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.MICRO
            )
        )

        # ECS Cluster
        cluster = ecs.Cluster(self, "HaikuCluster", vpc=vpc)

        # MinIO replacement with S3
        bucket = s3.Bucket(self, "XXXXXXXXXXX")

        # Task Definition for the main application
        task_def = ecs.FargateTaskDefinition(self, "HaikuTaskDef")
