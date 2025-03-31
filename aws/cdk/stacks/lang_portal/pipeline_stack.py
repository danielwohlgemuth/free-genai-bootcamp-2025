import os
from constructs import Construct
from aws_cdk import (
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_ecr as ecr,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_s3 as s3,
    Stack
)

class LangPortalPipelineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str,
                 bucket: s3.Bucket,
                 cluster: ecs.Cluster,
                 repository: ecr.Repository,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Frontend Pipeline
        frontend_pipeline = codepipeline.Pipeline(
            self, "LangPortalFrontendPipeline",
            pipeline_name="lang-portal-frontend-pipeline",
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
                            "aws/lang-portal-frontend/*",
                            "aws/lang-portal-frontend/**/*"
                        ]
                    )
                ]
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
                        self, "LangPortalFrontendBuild",
                        build_spec=codebuild.BuildSpec.from_object({
                            "version": "0.2",
                            "phases": {
                                "install": {
                                    "commands": [
                                        "cd aws/lang-portal-frontend",
                                        "npm install"
                                    ]
                                },
                                "build": {
                                    "commands": [
                                        "npm run build"
                                    ]
                                }
                            },
                            "artifacts": {
                                "base-directory": "aws/lang-portal-frontend/dist",
                                "files": ["**/*"]
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
                codepipeline_actions.S3DeployAction(
                    action_name="Deploy",
                    input=build_output,
                    bucket=bucket
                )
            ]
        )

        # Backend Pipeline
        backend_pipeline = codepipeline.Pipeline(
            self, "LangPortalBackendPipeline",
            pipeline_name="lang-portal-backend-pipeline",
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
                            "aws/lang-portal-backend/*",
                            "aws/lang-portal-backend/**/*"
                        ]
                    )
                ]
            )
        )

        # Create the build role
        build_role = iam.Role(
            self, "LangPortalBackendBuildRole",
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
            description="Role for Lang Portal Backend CodeBuild project"
        )

        # Attach the managed policy
        build_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryReadOnly")
        )

        # Add additional write permissions for your specific repository
        build_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ecr:InitiateLayerUpload",
                    "ecr:UploadLayerPart",
                    "ecr:CompleteLayerUpload",
                    "ecr:PutImage"
                ],
                resources=[repository.repository_arn]
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
                        self, "LangPortalBackendBuild",
                        role=build_role,
                        environment=codebuild.BuildEnvironment(
                            privileged=True
                        ),
                        environment_variables={
                            "ECR_REPOSITORY_URI": codebuild.BuildEnvironmentVariable(
                                value=repository.repository_uri
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
                        self, "LangPortalBackendService",
                        service_name="lang-portal-backend",
                        cluster=cluster
                    ),
                    input=backend_build_output
                )
            ]
        )