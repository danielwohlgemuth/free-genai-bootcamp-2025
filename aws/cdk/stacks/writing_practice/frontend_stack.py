from aws_cdk import (
    aws_certificatemanager as acm,
    aws_ec2 as ec2,
    aws_ecr as ecr,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_elasticloadbalancingv2 as elbv2,
    aws_iam as iam,
    aws_logs as logs,
    aws_route53 as route53,
    aws_secretsmanager as secretsmanager,
    CfnOutput,
    Duration,
    RemovalPolicy,
    Stack
)
from constructs import Construct

class WritingPracticeFrontendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str,
                 vpc: ec2.Vpc, user_pool, user_pool_client, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create ECR Repository
        self.repository = ecr.Repository(
            self, "Repository",
            repository_name=f"{construct_id}-repo".lower(),
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
            cluster_name=f"{construct_id}-cluster",
            container_insights_v2=ecs.ContainerInsights.ENABLED
        )

        # Import hosted zone
        self.hosted_zone = route53.HostedZone.from_lookup(
            self, "HostedZone",
            domain_name="app-dw.net"
        )

        # Create certificate for ALB
        self.certificate = acm.Certificate(
            self, "Certificate",
            domain_name="writing.app-dw.net",
            validation=acm.CertificateValidation.from_dns(self.hosted_zone)
        )

        # # Create security group for the service
        # self.service_sg = ec2.SecurityGroup(
        #     self, "ServiceSecurityGroup",
        #     vpc=vpc,
        #     description="Security group for Writing Practice frontend service",
        #     security_group_name=f"{construct_id}-service-sg"
        # )

        # # Allow inbound from ALB on Streamlit port 8501
        # self.service_sg.add_ingress_rule(
        #     peer=ec2.Peer.any_ipv4(),
        #     connection=ec2.Port.tcp(8501),
        #     description="Allow inbound HTTP traffic"
        # )

        # # Create Task Definition
        # task_definition = ecs.FargateTaskDefinition(
        #     self, "TaskDef",
        #     memory_limit_mib=2048,
        #     cpu=1024,
        #     family=f"{construct_id}-task"
        # )

        # # Add container to task definition
        # container = task_definition.add_container(
        #     "StreamlitContainer",
        #     image=ecs.ContainerImage.from_ecr_repository(
        #         repository=self.repository,
        #         tag="latest"
        #     ),
        #     memory_limit_mib=2048,
        #     cpu=1024,
        #     logging=ecs.LogDriver.aws_logs(
        #         stream_prefix="WritingPractice",
        #         log_retention=logs.RetentionDays.ONE_WEEK
        #     ),
        #     environment={
        #         "COGNITO_USER_POOL_ID": user_pool.user_pool_id,
        #         "COGNITO_APP_CLIENT_ID": user_pool_client.user_pool_client_id,
        #         "AWS_DEFAULT_REGION": Stack.of(self).region
        #     },
        #     secrets={
        #         "OPENAI_API_KEY": ecs.Secret.from_secrets_manager(
        #             secretsmanager.Secret.from_secret_name_v2(
        #                 self, "OpenAISecret",
        #                 "openai-api-key"
        #             ),
        #             "OPENAI_API_KEY"
        #         )
        #     }
        # )

        # container.add_port_mappings(
        #     ecs.PortMapping(
        #         container_port=8501,
        #         protocol=ecs.Protocol.TCP
        #     )
        # )

        # # Create Fargate Service
        # self.service = ecs_patterns.ApplicationLoadBalancedFargateService(
        #     self, "Service",
        #     cluster=self.cluster,
        #     task_definition=task_definition,
        #     desired_count=1,
        #     certificate=self.certificate,
        #     domain_name="writing.app-dw.net",
        #     domain_zone=self.hosted_zone,
        #     protocol=elbv2.ApplicationProtocol.HTTPS,
        #     public_load_balancer=True,
        #     assign_public_ip=False,
        #     security_groups=[self.service_sg],
        #     task_subnets=ec2.SubnetSelection(
        #         subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
        #     ),
        #     listener_port=443,
        #     target_protocol=elbv2.ApplicationProtocol.HTTP,
        #     health_check=ecs.HealthCheck(
        #         command=["CMD-SHELL", "curl -f http://localhost:8000/healthz || exit 1"],
        #         interval=Duration.seconds(30),
        #         timeout=Duration.seconds(5),
        #         retries=3,
        #         start_period=Duration.seconds(60)
        #     ),
        #     capacity_provider_strategies=[
        #         ecs.CapacityProviderStrategy(
        #             capacity_provider="FARGATE_SPOT",
        #             weight=1
        #         )
        #     ],
        #     circuit_breaker=ecs.DeploymentCircuitBreaker(
        #         rollback=True
        #     ),
        #     min_healthy_percent=100
        # )

        # # Auto Scaling configuration
        # scaling = self.service.service.auto_scale_task_count(
        #     max_capacity=4,
        #     min_capacity=1
        # )

        # self.service.target_group.configure_health_check(
        #     path="/healthz",
        #     healthy_http_codes="200",
        #     interval=Duration.seconds(30),
        #     timeout=Duration.seconds(3),
        #     healthy_threshold_count=2,
        #     unhealthy_threshold_count=3
        # )

        # scaling.scale_on_cpu_utilization(
        #     "CpuScaling",
        #     target_utilization_percent=70,
        #     scale_in_cooldown=Duration.seconds(60),
        #     scale_out_cooldown=Duration.seconds(60)
        # )

        # scaling.scale_on_memory_utilization(
        #     "MemoryScaling",
        #     target_utilization_percent=70,
        #     scale_in_cooldown=Duration.seconds(60),
        #     scale_out_cooldown=Duration.seconds(60)
        # )

        # # Grant permissions to call OpenAI API
        # task_definition.add_to_task_role_policy(
        #     iam.PolicyStatement(
        #         actions=[
        #             "secretsmanager:GetSecretValue"
        #         ],
        #         resources=[
        #             f"arn:aws:secretsmanager:{Stack.of(self).region}:{Stack.of(self).account}:secret:openai-api-key-*"
        #         ]
        #     )
        # )

        # # Outputs
        # CfnOutput(self, "ServiceURL",
        #     value=f"https://writing.app-dw.net",
        #     description="Writing Practice Frontend URL",
        #     export_name=f"{construct_id}-service-url"
        # )

        # CfnOutput(self, "ServiceName",
        #     value=self.service.service.service_name,
        #     description="Writing Practice Frontend Service Name",
        #     export_name=f"{construct_id}-service-name"
        # )

        # CfnOutput(self, "ClusterName",
        #     value=self.cluster.cluster_name,
        #     description="ECS Cluster Name",
        #     export_name=f"{construct_id}-cluster-name"
        # )