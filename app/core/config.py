import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Secure RAG PoC"
    
    # AWS / LocalStack Config
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = "test"
    AWS_SECRET_ACCESS_KEY: str = "test"
    AWS_ENDPOINT_URL: str = "http://localhost:4566" # LocalStack endpoint
    
    # S3 Config
    S3_BUCKET_NAME: str = "secure-rag-data"
    
    # Qdrant Config
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    
    # OpenAI (Optional for PoC, can use local embeddings)
    OPENAI_API_KEY: str = "sk-..."

    class Config:
        env_file = ".env"

settings = Settings()
