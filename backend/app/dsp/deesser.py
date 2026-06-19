"""DSP Pipeline - De-Esser (Remove Sibilance)"""
from typing import Tuple
from loguru import logger
import numpy as np
from scipy import signal

class DeEsser:
    """De-esser for removing sibilance (s and sh sounds)"""
    
    def __init__(
        self,
        freq_min: int = 5000,
        freq_max: int = 8000,
        trigger_db: float = 6.0,
        reduction_db: float = 2.0,
        max_reduction_db: float = 4.0,
        sample_rate: int = 16000,
    ):
        """
        Initialize DeEsser
        
        Args:
            freq_min: Minimum frequency for sibilance detection (Hz)
            freq_max: Maximum frequency for sibilance detection (Hz)
            trigger_db: Trigger level above average (dB)
            reduction_db: Initial reduction amount (dB)
            max_reduction_db: Maximum reduction amount (dB)
            sample_rate: Sample rate (Hz)
        """
        self.freq_min = freq_min
        self.freq_max = freq_max
        self.trigger_db = trigger_db
        self.reduction_db = reduction_db
        self.max_reduction_db = max_reduction_db
        self.sample_rate = sample_rate
        
        # Design bandpass filter for sibilance range
        self.sos_bp = signal.butter(
            2,
            [freq_min, freq_max],
            btype='band',
            fs=sample_rate,
            output='sos'
        )
        
        logger.info(f"DeEsser initialized: {freq_min}-{freq_max}Hz, Trigger: {trigger_db}dB")
    
    def process(self, audio: np.ndarray) -> np.ndarray:
        """
        Apply de-esser to audio
        
        Args:
            audio: Input audio array
        
        Returns:
            De-essed audio
        """
        try:
            # Extract sibilance band
            sibilance = signal.sosfilt(self.sos_bp, audio)
            
            # Calculate RMS level
            rms_sibilance = np.sqrt(np.mean(sibilance ** 2))
            rms_total = np.sqrt(np.mean(audio ** 2))
            
            if rms_sibilance == 0:
                return audio
            
            # Calculate sibilance level relative to total
            sibilance_db = 20 * np.log10(rms_sibilance / (rms_total + 1e-10))
            
            # Apply reduction if sibilance is above threshold
            if sibilance_db > -self.trigger_db:
                # Calculate reduction amount
                reduction_amount = min(
                    self.reduction_db + (sibilance_db + self.trigger_db),
                    self.max_reduction_db
                )
                
                # Convert dB to linear
                reduction_factor = 10 ** (-reduction_amount / 20)
                
                # Apply reduction to sibilance band only
                result = audio.copy()
                result += (sibilance * (reduction_factor - 1))
                
                logger.info(f"De-esser applied: {reduction_amount:.1f}dB reduction")
                return result
            
            return audio
        
        except Exception as e:
            logger.error(f"De-esser failed: {str(e)}")
            raise
