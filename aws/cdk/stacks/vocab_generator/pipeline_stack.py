from constructs import Construct
from aws_cdk import (
    Stack,
    aws_codebuild as codebuild,
    aws_codecommit as codecommit,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_iam as iam,
    SecretValue,
    aws_ecs as ecs
)

class VocabGeneratorPipelineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Frontend Pipeline
        frontend_pipeline = codepipeline.Pipeline(
            self, "VocabGeneratorFrontendPipeline",
            pipeline_name="vocab-generator-frontend-pipeline"
        )

        # Source stage for frontend
        source_output = codepipeline.Artifact()
        frontend_pipeline.add_stage(
            stage_name="Source",
            actions=[
                codepipeline_actions.GitHubSourceAction(
                    action_name="GitHub_Source",
                    owner="your-github-org",  # Replace with your GitHub org/user
                    repo="free-genai-bootcamp-2025",
                    branch="main",
                    oauth_token=SecretValue.secrets_manager("github-token"),
                    output=source_output,
                    trigger=codepipeline_actions.GitHubTrigger.PUSH,
                    trigger_paths=["aws/vocab-generator-frontend/**/*"]
                )
            ]
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
                        build_spec=codebuild.BuildSpec.from_object({
                            "version": "0.2",
                            "phases": {
                                "install": {
                                    "commands": [
                                        "cd aws/vocab-generator-frontend",
                                        "pip install -r requirements.txt"
                                    ]
                                },
                                "build": {
                                    "commands": [
                                        "pytest",
                                        "docker build -t vocab-generator-frontend ."
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
                        cluster=ecs.Cluster.from_cluster_attributes(
                            self, "ECSCluster",
                            cluster_name="your-cluster-name"  # Replace with your cluster name
                        )
                    ),
                    input=build_output
                )
            ]
        )

        # Backend Pipeline
        backend_pipeline = codepipeline.Pipeline(
            self, "VocabGeneratorBackendPipeline",
            pipeline_name="vocab-generator-backend-pipeline"
        )

        # Source stage for backend
        backend_source_output = codepipeline.Artifact()
        backend_pipeline.add_stage(
            stage_name="Source",
            actions=[
                codepipeline_actions.GitHubSourceAction(
                    action_name="GitHub_Source",
                    owner="your-github-org",  # Replace with your GitHub org/user
                    repo="free-genai-bootcamp-2025",
                    branch="main",
                    oauth_token=SecretValue.secrets_manager("github-token"),
                    output=backend_source_output,
                    trigger=codepipeline_actions.GitHubTrigger.PUSH,
                    trigger_paths=["aws/vocab-generator-backend/**/*"]
                )
            ]
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
                        build_spec=codebuild.BuildSpec.from_object({
                            "version": "0.2",
                            "phases": {
                                "install": {
                                    "commands": [
                                        "cd aws/vocab-generator-backend",
                                        "pip install -r requirements.txt"
                                    ]
                                },
                                "build": {
                                    "commands": [
                                        "pytest",
                                        "docker build -t vocab-generator-backend ."
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
                        cluster=ecs.Cluster.from_cluster_attributes(
                            self, "ECSCluster",
                            cluster_name="your-cluster-name"  # Replace with your cluster name
                        )
                    ),
                    input=backend_build_output
                )
            ]
        )