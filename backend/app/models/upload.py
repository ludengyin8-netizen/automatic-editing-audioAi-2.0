"""Upload Model"""
from sqlalchemy import Column, String, DateTime, Integer, Float
from datetime import datetime
import uuid

from app.core.database import Base

class Upload(Base):
    """Upload model for tracking uploaded audio files"""
    __tablename__ = "uploads"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # File info
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    file_format = Column(String(10), nullable=False)  # wav, mp3, m4a
    
    # Audio properties
    duration = Column(Float, nullable=True)  # in seconds
    sample_rate = Column(Integer, nullable=True)
    channels = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Upload {self.id} - {self.original_filename}>"
