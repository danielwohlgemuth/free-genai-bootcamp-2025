from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_elasticloadbalancingv2 as elbv2,
    aws_iam as iam,
    aws_logs as logs,
    CfnOutput,
    Duration,
    Stack
)
from constructs import Construct

class HaikuGeneratorBackendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str,
                 vpc: ec2.Vpc, database, user_pool, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create ECS Cluster
        self.cluster = ecs.Cluster(
            self, "Cluster",
            vpc=vpc,
            cluster_name=f"{construct_id}-cluster",
            container_insights=True
        )

        # Create security group for the service
        self.service_sg = ec2.SecurityGroup(
            self, "ServiceSecurityGroup",
            vpc=vpc,
            description="Security group for Haiku Generator backend service",
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
            "ApiContainer",
            image=ecs.ContainerImage.from_asset("../haiku-generator-backend"),
            memory_limit_mib=512,
            cpu=256,
            logging=ecs.LogDriver.aws_logs(
                stream_prefix="HaikuGeneratorBackend",
                log_retention=logs.RetentionDays.ONE_WEEK
            ),
            environment={
                "COGNITO_USER_POOL_ID": user_pool.user_pool_id,
                "DB_HOST": database.cluster_endpoint.hostname,
                "DB_PORT": "5432",
                "DB_NAME": "haiku",
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
            task_definition=task_definition,
            desired_count=2,
            certificate=None,  # SSL termination at CloudFront
            protocol=elbv2.ApplicationProtocol.HTTP,
            public_load_balancer=True,
            assign_public_ip=True,
            security_groups=[self.service_sg],
            task_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            listener_port=80,
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
            )
        )

        # Auto Scaling configuration
        scaling = self.service.service.auto_scale_task_count(
            max_capacity=10,
            min_capacity=2
        )

        self.service.target_group.configure_health_check(
            path="/api/health",
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

        # Grant permissions to call OpenAI API
        task_definition.add_to_task_role_policy(
            iam.PolicyStatement(
                actions=[
                    "secretsmanager:GetSecretValue"
                ],
                resources=[
                    f"arn:aws:secretsmanager:{Stack.of(self).region}:{Stack.of(self).account}:secret:openai-api-key-*"
                ]
            )
        )

        # Outputs
        CfnOutput(self, "ServiceURL",
            value=f"http://{self.service.load_balancer.load_balancer_dns_name}",
            description="Haiku Generator Backend Service URL",
            export_name=f"{construct_id}-service-url"
        )

        CfnOutput(self, "ServiceName",
            value=self.service.service.service_name,
            description="Haiku Generator Backend Service Name",
            export_name=f"{construct_id}-service-name"
        )

        CfnOutput(self, "ClusterName",
            value=self.cluster.cluster_name,
            description="ECS Cluster Name",
            export_name=f"{construct_id}-cluster-name"
        )