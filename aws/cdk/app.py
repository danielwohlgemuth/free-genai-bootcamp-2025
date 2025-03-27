#!/usr/bin/env python3
import os
from aws_cdk import App, Environment
from stacks.network_stack import NetworkStack
from stacks.database_stack import DatabaseStack
from stacks.auth_stack import AuthStack
from stacks.monitoring_stack import MonitoringStack
from stacks.storage_stack import StorageStack
from stacks.lang_portal.frontend_stack import LangPortalFrontendStack
from stacks.lang_portal.backend_stack import LangPortalBackendStack
from stacks.haiku_generator.frontend_stack import HaikuGeneratorFrontendStack
from stacks.haiku_generator.backend_stack import HaikuGeneratorBackendStack
from stacks.vocab_generator.frontend_stack import VocabGeneratorFrontendStack
from stacks.vocab_generator.backend_stack import VocabGeneratorBackendStack
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
    user_pool=auth_stack.user_pool,
    storage_bucket=storage_stack.lang_portal_bucket,
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
    user_pool=auth_stack.user_pool,
    storage_bucket=storage_stack.haiku_bucket,
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
    env=env
)

app.synth()