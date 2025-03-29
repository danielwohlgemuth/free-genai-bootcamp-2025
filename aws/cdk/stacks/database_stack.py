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

class DatabaseStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create credentials for Lang Portal database
        self.lang_portal_credentials = rds.Credentials.from_generated_secret(
            username="langportal",
            secret_name=f"{construct_id}/lang-portal-db-credentials"
        )

        # Create credentials for Haiku database
        self.haiku_credentials = rds.Credentials.from_generated_secret(
            username="haiku",
            secret_name=f"{construct_id}/haiku-db-credentials"
        )

        # Create security group for Lang Portal database
        self.lang_portal_security_group = ec2.SecurityGroup(
            self, "LangPortalDBSecurityGroup",
            vpc=vpc,
            description="Security group for Lang Portal Aurora cluster",
            security_group_name=f"{construct_id}-lang-portal-db-sg"
        )

        # Create security group for Haiku database
        self.haiku_security_group = ec2.SecurityGroup(
            self, "HaikuDBSecurityGroup",
            vpc=vpc,
            description="Security group for Haiku Aurora cluster",
            security_group_name=f"{construct_id}-haiku-db-sg"
        )

        # Create Lang Portal Aurora cluster
        self.lang_portal_db = rds.DatabaseCluster(
            self, "LangPortalDB",
            engine=rds.DatabaseClusterEngine.aurora_postgres(
                version=rds.AuroraPostgresEngineVersion.VER_13_9
            ),
            credentials=self.lang_portal_credentials,
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
            security_groups=[self.lang_portal_security_group],
            backup=rds.BackupProps(
                retention=Duration.days(7),
                preferred_window="03:00-04:00"  # UTC
            ),
            parameter_group=rds.ParameterGroup.from_parameter_group_name(
                self, "LangPortalDBParameterGroup",
                parameter_group_name="default.aurora-postgresql13"
            ),
            removal_policy=RemovalPolicy.SNAPSHOT,
            cloudwatch_logs_retention=logs.RetentionDays.ONE_WEEK
        )

        # Create Haiku Aurora cluster
        self.haiku_db = rds.DatabaseCluster(
            self, "HaikuDB",
            engine=rds.DatabaseClusterEngine.aurora_postgres(
                version=rds.AuroraPostgresEngineVersion.VER_13_9
            ),
            credentials=self.haiku_credentials,
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
            security_groups=[self.haiku_security_group],
            backup=rds.BackupProps(
                retention=Duration.days(7),
                preferred_window="03:00-04:00"  # UTC
            ),
            parameter_group=rds.ParameterGroup.from_parameter_group_name(
                self, "HaikuDBParameterGroup",
                parameter_group_name="default.aurora-postgresql13"
            ),
            removal_policy=RemovalPolicy.SNAPSHOT,
            cloudwatch_logs_retention=logs.RetentionDays.ONE_WEEK
        )

        # Create RDS Proxy for Lang Portal
        self.lang_portal_proxy = rds.DatabaseProxy(
            self, "LangPortalDBProxy",
            proxy_target=rds.ProxyTarget.from_cluster(self.lang_portal_db),
            secrets=[self.lang_portal_db.secret],
            debug_logging=True,
            vpc=vpc,
            security_groups=[self.lang_portal_security_group],
            require_tls=True
        )

        # Create RDS Proxy for Haiku
        self.haiku_proxy = rds.DatabaseProxy(
            self, "HaikuDBProxy",
            proxy_target=rds.ProxyTarget.from_cluster(self.haiku_db),
            secrets=[self.haiku_db.secret],
            debug_logging=True,
            vpc=vpc,
            security_groups=[self.haiku_security_group],
            require_tls=True
        )

        # Outputs
        CfnOutput(self, "LangPortalDBEndpoint",
            value=self.lang_portal_db.cluster_endpoint.hostname,
            description="Lang Portal Database endpoint",
            export_name=f"{construct_id}-lang-portal-db-endpoint"
        )

        CfnOutput(self, "LangPortalProxyEndpoint",
            value=self.lang_portal_proxy.endpoint,
            description="Lang Portal Database Proxy endpoint",
            export_name=f"{construct_id}-lang-portal-proxy-endpoint"
        )

        CfnOutput(self, "HaikuDBEndpoint",
            value=self.haiku_db.cluster_endpoint.hostname,
            description="Haiku Database endpoint",
            export_name=f"{construct_id}-haiku-db-endpoint"
        )

        CfnOutput(self, "HaikuProxyEndpoint",
            value=self.haiku_proxy.endpoint,
            description="Haiku Database Proxy endpoint",
            export_name=f"{construct_id}-haiku-proxy-endpoint"
        )