import os 
from typing import List
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application configuration settings."""
    APP_NAME: str = "AI Mock Interview"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT:int = 8000

    MAX_FILE_SIZE:int = 10*1024*1024
    UPLOADS_FOLDER:str = "static/uploads"
    ALLOWED_EXTENSIONS:List = ["pdf", "docs", "doc"]

    GROQ_API_KEY:str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL:str = "openai/gpt-oss-120b"

    MAX_QUESTIONS: int = 15
    MIN_QUESTIONS: int = 5
    INTERVIEW_TIME_LIMIT: int = 45  # minutes
    
    # Database Settings
    DATABASE_URL: str = None
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Create upload directory if it doesn't exist
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)