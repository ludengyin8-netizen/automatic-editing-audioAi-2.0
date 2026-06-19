"""API Routes"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from loguru import logger
import os
from pathlib import Path

from app.core.database import get_db
from app.core.config import settings
from app.models.upload import Upload
from app.models.task import Task, TaskStatus
from app.core.file_handler import save_upload_file, get_audio_properties

router = APIRouter(prefix="/api", tags=["api"])

@router.post("/upload")
async def upload_audio(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload audio file
    
    Supported formats: .wav, .mp3, .m4a
    """
    try:
        # Validate file format
        file_ext = Path(file.filename).suffix.lower().lstrip('.')
        if file_ext not in settings.ALLOWED_AUDIO_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Supported: {', '.join(settings.ALLOWED_AUDIO_FORMATS)}"
            )
        
        # Save file
        saved_path, filename = await save_upload_file(file)
        
        # Get audio properties
        duration, sample_rate, channels = get_audio_properties(saved_path)
        
        # Create upload record
        upload = Upload(
            filename=filename,
            original_filename=file.filename,
            file_path=str(saved_path),
            file_size=os.path.getsize(saved_path),
            file_format=file_ext,
            duration=duration,
            sample_rate=sample_rate,
            channels=channels,
        )
        
        db.add(upload)
        db.commit()
        db.refresh(upload)
        
        logger.info(f"File uploaded: {upload.id} - {file.filename}")
        
        return {
            "upload_id": upload.id,
            "filename": upload.original_filename,
            "file_size": upload.file_size,
            "duration": upload.duration,
            "sample_rate": upload.sample_rate,
            "channels": upload.channels,
        }
    
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process")
async def process_audio(
    upload_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Start audio processing
    """
    try:
        # Get upload
        upload = db.query(Upload).filter(Upload.id == upload_id).first()
        if not upload:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        # Create task
        task = Task(
            upload_id=upload_id,
            original_filename=upload.original_filename,
            file_path=upload.file_path,
            status=TaskStatus.PENDING,
        )
        
        db.add(task)
        db.commit()
        db.refresh(task)
        
        logger.info(f"Processing started: {task.id}")
        
        return {
            "task_id": task.id,
            "status": task.status,
            "message": "Processing queued",
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Process failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{task_id}")
async def get_status(
    task_id: str,
    db: Session = Depends(get_db),
):
    """
    Get task status
    """
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {
            "task_id": task.id,
            "status": task.status,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "error_message": task.error_message,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/result/{task_id}")
async def get_result(
    task_id: str,
    db: Session = Depends(get_db),
):
    """
    Get task result
    """
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if task.status != TaskStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail=f"Task not completed. Current status: {task.status}"
            )
        
        return {
            "task_id": task.id,
            "output_file": task.output_file_path,
            "edit_log": task.edit_log_path,
            "edit_decisions": task.edit_decisions,
            "completed_at": task.processing_end,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Result retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
