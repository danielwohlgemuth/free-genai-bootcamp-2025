import os
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_ecs as ecs
)

class WritingPracticePipelineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, cluster: ecs.Cluster, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Frontend Pipeline
        frontend_pipeline = codepipeline.Pipeline(
            self, "WritingPracticePipeline",
            pipeline_name="writing-practice-pipeline"
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

        # Build stage for frontend
        build_output = codepipeline.Artifact()
        frontend_pipeline.add_stage(
            stage_name="Build",
            actions=[
                codepipeline_actions.CodeBuildAction(
                    action_name="Build",
                    project=codebuild.PipelineProject(
                        self, "WritingPracticeBuild",
                        build_spec=codebuild.BuildSpec.from_object({
                            "version": "0.2",
                            "phases": {
                                "install": {
                                    "commands": [
                                        "cd aws/writing-practice-frontend",
                                        "pip install -r requirements.txt"
                                    ]
                                },
                                "build": {
                                    "commands": [
                                        "pytest",
                                        "docker build -t writing-practice ."
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