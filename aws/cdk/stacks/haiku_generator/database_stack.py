from aws_cdk import (
    aws_ec2 as ec2,
    aws_logs as logs,
    aws_rds as rds,
    CfnOutput,
    Duration,
    RemovalPolicy,
    Stack
)
from constructs import Construct

class HaikuGeneratorDatabaseStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create credentials for database
        self.credentials = rds.Credentials.from_generated_secret(
            username="haiku",
            secret_name=f"{construct_id}/haiku-db-credentials"
        )

        # Create security group for database
        self.security_group = ec2.SecurityGroup(
            self, "DBSecurityGroup",
            vpc=vpc,
            description="Security group for Aurora cluster",
            security_group_name=f"{construct_id}-db-sg"
        )

        # Create Aurora cluster
        self.db = rds.DatabaseCluster(
            self, "HaikuDB",
            default_database_name="haiku",
            engine=rds.DatabaseClusterEngine.aurora_postgres(
                version=rds.AuroraPostgresEngineVersion.VER_16_6
            ),
            credentials=self.credentials,
            writer=rds.ClusterInstance.provisioned("writer",
                publicly_accessible=False,
                instance_type=ec2.InstanceType.of(
                    ec2.InstanceClass.T4G,
                    ec2.InstanceSize.MEDIUM
                ),
            ),
            readers=[
                rds.ClusterInstance.serverless_v2("reader", scale_with_writer=True)
            ],
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            vpc=vpc,
            security_groups=[self.security_group],
            backup=rds.BackupProps(
                retention=Duration.days(7),
                preferred_window="03:00-04:00"  # UTC
            ),
            parameter_group=rds.ParameterGroup.from_parameter_group_name(
                self, "DBParameterGroup",
                parameter_group_name="default.aurora-postgresql16"
            ),
            removal_policy=RemovalPolicy.SNAPSHOT,
            cloudwatch_logs_retention=logs.RetentionDays.ONE_WEEK
        )

        # Outputs
        CfnOutput(self, "DBEndpoint",
            value=self.db.cluster_endpoint.hostname,
            description="Database endpoint",
            export_name=f"{construct_id}-db-endpoint"
        )