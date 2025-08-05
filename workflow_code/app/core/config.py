# app/core/config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "qwen3:14b"
    DATABASE_URL: str = "postgresql://postgres:100703@localhost:5432/decathlon"

settings = Settings()

   
    
    
