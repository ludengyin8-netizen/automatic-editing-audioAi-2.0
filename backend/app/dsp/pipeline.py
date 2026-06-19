"""DSP Pipeline - Main DSP Chain"""
from typing import Dict, Any
from loguru import logger
import numpy as np
from pathlib import Path
import json

from app.dsp.highpass_filter import HighPassFilter
from app.dsp.noise_reducer import NoiseReducer
from app.dsp.deesser import DeEsser
from app.dsp.compressor import DynamicCompressor
from app.dsp.limiter import Limiter
from app.dsp.loudness_normalizer import LoudnessNormalizer
from app.core.config import settings

class DSPPipeline:
    """Complete DSP processing chain"""
    
    def __init__(self):
        """Initialize DSP Pipeline with all processors"""
        logger.info("Initializing DSP Pipeline")
        
        self.highpass = HighPassFilter(
            cutoff_freq=settings.HIGHPASS_FREQ,
            order=settings.HIGHPASS_ORDER,
            sample_rate=settings.SAMPLE_RATE,
        )
        
        self.noise_reducer = NoiseReducer(
            max_reduction_db=settings.NOISE_REDUCTION_DB,
            sample_rate=settings.SAMPLE_RATE,
        )
        
        self.deesser = DeEsser(
            sample_rate=settings.SAMPLE_RATE,
        )
        
        self.compressor = DynamicCompressor(
            ratio=settings.COMPRESSOR_RATIO,
            sample_rate=settings.SAMPLE_RATE,
        )
        
        self.limiter = Limiter(
            sample_rate=settings.SAMPLE_RATE,
        )
        
        self.loudness_normalizer = LoudnessNormalizer(
            target_lufs=settings.TARGET_LUFS,
            sample_rate=settings.SAMPLE_RATE,
        )
        
        logger.info("DSP Pipeline initialized with all processors")
    
    def process(
        self,
        audio: np.ndarray,
        bypass_steps: list = None,
    ) -> tuple[np.ndarray, Dict[str, Any]]:
        """
        Apply complete DSP chain to audio
        
        Execution order:
        1. High-pass filter
        2. Noise reduction
        3. De-esser
        4. Clarity enhancement
        5. Compressor
        6. Limiter
        7. LUFS normalization
        
        Args:
            audio: Input audio array
            bypass_steps: List of steps to bypass
        
        Returns:
            Tuple of (processed_audio, processing_stats)
        """
        try:
            if bypass_steps is None:
                bypass_steps = []
            
            logger.info("Starting DSP chain processing")
            
            stats = {
                "input_peak_dbfs": self.limiter.get_peak_level(audio),
                "input_loudness_lufs": self.loudness_normalizer.measure_loudness(audio),
                "processing_steps": [],
            }
            
            result = audio.copy()
            
            # 1. High-pass filter
            if "highpass" not in bypass_steps:
                result = self.highpass.process(result)
                stats["processing_steps"].append("highpass_filter")
                logger.info("✓ High-pass filter applied")
            
            # 2. Noise reduction
            if "noise_reduction" not in bypass_steps:
                result = self.noise_reducer.reduce_noise(result)
                stats["processing_steps"].append("noise_reduction")
                logger.info("✓ Noise reduction applied")
            
            # 3. De-esser
            if "deesser" not in bypass_steps:
                result = self.deesser.process(result)
                stats["processing_steps"].append("deesser")
                logger.info("✓ De-esser applied")
            
            # 4. Compressor
            if "compressor" not in bypass_steps:
                result = self.compressor.process(result)
                stats["processing_steps"].append("compressor")
                logger.info("✓ Compressor applied")
            
            # 5. Limiter
            if "limiter" not in bypass_steps:
                result = self.limiter.process(result)
                stats["processing_steps"].append("limiter")
                logger.info("✓ Limiter applied")
            
            # 6. LUFS normalization
            if "loudness" not in bypass_steps:
                result = self.loudness_normalizer.normalize(result)
                stats["processing_steps"].append("loudness_normalization")
                logger.info("✓ Loudness normalization applied")
            
            # Measure output
            stats["output_peak_dbfs"] = self.limiter.get_peak_level(result)
            stats["output_loudness_lufs"] = self.loudness_normalizer.measure_loudness(result)
            stats["peak_reduction_db"] = stats["input_peak_dbfs"] - stats["output_peak_dbfs"]
            stats["loudness_adjustment_db"] = stats["output_loudness_lufs"] - stats["input_loudness_lufs"]
            
            logger.info("DSP chain processing complete")
            return result, stats
        
        except Exception as e:
            logger.error(f"DSP processing failed: {str(e)}")
            raise
