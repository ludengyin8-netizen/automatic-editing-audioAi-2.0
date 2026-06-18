"""Configuration management for Audio Director Agent"""

from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # FastAPI
    FAST_API_HOST: str = "0.0.0.0"
    FAST_API_PORT: int = 8000
    FAST_API_WORKERS: int = 4
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/audio_director"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_QUEUE_NAME: str = "audio_processing_queue"

    # Whisper Configuration
    WHISPER_MODEL: str = "large-v3"
    WHISPER_DEVICE: str = "cuda"  # cuda or cpu
    WHISPER_COMPUTE_TYPE: str = "float16"
    WHISPER_LANGUAGE: str = "zh"

    # LLM API Keys
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None

    # Audio Processing
    DEFAULT_SAMPLE_RATE: int = 16000
    MAX_AUDIO_DURATION: int = 3600  # seconds
    AUDIO_OUTPUT_FORMAT: str = "wav"
    AUDIO_OUTPUT_BITRATE: str = "128k"

    # Processing Strategy
    DEFAULT_EDIT_STRATEGY: str = "natural"  # natural, aggressive, minimal
    MIN_SILENCE_DURATION: float = 0.3  # seconds
    MAX_EDIT_RATIO: float = 0.15  # maximum 15% of content can be edited

    # File Storage
    UPLOAD_DIR: Path = Path("./uploads")
    OUTPUT_DIR: Path = Path("./outputs")
    MAX_FILE_SIZE: int = 500 * 1024 * 1024  # 500MB

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Path = Path("./logs/audio_director.log")

    # Performance
    WORKERS: int = 4
    THREADS_PER_WORKER: int = 2
    GPU_ENABLED: bool = True

    # DSP Settings
    DSP_NOISE_REDUCTION: float = 4.0  # dB
    DSP_HIGHPASS_FREQ: int = 70  # Hz
    DSP_COMPRESSION_RATIO: float = 1.8
    DSP_SIBILANCE_FREQ_MIN: int = 5000  # Hz
    DSP_SIBILANCE_FREQ_MAX: int = 8000  # Hz
    DSP_TARGET_LUFS: float = -16.0
    DSP_TRUE_PEAK_MAX: float = -1.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def create_directories(self):
        """Create necessary directories if they don't exist"""
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
settings.create_directories()
