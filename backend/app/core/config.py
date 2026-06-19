"""Application Configuration"""
from pydantic_settings import BaseSettings
from pathlib import Path
import yaml
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # Project paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    BACKEND_DIR: Path = BASE_DIR / "backend"
    DATA_DIR: Path = BASE_DIR / "data"
    UPLOAD_DIR: Path = DATA_DIR / "uploads"
    TEMP_DIR: Path = DATA_DIR / "temp"
    CACHE_DIR: Path = DATA_DIR / "cache"
    LOG_DIR: Path = BASE_DIR / "logs"
    
    # API settings
    API_TITLE: str = "VoiceFlow-CN API"
    API_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./voiceflow.db"
    
    # File upload
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024  # 500 MB
    ALLOWED_AUDIO_FORMATS: list = ["wav", "mp3", "m4a"]
    
    # Audio processing
    SAMPLE_RATE: int = 16000
    NOISE_REDUCTION_DB: float = 4.0
    DEESSER_STRENGTH: float = 2.0
    TARGET_LUFS: float = -16.0
    COMPRESSOR_RATIO: float = 1.8
    CROSSFADE_MS: int = 25
    
    # DSP parameters
    HIGHPASS_FREQ: int = 70
    HIGHPASS_ORDER: int = 12
    
    # Content analysis
    PAUSE_THRESHOLD: float = 0.8
    PAUSE_TARGET: float = 0.65
    REPETITION_WINDOW: int = 15
    REPETITION_THRESHOLD: float = 0.95
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def __init__(self, **data):
        super().__init__(**data)
        # Create necessary directories
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.TEMP_DIR.mkdir(parents=True, exist_ok=True)
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    def load_config_file(self, config_path: Optional[str] = None):
        """Load configuration from YAML file"""
        if config_path is None:
            config_path = self.BACKEND_DIR / "config.yaml"
        
        if Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
                for key, value in config_data.items():
                    if hasattr(self, key.upper()):
                        setattr(self, key.upper(), value)

settings = Settings()
