from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ecr_assets as ecr_assets,
    aws_elasticloadbalancingv2 as elbv2,
    aws_certificatemanager as acm
)
from constructs import Construct


class BackendService:
    def __init__(self, stack: Stack, vpc: ec2.Vpc, cluster: ecs.Cluster, 
                 service_name: str, source_path: str, port: int = 3000,
                 cpu: int = 512, memory: int = 1024, min_capacity: int = 1):
        
        # Create ECR image
        image = ecr_assets.DockerImageAsset(
            stack, f"{service_name}-image",
            directory=source_path
        )

        # Task Definition
        task_definition = ecs.FargateTaskDefinition(
            stack, f"{service_name}-task-def",
            memory_limit_mib=memory,
            cpu=cpu,
        )

        # Container
        container = task_definition.add_container(
            f"{service_name}-container",
            image=ecs.ContainerImage.from_docker_image_asset(image),
            logging=ecs.LogDriver.aws_logs(stream_prefix=service_name),
            environment={
                "SERVICE_NAME": service_name,
                "NODE_ENV": "production"
            }
        )

        container.add_port_mappings(
            ecs.PortMapping(
                container_port=port,
                protocol=ecs.Protocol.TCP
            )
        )

        # Security Group
        security_group = ec2.SecurityGroup(
            stack, f"{service_name}-sg",
            vpc=vpc,
            description=f"Security group for {service_name}"
        )

        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(port),
            f"Allow inbound traffic for {service_name}"
        )

        # Fargate Service
        self.service = ecs_patterns.ApplicationLoadBalancedFargateService(
            stack, f"{service_name}-service",
            cluster=cluster,
            task_definition=task_definition,
            public_load_balancer=True,
            desired_count=min_capacity,
            security_groups=[security_group],
            assign_public_ip=False,
            listener_port=443,
            protocol=elbv2.ApplicationProtocol.HTTPS,
            certificate=acm.Certificate.from_certificate_arn(
                stack, f"{service_name}-cert",
                certificate_arn="your-certificate-arn"  # Replace with your cert ARN
            )
        )

        # Auto Scaling
        scaling = self.service.service.auto_scale_task_count(
            max_capacity=4,
            min_capacity=min_capacity
        )

        scaling.scale_on_cpu_utilization(
            f"{service_name}-cpu-scaling",
            target_utilization_percent=70,
        )

class MultiBackendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, 
                 shared_infra: SharedInfraStack, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define backend services
        self.services = {
            "haiku-generator": BackendService(
                self, shared_infra.vpc, shared_infra.cluster,
                "haiku-generator",
                "./haiku-generator-backend",
                port=3000
            ),
            "lang-portal": BackendService(
                self, shared_infra.vpc, shared_infra.cluster,
                "lang-portal",
                "./lang-portal-backend",
                port=3001
            ),
            "vocab-generator": BackendService(
                self, shared_infra.vpc, shared_infra.cluster,
                "vocab-generator",
                "./vocab-generator-backend",
                port=3002
            )
        }
