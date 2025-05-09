#!/usr/bin/env python3
import os
from aws_cdk import App, Environment
from dotenv import load_dotenv
from stacks.auth_stack import AuthStack
from stacks.haiku_generator.backend_stack import HaikuGeneratorBackendStack
from stacks.haiku_generator.backend_pipeline_stack import HaikuGeneratorBackendPipelineStack
from stacks.haiku_generator.certificate_stack import HaikuGeneratorCertificateStack
from stacks.haiku_generator.database_stack import HaikuGeneratorDatabaseStack
from stacks.haiku_generator.frontend_stack import HaikuGeneratorFrontendStack
from stacks.haiku_generator.frontend_pipeline_stack import HaikuGeneratorFrontendPipelineStack
from stacks.lang_portal.backend_pipeline_stack import LangPortalBackendPipelineStack
from stacks.lang_portal.backend_stack import LangPortalBackendStack
from stacks.lang_portal.certificate_stack import LangPortalCertificateStack
from stacks.lang_portal.frontend_pipeline_stack import LangPortalFrontendPipelineStack
from stacks.lang_portal.frontend_stack import LangPortalFrontendStack
from stacks.monitoring_stack import MonitoringStack
from stacks.network_stack import NetworkStack
from stacks.vocab_generator.backend_stack import VocabGeneratorBackendStack
from stacks.vocab_generator.frontend_stack import VocabGeneratorFrontendStack
from stacks.vocab_generator.pipeline_stack import VocabGeneratorPipelineStack
from stacks.writing_practice.frontend_stack import WritingPracticeFrontendStack
from stacks.writing_practice.pipeline_stack import WritingPracticePipelineStack

app = App()

load_dotenv()
env = Environment(
    account=os.getenv('CDK_DEFAULT_ACCOUNT'),
    region=os.getenv('CDK_DEFAULT_REGION', 'us-east-1')
)

# Core infrastructure stacks
network_stack = NetworkStack(app, "NetworkStack", env=env)
# monitoring_stack = MonitoringStack(app, "MonitoringStack", env=env)
auth_stack = AuthStack(app, "AuthStack", env=env)

# Lang Portal stacks
lang_portal_certificate = LangPortalCertificateStack(app, "LangPortalCertificateStack",
    env=env
)

lang_portal_backend = LangPortalBackendStack(app, "LangPortalBackendStack",
    vpc=network_stack.vpc,
    user_pool=auth_stack.user_pool,
    user_pool_client=auth_stack.lang_portal_client,
    certificate=lang_portal_certificate.certificate,
    env=env
)


lang_portal_frontend = LangPortalFrontendStack(app, "LangPortalFrontendStack",
    backend_alb=lang_portal_backend.service.load_balancer,
    certificate=lang_portal_certificate.certificate,
    env=env
)

lang_portal_frontend_pipeline = LangPortalFrontendPipelineStack(app, "LangPortalFrontendPipelineStack",
    bucket=lang_portal_frontend.bucket,
    user_pool_id=auth_stack.user_pool.user_pool_id,
    user_pool_client_id=auth_stack.lang_portal_client.user_pool_client_id,
    env=env
)

lang_portal_backend_pipeline = LangPortalBackendPipelineStack(app, "LangPortalBackendPipelineStack",
    cluster=lang_portal_backend.cluster,
    repository=lang_portal_backend.repository,
    env=env
)

# Haiku Generator stacks
haiku_certificate = HaikuGeneratorCertificateStack(app, "HaikuGeneratorCertificateStack",
    env=env
)

haiku_backend = HaikuGeneratorBackendStack(app, "HaikuGeneratorBackendStack",
    vpc=network_stack.vpc,
    user_pool=auth_stack.user_pool,
    user_pool_client=auth_stack.haiku_client,
    certificate=haiku_certificate.certificate,
    env=env
)

haiku_backend_pipeline = HaikuGeneratorBackendPipelineStack(app, "HaikuGeneratorBackendPipelineStack",
    cluster=haiku_backend.cluster,
    repository=haiku_backend.repository,
    env=env
)

haiku_frontend = HaikuGeneratorFrontendStack(app, "HaikuGeneratorFrontendStack",
    backend_alb=haiku_backend.service.load_balancer,
    certificate=haiku_certificate.certificate,
    env=env
)

haiku_frontend_pipeline = HaikuGeneratorFrontendPipelineStack(app, "HaikuGeneratorFrontendPipelineStack",
    bucket=haiku_frontend.bucket,
    user_pool_id=auth_stack.user_pool.user_pool_id,
    user_pool_client_id=auth_stack.haiku_client.user_pool_client_id,
    env=env
)

# # Vocab Generator stacks
# vocab_frontend = VocabGeneratorFrontendStack(app, "VocabGeneratorFrontendStack",
#     vpc=network_stack.vpc,
#     user_pool=auth_stack.user_pool,
#     user_pool_client=auth_stack.vocab_client,
#     env=env
# )

# vocab_backend = VocabGeneratorBackendStack(app, "VocabGeneratorBackendStack",
#     vpc=network_stack.vpc,
#     database=lang_portal_database.db,
#     user_pool=auth_stack.user_pool,
#     env=env
# )

# vocab_pipeline = VocabGeneratorPipelineStack(app, "VocabGeneratorPipelineStack",
#     frontend_cluster=vocab_frontend.cluster,
#     backend_cluster=vocab_backend.cluster,
#     frontend_repository=vocab_frontend.repository,
#     backend_repository=vocab_backend.repository,
#     env=env
# )

# # Writing Practice stack
# writing_practice = WritingPracticeFrontendStack(app, "WritingPracticeFrontendStack",
#     vpc=network_stack.vpc,
#     user_pool=auth_stack.user_pool,
#     user_pool_client=auth_stack.vocab_client,
#     env=env
# )

# writing_practice_pipeline = WritingPracticePipelineStack(app, "WritingPracticePipelineStack",
#     cluster=writing_practice.cluster,
#     repository=writing_practice.repository,
#     env=env
# )

app.synth()