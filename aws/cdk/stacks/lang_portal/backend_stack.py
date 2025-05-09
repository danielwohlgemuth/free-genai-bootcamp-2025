from aws_cdk import (
    aws_certificatemanager as acm,
    aws_cognito as cognito,
    aws_ec2 as ec2,
    aws_ecr as ecr,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_elasticloadbalancingv2 as elbv2,
    aws_logs as logs,
    aws_rds as rds,
    CfnOutput,
    Duration,
    RemovalPolicy,
    Stack
)
from constructs import Construct

class LangPortalBackendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str,
                 vpc: ec2.Vpc,
                 user_pool: cognito.UserPool,
                 user_pool_client: cognito.UserPoolClient,
                 certificate: acm.Certificate,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create credentials for database
        self.credentials = rds.Credentials.from_generated_secret(
            username="langportal",
            secret_name=f"{construct_id}/lang-portal-db-credentials"
        )

        # Create security group for the database
        self.database_security_group = ec2.SecurityGroup(
            self, "DatabaseSecurityGroup",
            vpc=vpc,
            description="Security group for Lang Portal database",
            security_group_name=f"{construct_id}-database-sg"
        )

        # Create standard RDS PostgreSQL instance
        self.db = rds.DatabaseInstance(
            self, "DB",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_16_6
            ),
            credentials=self.credentials,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3,
                ec2.InstanceSize.MICRO
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            allocated_storage=20,
            security_groups=[self.database_security_group],
            publicly_accessible=False,
            backup_retention=Duration.days(7),
            preferred_backup_window="03:00-04:00",  # UTC
            deletion_protection=False,
            delete_automated_backups=True,
            removal_policy=RemovalPolicy.SNAPSHOT,
            cloudwatch_logs_retention=logs.RetentionDays.ONE_WEEK,
            parameter_group=rds.ParameterGroup.from_parameter_group_name(
                self, "DBParameterGroup",
                parameter_group_name="default.postgres16"
            )
        )

        # Create ECR Repository
        self.repository = ecr.Repository(
            self, "Repository",
            repository_name="lang-portal-backend",
            removal_policy=RemovalPolicy.DESTROY,
            lifecycle_rules=[
                ecr.LifecycleRule(
                    max_image_count=5,
                    rule_priority=1,
                    description="Keep only the last 5 images"
                )
            ]
        )

        # Create ECS Cluster
        self.cluster = ecs.Cluster(
            self, "Cluster",
            vpc=vpc,
            cluster_name="lang-portal",
            container_insights_v2=ecs.ContainerInsights.ENABLED
        )

        # Allow inbound only from CloudFront using managed prefix list
        self.alb_security_group = ec2.SecurityGroup(
            self, "ALBSecurityGroup",
            vpc=vpc,
            description="Security group for ALB",
            security_group_name=f"{construct_id}-alb-sg"
        )

        # Look up CloudFront prefix list
        cloudfront_prefix_list = ec2.PrefixList.from_lookup(
            self, "CloudFrontPrefixList",
            prefix_list_name="com.amazonaws.global.cloudfront.origin-facing"
        )

        # Allow ALB to connect to ECS tasks
        self.alb_security_group.add_ingress_rule(
            peer=ec2.Peer.prefix_list(cloudfront_prefix_list.prefix_list_id),
            connection=ec2.Port.tcp(443),
            description="Allow inbound HTTPS traffic from CloudFront only"
        )

        # Create security group for the service
        self.service_security_group = ec2.SecurityGroup(
            self, "ServiceSecurityGroup",
            vpc=vpc,
            description="Security group for Lang Portal backend service",
            security_group_name=f"{construct_id}-service-sg"
        )

        # Allow internal traffic from ALB to ECS tasks on port 8000
        self.service_security_group.add_ingress_rule(
            peer=ec2.Peer.security_group_id(self.alb_security_group.security_group_id),
            connection=ec2.Port.tcp(8000),
            description="Allow inbound traffic from ALB to ECS tasks"
        )

        # Allow internal traffic from service to database
        self.database_security_group.add_ingress_rule(
            peer=ec2.Peer.security_group_id(self.service_security_group.security_group_id),
            connection=ec2.Port.tcp(5432),
            description="Allow inbound traffic from service to database"
        )

        # Create Task Definition
        task_definition = ecs.FargateTaskDefinition(
            self, "TaskDef",
            memory_limit_mib=512,
            cpu=256,
            family=f"{construct_id}-task"
        )

        # Add container to task definition
        container = task_definition.add_container(
            "Container",
            container_name="Container",
            image=ecs.ContainerImage.from_ecr_repository(
                repository=self.repository,
                tag="latest"
            ),
            memory_limit_mib=512,
            cpu=256,
            logging=ecs.LogDriver.aws_logs(
                stream_prefix="LangPortalBackend",
                log_retention=logs.RetentionDays.ONE_WEEK
            ),
            environment={
                "COGNITO_USER_POOL_ID": user_pool.user_pool_id,
                "COGNITO_CLIENT_ID": user_pool_client.user_pool_client_id,
                "COGNITO_REGION": Stack.of(self).region,
                "DB_HOST": self.db.instance_endpoint.hostname,
                "DB_PORT": str(self.db.instance_endpoint.port),
                "DB_NAME": "langportal",
                "AWS_DEFAULT_REGION": Stack.of(self).region
            },
            secrets={
                "DB_USER": ecs.Secret.from_secrets_manager(self.db.secret, "username"),
                "DB_PASSWORD": ecs.Secret.from_secrets_manager(self.db.secret, "password")
            }
        )

        container.add_port_mappings(
            ecs.PortMapping(
                container_port=8000,
                protocol=ecs.Protocol.TCP
            )
        )

        # Create Fargate Service
        self.service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "Service",
            cluster=self.cluster,
            service_name="backend",
            task_definition=task_definition,
            desired_count=1,
            certificate=certificate,
            protocol=elbv2.ApplicationProtocol.HTTPS,
            public_load_balancer=True,
            assign_public_ip=False,
            security_groups=[self.service_security_group],
            task_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            listener_port=443,
            target_protocol=elbv2.ApplicationProtocol.HTTP,
            health_check=ecs.HealthCheck(
                command=["CMD-SHELL", "curl -f http://localhost:8000/api/health || exit 1"],
                interval=Duration.seconds(30),
                timeout=Duration.seconds(5),
                retries=3,
                start_period=Duration.seconds(60)
            ),
            capacity_provider_strategies=[
                ecs.CapacityProviderStrategy(
                    capacity_provider="FARGATE_SPOT",
                    weight=1
                )
            ],
            circuit_breaker=ecs.DeploymentCircuitBreaker(
                rollback=True
            ),
            enable_execute_command=True,
            min_healthy_percent=100
        )

        # Auto Scaling configuration
        scaling = self.service.service.auto_scale_task_count(
            max_capacity=4,
            min_capacity=1
        )

        self.service.target_group.configure_health_check(
            path="/api/health",
            port="8000",
            healthy_http_codes="200",
            interval=Duration.seconds(30),
            timeout=Duration.seconds(3),
            healthy_threshold_count=2,
            unhealthy_threshold_count=3
        )

        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=70,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60)
        )

        scaling.scale_on_memory_utilization(
            "MemoryScaling",
            target_utilization_percent=70,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60)
        )