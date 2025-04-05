from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Cognito Settings
    COGNITO_REGION: str = Field(..., env="COGNITO_REGION")
    COGNITO_USER_POOL_ID: str = Field(..., env="COGNITO_USER_POOL_ID")
    COGNITO_CLIENT_ID: str = Field(..., env="COGNITO_CLIENT_ID")
    
    # JWT Settings
    JWT_ALGORITHM: str = "RS256"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()