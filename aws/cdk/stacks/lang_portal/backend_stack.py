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
                 database: rds.DatabaseInstance,
                 user_pool: cognito.UserPool,
                 user_pool_client: cognito.UserPoolClient,
                 certificate: acm.Certificate,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

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

        # Create security group for the service
        self.service_sg = ec2.SecurityGroup(
            self, "ServiceSecurityGroup",
            vpc=vpc,
            description="Security group for Lang Portal backend service",
            security_group_name=f"{construct_id}-service-sg"
        )

        # Allow inbound from ALB on port 8000
        self.service_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(8000),
            description="Allow inbound HTTP traffic"
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
                "DB_HOST": database.instance_endpoint.hostname,
                "DB_PORT": "5432",
                "DB_NAME": "langportal",
                "AWS_DEFAULT_REGION": Stack.of(self).region
            },
            secrets={
                "DB_USERNAME": ecs.Secret.from_secrets_manager(database.secret, "username"),
                "DB_PASSWORD": ecs.Secret.from_secrets_manager(database.secret, "password")
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
            security_groups=[self.service_sg],
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