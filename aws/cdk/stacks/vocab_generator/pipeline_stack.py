import os
from constructs import Construct
from aws_cdk import (
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_iam as iam,
    aws_ecr as ecr,
    aws_ecs as ecs,
    Stack
)

class VocabGeneratorPipelineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str,
                 frontend_cluster: ecs.Cluster,
                 backend_cluster: ecs.Cluster,
                 frontend_repository: ecr.Repository,
                 backend_repository: ecr.Repository,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Frontend Pipeline
        frontend_pipeline = codepipeline.Pipeline(
            self, "VocabGeneratorFrontendPipeline",
            pipeline_name="vocab-generator-frontend-pipeline",
            pipeline_type=codepipeline.PipelineType.V2
        )

        # Source stage for frontend
        source_output = codepipeline.Artifact()
        frontend_pipeline.add_stage(
            stage_name="Source",
            actions=[
                codepipeline_actions.CodeStarConnectionsSourceAction(
                    action_name="GitHub_Source",
                    owner="danielwohlgemuth",
                    repo="free-genai-bootcamp-2025",
                    branch="main",
                    output=source_output,
                    connection_arn=os.getenv("GITHUB_CONNECTION_ARN")
                )
            ]
        )

        # Trigger for frontend
        frontend_pipeline.add_trigger(
            provider_type=codepipeline.ProviderType.CODE_STAR_SOURCE_CONNECTION,
            git_configuration=codepipeline.GitConfiguration(
                source_action=frontend_pipeline.stages[0].actions[0],
                push_filter=[
                    codepipeline.GitPushFilter(
                        branches_includes=["main"],
                        file_paths_includes=[
                            "aws/vocab-generator-frontend/*",
                            "aws/vocab-generator-frontend/**/*"
                        ]
                    )
                ]
            )
        )

        # Create the build role
        frontend_build_role = iam.Role(
            self, "VocabGeneratorFrontendBuildRole",
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
            description="Role for Vocab Generator Frontend CodeBuild project"
        )

        # Attach the managed policy
        frontend_build_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryReadOnly")
        )

        # Add additional write permissions for your specific repository
        frontend_build_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ecr:InitiateLayerUpload",
                    "ecr:UploadLayerPart",
                    "ecr:CompleteLayerUpload",
                    "ecr:PutImage"
                ],
                resources=[frontend_repository.repository_arn]
            )
        )

        # Build stage for frontend
        build_output = codepipeline.Artifact()
        frontend_pipeline.add_stage(
            stage_name="Build",
            actions=[
                codepipeline_actions.CodeBuildAction(
                    action_name="Build",
                    project=codebuild.PipelineProject(
                        self, "VocabGeneratorFrontendBuild",
                        role=frontend_build_role,
                        environment=codebuild.BuildEnvironment(
                            privileged=True
                        ),
                        environment_variables={
                            "ECR_REPOSITORY_URI": codebuild.BuildEnvironmentVariable(
                                value=frontend_repository.repository_uri
                            ),
                            "AWS_DEFAULT_REGION": codebuild.BuildEnvironmentVariable(
                                value=Stack.of(self).region
                            )
                        },
                        build_spec=codebuild.BuildSpec.from_object({
                            "version": "0.2",
                            "phases": {
                                "pre_build": {
                                    "commands": [
                                        "cd aws/vocab-generator-frontend",
                                        "aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $ECR_REPOSITORY_URI"
                                    ]
                                },
                                "build": {
                                    "commands": [
                                        "docker build -t $ECR_REPOSITORY_URI:$CODEBUILD_RESOLVED_SOURCE_VERSION .",
                                        "docker tag $ECR_REPOSITORY_URI:$CODEBUILD_RESOLVED_SOURCE_VERSION $ECR_REPOSITORY_URI:latest"
                                    ]
                                },
                                "post_build": {
                                    "commands": [
                                        "docker push $ECR_REPOSITORY_URI:$CODEBUILD_RESOLVED_SOURCE_VERSION",
                                        "docker push $ECR_REPOSITORY_URI:latest"
                                    ]
                                }
                            }
                        })
                    ),
                    input=source_output,
                    outputs=[build_output]
                )
            ]
        )

        # Deploy stage for frontend
        frontend_pipeline.add_stage(
            stage_name="Deploy",
            actions=[
                codepipeline_actions.EcsDeployAction(
                    action_name="Deploy",
                    service=ecs.FargateService.from_fargate_service_attributes(
                        self, "VocabGeneratorFrontendService",
                        service_name="vocab-frontend",  # Must match service name in ECS
                        cluster=frontend_cluster
                    ),
                    input=build_output
                )
            ]
        )

        # Backend Pipeline
        backend_pipeline = codepipeline.Pipeline(
            self, "VocabGeneratorBackendPipeline",
            pipeline_name="vocab-generator-backend-pipeline",
            pipeline_type=codepipeline.PipelineType.V2
        )

        # Source stage for backend
        backend_source_output = codepipeline.Artifact()
        backend_pipeline.add_stage(
            stage_name="Source",
            actions=[
                codepipeline_actions.CodeStarConnectionsSourceAction(
                    action_name="GitHub_Source",
                    owner="danielwohlgemuth",
                    repo="free-genai-bootcamp-2025",
                    branch="main",
                    output=backend_source_output,
                    connection_arn=os.getenv("GITHUB_CONNECTION_ARN")
                )
            ]
        )

        # Trigger for backend
        backend_pipeline.add_trigger(
            provider_type=codepipeline.ProviderType.CODE_STAR_SOURCE_CONNECTION,
            git_configuration=codepipeline.GitConfiguration(
                source_action=backend_pipeline.stages[0].actions[0],
                push_filter=[
                    codepipeline.GitPushFilter(
                        branches_includes=["main"],
                        file_paths_includes=[
                            "aws/vocab-generator-backend/*",
                            "aws/vocab-generator-backend/**/*"
                        ]
                    )
                ]
            )
        )

        # Create the build role
        backend_build_role = iam.Role(
            self, "VocabGeneratorBackendBuildRole",
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
            description="Role for Vocab Generator Backend CodeBuild project"
        )

        # Attach the managed policy
        backend_build_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryReadOnly")
        )

        # Add additional write permissions for your specific repository
        backend_build_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ecr:InitiateLayerUpload",
                    "ecr:UploadLayerPart",
                    "ecr:CompleteLayerUpload",
                    "ecr:PutImage"
                ],
                resources=[backend_repository.repository_arn]
            )
        )

        # Build stage for backend
        backend_build_output = codepipeline.Artifact()
        backend_pipeline.add_stage(
            stage_name="Build",
            actions=[
                codepipeline_actions.CodeBuildAction(
                    action_name="Build",
                    project=codebuild.PipelineProject(
                        self, "VocabGeneratorBackendBuild",
                        role=backend_build_role,
                        environment=codebuild.BuildEnvironment(
                            privileged=True
                        ),
                        environment_variables={
                            "ECR_REPOSITORY_URI": codebuild.BuildEnvironmentVariable(
                                value=backend_repository.repository_uri
                            ),
                            "AWS_DEFAULT_REGION": codebuild.BuildEnvironmentVariable(
                                value=Stack.of(self).region
                            )
                        },
                        build_spec=codebuild.BuildSpec.from_object({
                            "version": "0.2",
                            "phases": {
                                "pre_build": {
                                    "commands": [
                                        "cd aws/lang-portal-backend",
                                        "aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $ECR_REPOSITORY_URI"
                                    ]
                                },
                                "build": {
                                    "commands": [
                                        "docker build -t $ECR_REPOSITORY_URI:$CODEBUILD_RESOLVED_SOURCE_VERSION .",
                                        "docker tag $ECR_REPOSITORY_URI:$CODEBUILD_RESOLVED_SOURCE_VERSION $ECR_REPOSITORY_URI:latest"
                                    ]
                                },
                                "post_build": {
                                    "commands": [
                                        "docker push $ECR_REPOSITORY_URI:$CODEBUILD_RESOLVED_SOURCE_VERSION",
                                        "docker push $ECR_REPOSITORY_URI:latest"
                                    ]
                                }
                            }
                        })
                    ),
                    input=backend_source_output,
                    outputs=[backend_build_output]
                )
            ]
        )

        # Deploy stage for backend
        backend_pipeline.add_stage(
            stage_name="Deploy",
            actions=[
                codepipeline_actions.EcsDeployAction(
                    action_name="Deploy",
                    service=ecs.FargateService.from_fargate_service_attributes(
                        self, "VocabGeneratorBackendService",
                        service_name="vocab-backend",  # Must match service name in ECS
                        cluster=backend_cluster
                    ),
                    input=backend_build_output
                )
            ]
        )