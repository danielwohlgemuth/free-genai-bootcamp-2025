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

class LangPortalDatabaseStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create credentials for database
        self.credentials = rds.Credentials.from_generated_secret(
            username="langportal",
            secret_name=f"{construct_id}/lang-portal-db-credentials"
        )

        # Create security group for database
        self.security_group = ec2.SecurityGroup(
            self, "DBSecurityGroup",
            vpc=vpc,
            description="Security group for RDS instance",
            security_group_name=f"{construct_id}-db-sg"
        )

        # Create standard RDS PostgreSQL instance
        self.db = rds.DatabaseInstance(
            self, "DB",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_16_6
            ),
            credentials=self.credentials,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T4G,
                ec2.InstanceSize.MEDIUM
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            security_groups=[self.security_group],
            publicly_accessible=False,
            backup_retention=Duration.days(7),
            preferred_backup_window="03:00-04:00",  # UTC
            deletion_protection=True,
            removal_policy=RemovalPolicy.SNAPSHOT,
            cloudwatch_logs_retention=logs.RetentionDays.ONE_WEEK,
            parameter_group=rds.ParameterGroup.from_parameter_group_name(
                self, "DBParameterGroup",
                parameter_group_name="default.postgres16"
            )
        )