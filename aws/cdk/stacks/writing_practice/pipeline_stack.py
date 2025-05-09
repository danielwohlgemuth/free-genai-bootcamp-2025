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

class WritingPracticePipelineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str,
                 cluster: ecs.Cluster,
                 repository: ecr.Repository,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Frontend Pipeline
        frontend_pipeline = codepipeline.Pipeline(
            self, "WritingPracticePipeline",
            pipeline_name="writing-practice-pipeline",
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
                            "aws/writing-practice-frontend/*",
                            "aws/writing-practice-frontend/**/*"
                        ]
                    )
                ]
            )
        )

        # Create the build role
        build_role = iam.Role(
            self, "WritingPracticeBuildRole",
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
            description="Role for Writing Practice CodeBuild project"
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

        # Build stage for frontend
        build_output = codepipeline.Artifact()
        frontend_pipeline.add_stage(
            stage_name="Build",
            actions=[
                codepipeline_actions.CodeBuildAction(
                    action_name="Build",
                    project=codebuild.PipelineProject(
                        self, "WritingPracticeBuild",
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
                                        "cd aws/writing-practice-frontend",
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
                        self, "WritingPracticeService",
                        service_name="writing-practice",  # Must match service name in ECS
                        cluster=cluster
                    ),
                    input=build_output
                )
            ]
        )