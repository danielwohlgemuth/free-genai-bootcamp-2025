#!/usr/bin/env python3
import os
from aws_cdk import App, Environment
from stacks.auth_stack import AuthStack
from stacks.database_stack import DatabaseStack
from stacks.haiku_generator.backend_stack import HaikuGeneratorBackendStack
from stacks.haiku_generator.frontend_stack import HaikuGeneratorFrontendStack
from stacks.lang_portal.backend_stack import LangPortalBackendStack
from stacks.lang_portal.frontend_stack import LangPortalFrontendStack
from stacks.monitoring_stack import MonitoringStack
from stacks.network_stack import NetworkStack
from stacks.storage_stack import StorageStack
from stacks.vocab_generator.backend_stack import VocabGeneratorBackendStack
from stacks.vocab_generator.frontend_stack import VocabGeneratorFrontendStack
from stacks.writing_practice.frontend_stack import WritingPracticeFrontendStack

app = App()

env = Environment(
    account=os.getenv('CDK_DEFAULT_ACCOUNT'),
    region=os.getenv('CDK_DEFAULT_REGION', 'us-east-1')
)

# Core infrastructure stacks
network_stack = NetworkStack(app, "NetworkStack", env=env)
database_stack = DatabaseStack(app, "DatabaseStack", vpc=network_stack.vpc, env=env)
auth_stack = AuthStack(app, "AuthStack", env=env)
monitoring_stack = MonitoringStack(app, "MonitoringStack", env=env)
storage_stack = StorageStack(app, "StorageStack", env=env)

# Lang Portal stacks
lang_portal_frontend = LangPortalFrontendStack(app, "LangPortalFrontendStack",
    distribution=storage_stack.lang_portal_distribution,
    env=env
)

lang_portal_backend = LangPortalBackendStack(app, "LangPortalBackendStack",
    vpc=network_stack.vpc,
    database=database_stack.lang_portal_db,
    user_pool=auth_stack.user_pool,
    env=env
)

# Haiku Generator stacks
haiku_frontend = HaikuGeneratorFrontendStack(app, "HaikuGeneratorFrontendStack",
    distribution=storage_stack.haiku_distribution,
    env=env
)

haiku_backend = HaikuGeneratorBackendStack(app, "HaikuGeneratorBackendStack",
    vpc=network_stack.vpc,
    database=database_stack.haiku_db,
    user_pool=auth_stack.user_pool,
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

# Writing Practice stack
writing_practice = WritingPracticeFrontendStack(app, "WritingPracticeFrontendStack",
    vpc=network_stack.vpc,
    user_pool=auth_stack.user_pool,
    user_pool_client=auth_stack.vocab_client,
    env=env
)

app.synth()