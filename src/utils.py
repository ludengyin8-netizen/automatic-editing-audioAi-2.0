"""Utility functions for Audio Director Agent"""

import os
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional
from loguru import logger


def generate_task_id() -> str:
    """Generate a unique task ID"""
    return str(uuid.uuid4())


def generate_file_hash(file_path: Path) -> str:
    """Generate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_file_size(file_path: Path) -> int:
    """Get file size in bytes"""
    return file_path.stat().st_size


def format_duration(seconds: float) -> str:
    """Format duration in seconds to HH:MM:SS format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def get_supported_formats() -> tuple:
    """Get supported audio formats"""
    return (".wav", ".mp3", ".m4a", ".flac")


def validate_audio_format(file_path: Path) -> bool:
    """Validate if file has supported audio format"""
    return file_path.suffix.lower() in get_supported_formats()


def cleanup_temp_files(directory: Path, max_age_hours: int = 24):
    """Clean up temporary files older than max_age_hours"""
    try:
        now = datetime.now()
        for file_path in directory.glob("*"):
            if file_path.is_file():
                file_age = (now - datetime.fromtimestamp(file_path.stat().st_mtime)).total_seconds() / 3600
                if file_age > max_age_hours:
                    file_path.unlink()
                    logger.info(f"Cleaned up temp file: {file_path}")
    except Exception as e:
        logger.error(f"Error cleaning up temp files: {e}")


def format_bytes(bytes_value: int) -> str:
    """Format bytes to human-readable format"""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} TB"


def setup_logger(
    log_file: Optional[Path] = None,
    level: str = "INFO"
):
    """Setup logger with both console and file handlers"""
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(
        lambda msg: print(msg, end=""),
        format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level,
    )
    
    # Add file handler if log_file is provided
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            str(log_file),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=level,
            rotation="500 MB",
            retention="7 days",
        )
    
    return logger
