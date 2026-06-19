"""DSP Pipeline - Limiter"""
from loguru import logger
import numpy as np

class Limiter:
    """Look-ahead limiter to prevent clipping"""
    
    def __init__(
        self,
        true_peak_dbfs: float = -1.0,
        lookahead_ms: float = 5,
        sample_rate: int = 16000,
    ):
        """
        Initialize Limiter
        
        Args:
            true_peak_dbfs: True peak limit in dBFS
            lookahead_ms: Look-ahead time in milliseconds
            sample_rate: Sample rate in Hz
        """
        self.true_peak_dbfs = true_peak_dbfs
        self.lookahead_ms = lookahead_ms
        self.sample_rate = sample_rate
        
        self.lookahead_samples = int(lookahead_ms * sample_rate / 1000)
        self.threshold_linear = 10 ** (true_peak_dbfs / 20)
        
        logger.info(f"Limiter initialized: True Peak {true_peak_dbfs}dBFS, Lookahead {lookahead_ms}ms")
    
    def process(self, audio: np.ndarray) -> np.ndarray:
        """
        Apply limiting to audio
        
        Args:
            audio: Input audio array
        
        Returns:
            Limited audio
        """
        try:
            output = audio.copy()
            
            # Find peaks within lookahead window
            for i in range(len(audio)):
                # Look ahead
                lookahead_end = min(i + self.lookahead_samples, len(audio))
                future_peak = np.max(np.abs(audio[i:lookahead_end]))
                
                if future_peak > self.threshold_linear:
                    # Calculate gain reduction
                    gain = self.threshold_linear / (future_peak + 1e-10)
                    output[i] = audio[i] * gain
                else:
                    output[i] = audio[i]
            
            logger.info(f"Limiting applied: {self.true_peak_dbfs}dBFS")
            return output
        
        except Exception as e:
            logger.error(f"Limiting failed: {str(e)}")
            raise
    
    def get_peak_level(self, audio: np.ndarray) -> float:
        """
        Get peak level of audio in dBFS
        
        Args:
            audio: Audio array
        
        Returns:
            Peak level in dBFS
        """
        peak_linear = np.max(np.abs(audio))
        if peak_linear > 0:
            peak_dbfs = 20 * np.log10(peak_linear)
        else:
            peak_dbfs = -np.inf
        
        return peak_dbfs
