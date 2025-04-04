#!/usr/bin/env python3
import os
from aws_cdk import App, Environment
from dotenv import load_dotenv
from stacks.auth_stack import AuthStack
from stacks.database_stack import DatabaseStack
from stacks.haiku_generator.backend_stack import HaikuGeneratorBackendStack
from stacks.haiku_generator.frontend_stack import HaikuGeneratorFrontendStack
from stacks.haiku_generator.pipeline_stack import HaikuGeneratorPipelineStack
from stacks.lang_portal.backend_stack import LangPortalBackendStack
from stacks.lang_portal.frontend_stack import LangPortalFrontendStack
from stacks.lang_portal.certificate_stack import LangPortalCertificateStack
from stacks.lang_portal.pipeline_stack import LangPortalPipelineStack
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
monitoring_stack = MonitoringStack(app, "MonitoringStack", env=env)
database_stack = DatabaseStack(app, "DatabaseStack", vpc=network_stack.vpc, env=env)
auth_stack = AuthStack(app, "AuthStack", env=env)

# Lang Portal stacks
lang_portal_certificate = LangPortalCertificateStack(app, "LangPortalCertificateStack",
    env=env
)

lang_portal_backend = LangPortalBackendStack(app, "LangPortalBackendStack",
    vpc=network_stack.vpc,
    database=database_stack.lang_portal_db,
    user_pool=auth_stack.user_pool,
    certificate=lang_portal_certificate.certificate,
    env=env

)

lang_portal_frontend = LangPortalFrontendStack(app, "LangPortalFrontendStack",
    backend_alb=lang_portal_backend.service.load_balancer,
    certificate=lang_portal_certificate.certificate,
    env=env
)

lang_portal_pipeline = LangPortalPipelineStack(app, "LangPortalPipelineStack",
    bucket=lang_portal_frontend.bucket,
    service=lang_portal_backend.service.service,
    repository=lang_portal_backend.repository,
    user_pool_id=auth_stack.user_pool.user_pool_id,
    user_pool_client_id=auth_stack.lang_portal_client.user_pool_client_id,
    env=env
)

# Haiku Generator stacks
haiku_frontend = HaikuGeneratorFrontendStack(app, "HaikuGeneratorFrontendStack",
    env=env
)

haiku_backend = HaikuGeneratorBackendStack(app, "HaikuGeneratorBackendStack",
    vpc=network_stack.vpc,
    database=database_stack.haiku_db,
    user_pool=auth_stack.user_pool,
    env=env
)

haiku_pipeline = HaikuGeneratorPipelineStack(app, "HaikuGeneratorPipelineStack",
    bucket=haiku_frontend.bucket,
    cluster=haiku_backend.cluster,
    repository=haiku_backend.repository,
    env=env
)

# Vocab Generator stacks
vocab_frontend = VocabGeneratorFrontendStack(app, "VocabGeneratorFrontendStack",
    vpc=network_stack.vpc,
    user_pool=auth_stack.user_pool,
    user_pool_client=auth_stack.vocab_client,
    env=env
)

vocab_backend = VocabGeneratorBackendStack(app, "VocabGeneratorBackendStack",
    vpc=network_stack.vpc,
    database=database_stack.lang_portal_db,
    user_pool=auth_stack.user_pool,
    env=env
)

vocab_pipeline = VocabGeneratorPipelineStack(app, "VocabGeneratorPipelineStack",
    frontend_cluster=vocab_frontend.cluster,
    backend_cluster=vocab_backend.cluster,
    frontend_repository=vocab_frontend.repository,
    backend_repository=vocab_backend.repository,
    env=env
)

# Writing Practice stack
writing_practice = WritingPracticeFrontendStack(app, "WritingPracticeFrontendStack",
    vpc=network_stack.vpc,
    user_pool=auth_stack.user_pool,
    user_pool_client=auth_stack.vocab_client,
    env=env
)

writing_practice_pipeline = WritingPracticePipelineStack(app, "WritingPracticePipelineStack",
    cluster=writing_practice.cluster,
    repository=writing_practice.repository,
    env=env
)

app.synth()