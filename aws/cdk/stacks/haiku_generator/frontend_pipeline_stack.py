import os
from constructs import Construct
from aws_cdk import (
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_s3 as s3,
    Stack
)

class HaikuGeneratorFrontendPipelineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str,
                 bucket: s3.Bucket,
                 user_pool_id: str,
                 user_pool_client_id: str,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Frontend Pipeline
        frontend_pipeline = codepipeline.Pipeline(
            self, "Pipeline",
            pipeline_name="haiku-generator-frontend",
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
                            "aws/haiku-generator-frontend/*",
                            "aws/haiku-generator-frontend/**/*"
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
                        self, "HaikuGeneratorFrontendBuild",
                        environment_variables={
                            "REACT_APP_BACKEND_URL": codebuild.BuildEnvironmentVariable(
                                value="https://haiku.app-dw.net/api"
                            ),
                            "REACT_APP_COGNITO_AUTHORITY": codebuild.BuildEnvironmentVariable(
                                value=f"https://cognito-idp.{self.region}.amazonaws.com/{user_pool_id}"
                            ),
                            "REACT_APP_COGNITO_CLIENT_ID": codebuild.BuildEnvironmentVariable(
                                value=user_pool_client_id
                            ),
                            "REACT_APP_COGNITO_DOMAIN": codebuild.BuildEnvironmentVariable(
                                value="https://auth.app-dw.net"
                            ),
                            "REACT_APP_REDIRECT_SIGN_IN": codebuild.BuildEnvironmentVariable(
                                value="https://haiku.app-dw.net/auth/callback"
                            ),
                            "REACT_APP_REDIRECT_SIGN_OUT": codebuild.BuildEnvironmentVariable(
                                value="https://haiku.app-dw.net/"
                            )
                        },
                        build_spec=codebuild.BuildSpec.from_object({
                            "version": "0.2",
                            "phases": {
                                "install": {
                                    "commands": [
                                        "cd aws/haiku-generator-frontend",
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
                                "base-directory": "aws/haiku-generator-frontend/build",
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