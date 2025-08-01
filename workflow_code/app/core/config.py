# app/core/config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "qwen3:14b"
        # YENİ EKLEDİĞİMİZ VERİTABANI AYARI
    # postgresql://kullanici:sifre@host:port/veritabani_adi
    DATABASE_URL: str = "postgresql://postgres:1857@localhost:5432/decathlon_db"

settings = Settings()

   
    
    
