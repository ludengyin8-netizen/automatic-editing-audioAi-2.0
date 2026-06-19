"""File handling utilities"""
from fastapi import UploadFile
from pathlib import Path
from loguru import logger
import shutil
import uuid
import librosa

from app.core.config import settings

async def save_upload_file(file: UploadFile) -> tuple[Path, str]:
    """
    Save uploaded file to disk
    
    Returns:
        Tuple of (file_path, filename)
    """
    try:
        # Generate unique filename
        file_ext = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = settings.UPLOAD_DIR / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File saved: {file_path}")
        return file_path, unique_filename
    
    except Exception as e:
        logger.error(f"Failed to save file: {str(e)}")
        raise

def get_audio_properties(file_path: str) -> tuple[float, int, int]:
    """
    Get audio file properties
    
    Returns:
        Tuple of (duration, sample_rate, channels)
    """
    try:
        y, sr = librosa.load(file_path, sr=None, mono=False)
        duration = librosa.get_duration(y=y, sr=sr)
        
        # Get number of channels
        if len(y.shape) == 1:
            channels = 1
        else:
            channels = y.shape[0]
        
        logger.info(f"Audio properties - Duration: {duration}s, SR: {sr}Hz, Channels: {channels}")
        return duration, sr, channels
    
    except Exception as e:
        logger.error(f"Failed to get audio properties: {str(e)}")
        raise
