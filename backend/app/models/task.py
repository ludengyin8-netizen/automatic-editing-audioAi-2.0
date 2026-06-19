"""Task Model"""
from sqlalchemy import Column, String, DateTime, Float, JSON, Enum
from sqlalchemy.dialects.sqlite import GUID
from datetime import datetime
import uuid
from enum import Enum as PyEnum

from app.core.database import Base

class TaskStatus(str, PyEnum):
    """Task status enumeration"""
    PENDING = "pending"
    UPLOADING = "uploading"
    ANALYZING = "analyzing"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Task(Base):
    """Task model for tracking audio processing jobs"""
    __tablename__ = "tasks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    upload_id = Column(String(36), nullable=False)
    status = Column(String(20), default=TaskStatus.PENDING)
    
    # Content
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    
    # Processing details
    processing_start = Column(DateTime, nullable=True)
    processing_end = Column(DateTime, nullable=True)
    
    # Results
    output_file_path = Column(String(500), nullable=True)
    edit_log_path = Column(String(500), nullable=True)
    edit_decisions = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Error tracking
    error_message = Column(String(1000), nullable=True)
    
    def __repr__(self):
        return f"<Task {self.id} - {self.status}>"
