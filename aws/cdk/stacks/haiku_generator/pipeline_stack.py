from constructs import Construct
from aws_cdk import (
    Stack,
    aws_codebuild as codebuild,
    aws_codecommit as codecommit,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_iam as iam,
    SecretValue,
    aws_ecs as ecs,
    aws_s3 as s3
)

class HaikuGeneratorPipelineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Frontend Pipeline
        frontend_pipeline = codepipeline.Pipeline(
            self, "HaikuGeneratorFrontendPipeline",
            pipeline_name="haiku-generator-frontend-pipeline"
        )

        # Source stage for frontend
        source_output = codepipeline.Artifact()
        frontend_pipeline.add_stage(
            stage_name="Source",
            actions=[
                codepipeline_actions.GitHubSourceAction(
                    action_name="GitHub_Source",
                    owner="your-github-org",  # Replace with your GitHub org/user
                    repo="haiku-generator-frontend",
                    branch="main",
                    oauth_token=SecretValue.secrets_manager("github-token"),
                    output=source_output
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
                        self, "HaikuGeneratorFrontendBuild",
                        build_spec=codebuild.BuildSpec.from_object({
                            "version": "0.2",
                            "phases": {
                                "install": {
                                    "commands": [
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
                                "base-directory": "build",
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
                    bucket=s3.Bucket.from_bucket_name(
                        self, "HaikuGeneratorFrontendBucket",
                        "your-frontend-bucket-name"  # Replace with your bucket name
                    )
                )
            ]
        )

        # Backend Pipeline
        backend_pipeline = codepipeline.Pipeline(
            self, "HaikuGeneratorBackendPipeline",
            pipeline_name="haiku-generator-backend-pipeline"
        )

        # Source stage for backend
        backend_source_output = codepipeline.Artifact()
        backend_pipeline.add_stage(
            stage_name="Source",
            actions=[
                codepipeline_actions.GitHubSourceAction(
                    action_name="GitHub_Source",
                    owner="your-github-org",  # Replace with your GitHub org/user
                    repo="haiku-generator-backend",
                    branch="main",
                    oauth_token=SecretValue.secrets_manager("github-token"),
                    output=backend_source_output
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
                        self, "HaikuGeneratorBackendBuild",
                        build_spec=codebuild.BuildSpec.from_object({
                            "version": "0.2",
                            "phases": {
                                "pre_build": {
                                    "commands": [
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
                        self, "HaikuGeneratorBackendService",
                        service_name="haiku-generator-backend",  # Replace with your service name
                        cluster=ecs.Cluster.from_cluster_attributes(
                            self, "ECSCluster",
                            cluster_name="your-cluster-name"  # Replace with your cluster name
                        )
                    ),
                    input=backend_build_output
                )
            ]
        )