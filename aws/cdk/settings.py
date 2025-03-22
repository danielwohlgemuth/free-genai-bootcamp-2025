from typing import NamedTuple
from enum import Enum

class AppType(Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"

class AppConfig(NamedTuple):
    type: AppType
    source_path: str
    subdomain: str
    api_path: str = None  # Only for backend apps

# Root domain configuration
ROOT_DOMAIN = "app-dw.net"
AUTH_SUBDOMAIN = "auth"

# Application configurations
APPLICATIONS = {
    "haiku-generator": {
        "frontend": AppConfig(
            type=AppType.FRONTEND,
            source_path="aws/haiku-generator-frontend",
            subdomain="haiku"
        ),
        "backend": AppConfig(
            type=AppType.BACKEND,
            source_path="aws/haiku-generator-backend",
            subdomain="haiku",
            api_path="/api"
        )
    },
    "lang-portal": {
        "frontend": AppConfig(
            type=AppType.FRONTEND,
            source_path="aws/lang-portal-frontend",
            subdomain="lang-portal"
        ),
        "backend": AppConfig(
            type=AppType.BACKEND,
            source_path="aws/lang-portal-backend",
            subdomain="lang-portal",
            api_path="/api"
        )
    },
    "vocab-generator": {
        "frontend": AppConfig(
            type=AppType.FRONTEND,
            source_path="aws/vocab-generator-frontend",
            subdomain="vocab"
        ),
        "backend": AppConfig(
            type=AppType.BACKEND,
            source_path="aws/vocab-generator-backend",
            subdomain="vocab",
            api_path="/api"
        )
    },
    "writing-practice": {
        "frontend": AppConfig(
            type=AppType.FRONTEND,
            source_path="aws/writing-practice-frontend",
            subdomain="writing"
        )
    }
}

# Stack naming convention
def get_stack_name(app_name: str, stack_type: str, env: str = "prod") -> str:
    return f"{app_name}-{stack_type}-{env}"

# Common tags for all resources
DEFAULT_TAGS = {
    "Project": "language-apps",
    "ManagedBy": "CDK"
}

# Environment settings
class Environment:
    PROD = "prod"
    DEV = "dev"
