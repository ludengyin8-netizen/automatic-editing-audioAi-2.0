"""DSP Pipeline - Dynamic Compressor"""
from loguru import logger
import numpy as np

class DynamicCompressor:
    """Dynamic range compressor for controlling peak levels"""
    
    def __init__(
        self,
        ratio: float = 1.8,
        attack_ms: float = 15,
        release_ms: float = 120,
        threshold_db: float = -20,
        sample_rate: int = 16000,
    ):
        """
        Initialize DynamicCompressor
        
        Args:
            ratio: Compression ratio (e.g., 1.8:1)
            attack_ms: Attack time in milliseconds
            release_ms: Release time in milliseconds
            threshold_db: Threshold level in dB
            sample_rate: Sample rate in Hz
        """
        self.ratio = ratio
        self.attack_ms = attack_ms
        self.release_ms = release_ms
        self.threshold_db = threshold_db
        self.sample_rate = sample_rate
        
        # Convert times to samples
        self.attack_samples = int(attack_ms * sample_rate / 1000)
        self.release_samples = int(release_ms * sample_rate / 1000)
        
        logger.info(f"DynamicCompressor initialized: Ratio {ratio}:1, Attack {attack_ms}ms, Release {release_ms}ms")
    
    def process(self, audio: np.ndarray) -> np.ndarray:
        """
        Apply dynamic compression to audio
        
        Args:
            audio: Input audio array
        
        Returns:
            Compressed audio
        """
        try:
            output = np.zeros_like(audio)
            threshold_linear = 10 ** (self.threshold_db / 20)
            
            gain_reduction = 1.0
            
            for i in range(len(audio)):
                # Get current sample amplitude
                amplitude = abs(audio[i])
                
                if amplitude > threshold_linear:
                    # Calculate gain reduction needed
                    gain_reduction_target = threshold_linear + (amplitude - threshold_linear) / self.ratio
                    gain_reduction_target = gain_reduction_target / amplitude
                else:
                    gain_reduction_target = 1.0
                
                # Smooth gain reduction with attack/release
                if gain_reduction_target < gain_reduction:
                    # Attack phase
                    alpha = 1.0 / max(1, self.attack_samples)
                else:
                    # Release phase
                    alpha = 1.0 / max(1, self.release_samples)
                
                gain_reduction += alpha * (gain_reduction_target - gain_reduction)
                
                # Apply gain reduction
                output[i] = audio[i] * gain_reduction
            
            logger.info(f"Compression applied: {self.ratio}:1")
            return output
        
        except Exception as e:
            logger.error(f"Compression failed: {str(e)}")
            raise
