from aws_cdk import App
from stacks.shared_infra import SharedInfraStack
from stacks.multi_backend import MultiBackendStack

app = App()

# Deploy shared infrastructure
shared_infra = SharedInfraStack(app, "SharedInfraStack")

# Deploy backend services
backend_stack = MultiBackendStack(app, "MultiBackendStack", 
                                shared_infra=shared_infra)

app.synth()
