# backend/app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # SambaNova Cloud
    SAMBANOVA_API_KEY: str
    SAMBANOVA_BASE_URL: str = "https://api.sambanova.ai/v1"
    SAMBANOVA_MODEL_VISION: str = "Llama-4-Maverick-17B-128E-Instruct"
    SAMBANOVA_MODEL_CHAT: str = "Meta-Llama-3.1-8B-Instruct"
    SAMBANOVA_MODEL_EMBEDDING: str = "E5-Mistral-7B-Instruct"
    
    # Service Tuning
    MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.2  # Low for code tasks
    TOP_P: float = 0.1
    
    # Vector Store
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    EMBEDDING_DIM: int = 4096
    
    # Audio (Whisper local or API)
    WHISPER_MODEL: str = "base"  # Local fallback
    AUDIO_CHUNK_SIZE: int = 300  # seconds
    
    # Code Processing
    MAX_FILE_SIZE: int = 1024 * 1024  # 1MB
    SUPPORTED_EXTENSIONS: set = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', 
        '.rs', '.cpp', '.c', '.h', '.rb', '.php', '.swift',
        '.kt', '.scala', '.r', '.m', '.cs', '.json', '.yaml', '.md'
    }
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()