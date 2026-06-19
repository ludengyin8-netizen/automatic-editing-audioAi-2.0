"""DSP Pipeline - Loudness Normalization (LUFS)"""
from loguru import logger
import numpy as np
import pyloudnorm

class LoudnessNormalizer:
    """LUFS-based loudness normalization"""
    
    def __init__(
        self,
        target_lufs: float = -16.0,
        tolerance_lufs: float = 1.0,
        sample_rate: int = 16000,
    ):
        """
        Initialize LoudnessNormalizer
        
        Args:
            target_lufs: Target loudness in LUFS
            tolerance_lufs: Tolerance range in LUFS
            sample_rate: Sample rate in Hz
        """
        self.target_lufs = target_lufs
        self.tolerance_lufs = tolerance_lufs
        self.sample_rate = sample_rate
        
        # Initialize loudness meter
        self.meter = pyloudnorm.Meter(sample_rate)
        
        logger.info(f"LoudnessNormalizer initialized: Target {target_lufs}±{tolerance_lufs} LUFS")
    
    def measure_loudness(self, audio: np.ndarray) -> float:
        """
        Measure loudness of audio
        
        Args:
            audio: Audio array
        
        Returns:
            Loudness in LUFS
        """
        try:
            if len(audio) < self.sample_rate:
                logger.warning("Audio too short to measure loudness accurately")
            
            loudness = self.meter.integrated_loudness(audio)
            
            # Handle edge cases
            if loudness is None or np.isinf(loudness):
                logger.warning("Could not measure loudness, returning -70 LUFS")
                return -70.0
            
            logger.info(f"Measured loudness: {loudness:.2f} LUFS")
            return loudness
        
        except Exception as e:
            logger.error(f"Loudness measurement failed: {str(e)}")
            return -70.0  # Fallback to silent level
    
    def normalize(
        self,
        audio: np.ndarray,
        target_lufs: float = None,
    ) -> np.ndarray:
        """
        Normalize audio to target loudness
        
        Args:
            audio: Input audio array
            target_lufs: Override target LUFS (optional)
        
        Returns:
            Normalized audio
        """
        try:
            if target_lufs is None:
                target_lufs = self.target_lufs
            
            # Measure current loudness
            current_loudness = self.measure_loudness(audio)
            
            # If already within tolerance, no adjustment needed
            if abs(current_loudness - target_lufs) <= self.tolerance_lufs:
                logger.info(f"Audio already within tolerance: {current_loudness:.2f} LUFS")
                return audio
            
            # Normalize
            normalized = pyloudnorm.normalize.loudness(
                audio,
                current_loudness,
                target_lufs,
            )
            
            # Verify normalization
            new_loudness = self.measure_loudness(normalized)
            logger.info(f"Normalization applied: {current_loudness:.2f} → {new_loudness:.2f} LUFS")
            
            return normalized
        
        except Exception as e:
            logger.error(f"Normalization failed: {str(e)}")
            return audio
