"""Application configuration."""
from pydantic_settings import BaseSettings
from typing import List
import sys


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # MongoDB
    mongodb_uri: str
    
    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # OpenAI
    openai_api_key: str
    
    # CORS
    cors_origins: str = "http://localhost:5173"
    
    # App
    app_env: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


def load_settings() -> Settings:
    """Load settings with validation and fail-fast on missing required vars."""
    try:
        return Settings()
    except Exception as e:
        print(f"❌ CONFIGURATION ERROR: {e}")
        print("\n📋 Required environment variables:")
        print("  - MONGODB_URI")
        print("  - JWT_SECRET")
        print("  - OPENAI_API_KEY")
        print("\n💡 Copy .env.example to .env and fill in your values")
        sys.exit(1)


settings = load_settings()
