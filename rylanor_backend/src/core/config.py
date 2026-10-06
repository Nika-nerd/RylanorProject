from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Rylanor AI Assistant"
    GEMINI_API_KEY: str
    ELEVENLABS_API_KEY: str | None = None
    
    class Config:
        env_file = ".env"

settings = Settings()