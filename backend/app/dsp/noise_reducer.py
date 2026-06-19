"""DSP Pipeline - Noise Reduction"""
from typing import Optional
from loguru import logger
import numpy as np
from scipy import signal

class NoiseReducer:
    """Adaptive noise reduction preserving speech characteristics"""
    
    def __init__(
        self,
        max_reduction_db: float = 4.0,
        sample_rate: int = 16000,
    ):
        """
        Initialize NoiseReducer
        
        Args:
            max_reduction_db: Maximum noise reduction in dB
            sample_rate: Sample rate in Hz
        """
        self.max_reduction_db = max_reduction_db
        self.sample_rate = sample_rate
        logger.info(f"NoiseReducer initialized: Max reduction {max_reduction_db}dB")
    
    def estimate_noise_profile(
        self,
        audio: np.ndarray,
        noise_duration: float = 1.0,
    ) -> np.ndarray:
        """
        Estimate noise profile from beginning of audio
        
        Args:
            audio: Audio array
            noise_duration: Duration of noise to sample from (seconds)
        
        Returns:
            Noise profile (magnitude spectrum)
        """
        try:
            # Take beginning of audio as noise sample
            noise_samples = int(noise_duration * self.sample_rate)
            noise_sample = audio[:min(noise_samples, len(audio))]
            
            # Compute short-time Fourier transform
            f, t, Sxx = signal.spectrogram(
                noise_sample,
                fs=self.sample_rate,
                window='hann',
                nperseg=512,
            )
            
            # Average magnitude spectrum
            noise_profile = np.mean(Sxx, axis=1)
            
            logger.info(f"Noise profile estimated from {noise_duration}s")
            return noise_profile
        
        except Exception as e:
            logger.error(f"Noise profile estimation failed: {str(e)}")
            raise
    
    def reduce_noise(
        self,
        audio: np.ndarray,
        noise_profile: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """
        Apply noise reduction to audio
        
        Args:
            audio: Input audio array
            noise_profile: Pre-computed noise profile (optional)
        
        Returns:
            Noise-reduced audio
        """
        try:
            # If no noise profile provided, estimate from audio
            if noise_profile is None:
                noise_profile = self.estimate_noise_profile(audio)
            
            # Apply spectral subtraction
            f, t, Sxx = signal.spectrogram(
                audio,
                fs=self.sample_rate,
                window='hann',
                nperseg=512,
            )
            
            # Convert dB reduction to linear factor
            reduction_factor = 10 ** (-self.max_reduction_db / 20)
            
            # Subtract noise spectrum
            Sxx_reduced = Sxx - (noise_profile.reshape(-1, 1) * reduction_factor)
            
            # Ensure non-negative
            Sxx_reduced = np.maximum(Sxx_reduced, 0)
            
            # Reconstruct audio
            _, reduced = signal.istft(
                Sxx_reduced,
                fs=self.sample_rate,
                window='hann',
                nperseg=512,
            )
            
            logger.info(f"Noise reduction applied: {self.max_reduction_db}dB")
            return reduced
        
        except Exception as e:
            logger.error(f"Noise reduction failed: {str(e)}")
            raise
