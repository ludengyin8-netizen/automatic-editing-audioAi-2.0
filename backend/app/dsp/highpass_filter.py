"""DSP Pipeline - High Pass Filter"""
from typing import Tuple
from loguru import logger
import numpy as np
from scipy import signal

class HighPassFilter:
    """Butterworth high-pass filter for removing low-frequency noise"""
    
    def __init__(
        self,
        cutoff_freq: int = 70,
        order: int = 12,
        sample_rate: int = 16000,
    ):
        """
        Initialize HighPassFilter
        
        Args:
            cutoff_freq: Cutoff frequency in Hz
            order: Filter order (12dB/oct)
            sample_rate: Sample rate in Hz
        """
        self.cutoff_freq = cutoff_freq
        self.order = order
        self.sample_rate = sample_rate
        
        # Design filter
        self.sos = signal.butter(
            order,
            cutoff_freq,
            btype='high',
            fs=sample_rate,
            output='sos'
        )
        
        logger.info(f"HighPassFilter initialized: {cutoff_freq}Hz, Order: {order}")
    
    def process(self, audio: np.ndarray) -> np.ndarray:
        """
        Apply high-pass filter to audio
        
        Args:
            audio: Input audio array
        
        Returns:
            Filtered audio array
        """
        try:
            filtered = signal.sosfilt(self.sos, audio)
            logger.info(f"High-pass filter applied: {self.cutoff_freq}Hz")
            return filtered
        except Exception as e:
            logger.error(f"High-pass filter failed: {str(e)}")
            raise
    
    def get_frequency_response(
        self,
        freq_range: Tuple[int, int] = (20, 20000),
        num_points: int = 1000,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get filter frequency response
        
        Args:
            freq_range: Frequency range (min, max)
            num_points: Number of points to calculate
        
        Returns:
            Tuple of (frequencies, magnitude_db)
        """
        try:
            w, h = signal.sosfreqz(self.sos, worN=num_points, fs=self.sample_rate)
            magnitude_db = 20 * np.log10(np.abs(h) + 1e-10)
            
            return w, magnitude_db
        except Exception as e:
            logger.error(f"Failed to get frequency response: {str(e)}")
            raise
