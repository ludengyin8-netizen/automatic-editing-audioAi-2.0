"""ASR Engine API Routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from loguru import logger
from pathlib import Path
import json

from app.core.database import get_db
from app.core.config import settings
from app.core.asr_engine import ASREngine
from app.core.text_parser import TextParser
from app.models.task import Task, TaskStatus
from app.models.upload import Upload

router = APIRouter(prefix="/api/asr", tags=["asr"])

_asr_engine = None
_text_parser = None

def get_asr_engine():
    """Get or initialize ASR engine"""
    global _asr_engine
    if _asr_engine is None:
        _asr_engine = ASREngine(model_size="base")
    return _asr_engine

def get_text_parser():
    """Get or initialize text parser"""
    global _text_parser
    if _text_parser is None:
        _text_parser = TextParser()
    return _text_parser

@router.post("/transcribe/{upload_id}")
async def transcribe_audio(
    upload_id: str,
    language: str = "zh",
    db: Session = Depends(get_db),
):
    """
    Transcribe audio file and extract word-level timestamps
    
    Args:
        upload_id: Upload file ID
        language: Language code (default: zh for Chinese)
    
    Returns:
        Transcription result with word timeline
    """
    try:
        upload = db.query(Upload).filter(Upload.id == upload_id).first()
        if not upload:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        if not Path(upload.file_path).exists():
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        asr_engine = get_asr_engine()
        
        logger.info(f"Starting transcription for upload: {upload_id}")
        
        result = asr_engine.transcribe(
            upload.file_path,
            language=language,
        )
        
        word_timeline = asr_engine.get_word_timeline(result)
        
        transcription_dir = settings.CACHE_DIR / "transcriptions"
        transcription_dir.mkdir(parents=True, exist_ok=True)
        transcription_path = transcription_dir / f"{upload_id}_transcription.json"
        
        asr_engine.save_transcription(result, str(transcription_path))
        
        logger.info(f"Transcription completed for {upload_id}")
        
        return {
            "upload_id": upload_id,
            "text": result["text"],
            "language": result["language"],
            "language_probability": result["language_probability"],
            "duration": result["duration"],
            "word_count": len(word_timeline),
            "segment_count": len(result["segments"]),
            "word_timeline_sample": word_timeline[:20],
            "transcription_file": str(transcription_path),
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/parse/{upload_id}")
async def parse_text(
    upload_id: str,
    db: Session = Depends(get_db),
):
    """
    Parse transcription and segment into sentences
    
    Args:
        upload_id: Upload file ID
    
    Returns:
        Segmented sentences with word-level alignment
    """
    try:
        transcription_dir = settings.CACHE_DIR / "transcriptions"
        transcription_path = transcription_dir / f"{upload_id}_transcription.json"
        
        if not transcription_path.exists():
            raise HTTPException(status_code=404, detail="Transcription not found. Please transcribe first.")
        
        with open(transcription_path, "r", encoding="utf-8") as f:
            transcription = json.load(f)
        
        text_parser = get_text_parser()
        
        logger.info(f"Starting text parsing for upload: {upload_id}")
        
        sentences = text_parser.segment_sentences(transcription["text"])
        
        aligned_sentences = text_parser.align_words_to_sentences(
            transcription["words"],
            sentences,
        )
        
        parsing_dir = settings.CACHE_DIR / "parsing"
        parsing_dir.mkdir(parents=True, exist_ok=True)
        parsing_path = parsing_dir / f"{upload_id}_parsing.json"
        
        with open(parsing_path, "w", encoding="utf-8") as f:
            json.dump({
                "upload_id": upload_id,
                "sentences": aligned_sentences,
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Text parsing completed for {upload_id}")
        
        return {
            "upload_id": upload_id,
            "sentence_count": len(aligned_sentences),
            "sentences": aligned_sentences,
            "parsing_file": str(parsing_path),
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text parsing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transcription/{upload_id}")
async def get_transcription(
    upload_id: str,
    db: Session = Depends(get_db),
):
    """
    Get full transcription details
    """
    try:
        transcription_dir = settings.CACHE_DIR / "transcriptions"
        transcription_path = transcription_dir / f"{upload_id}_transcription.json"
        
        if not transcription_path.exists():
            raise HTTPException(status_code=404, detail="Transcription not found")
        
        with open(transcription_path, "r", encoding="utf-8") as f:
            transcription = json.load(f)
        
        return transcription
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get transcription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
