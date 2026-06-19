"""ASR Engine for extracting word-level timestamps"""
from faster_whisper import WhisperModel
from loguru import logger
from pathlib import Path
from typing import List, Dict, Any
import json

from app.core.config import settings

class ASREngine:
    """Faster Whisper-based ASR engine for Chinese audio"""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize ASR Engine
        
        Args:
            model_size: Model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.model = None
        self.device = "auto"
        self.compute_type = "float32"
        
        logger.info(f"Initializing ASR Engine with model: {model_size}")
        self._load_model()
    
    def _load_model(self):
        """Load Faster Whisper model"""
        try:
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
            )
            logger.info("ASR model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load ASR model: {str(e)}")
            raise
    
    def transcribe(
        self,
        audio_path: str,
        language: str = "zh",
        beam_size: int = 5,
    ) -> Dict[str, Any]:
        """
        Transcribe audio and extract word-level timestamps
        
        Args:
            audio_path: Path to audio file
            language: Language code (default: zh for Chinese)
            beam_size: Beam size for decoding
        
        Returns:
            Dictionary with transcription and word-level timestamps
        """
        try:
            logger.info(f"Starting transcription: {audio_path}")
            
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                beam_size=beam_size,
                word_level=True,
            )
            
            segments_list = list(segments)
            
            result = {
                "text": "",
                "language": info.language,
                "language_probability": info.language_probability,
                "duration": info.duration,
                "segments": [],
                "words": [],
            }
            
            word_id = 0
            
            for segment in segments_list:
                segment_data = {
                    "id": segment.id,
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text,
                    "words": [],
                }
                
                if hasattr(segment, "words") and segment.words:
                    for word in segment.words:
                        word_data = {
                            "id": word_id,
                            "word": word.word,
                            "start": word.start,
                            "end": word.end,
                            "probability": word.probability,
                        }
                        segment_data["words"].append(word_data)
                        result["words"].append(word_data)
                        word_id += 1
                
                result["segments"].append(segment_data)
                result["text"] += segment.text + " "
            
            result["text"] = result["text"].strip()
            
            logger.info(f"Transcription completed. Total words: {len(result['words'])}")
            return result
        
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            raise
    
    def get_word_timeline(self, transcription_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract word timeline from transcription result
        
        Returns:
            List of word timeline entries
        """
        try:
            timeline = []
            for word in transcription_result["words"]:
                timeline.append({
                    "id": word["id"],
                    "word": word["word"],
                    "start": round(word["start"], 3),
                    "end": round(word["end"], 3),
                    "probability": round(word["probability"], 3),
                })
            
            logger.info(f"Word timeline extracted: {len(timeline)} words")
            return timeline
        
        except Exception as e:
            logger.error(f"Failed to extract word timeline: {str(e)}")
            raise
    
    def save_transcription(self, result: Dict[str, Any], output_path: str):
        """
        Save transcription result to JSON file
        
        Args:
            result: Transcription result
            output_path: Path to save JSON file
        """
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Transcription saved to {output_path}")
        
        except Exception as e:
            logger.error(f"Failed to save transcription: {str(e)}")
            raise
