import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "影视素材库"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Security
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # Media
    MEDIA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "media")
    THUMB_SIZE: int = 300  # Thumbnail width
    
    # File size limits (in bytes)
    MAX_FILE_SIZE: int = 500 * 1024 * 1024  # 500MB
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 