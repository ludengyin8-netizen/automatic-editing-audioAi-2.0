"""Tests for DSP Pipeline"""
import pytest
import numpy as np
from app.dsp.highpass_filter import HighPassFilter
from app.dsp.deesser import DeEsser
from app.dsp.compressor import DynamicCompressor
from app.dsp.limiter import Limiter
from app.dsp.loudness_normalizer import LoudnessNormalizer

def create_test_audio(duration: float = 1.0, frequency: float = 440, sample_rate: int = 16000) -> np.ndarray:
    """Create test audio signal"""
    t = np.linspace(0, duration, int(duration * sample_rate))
    return 0.1 * np.sin(2 * np.pi * frequency * t)

def test_highpass_filter():
    """Test high-pass filter"""
    filt = HighPassFilter(cutoff_freq=70, sample_rate=16000)
    audio = create_test_audio()
    
    filtered = filt.process(audio)
    
    assert filtered.shape == audio.shape
    assert not np.isnan(filtered).any()
    assert not np.isinf(filtered).any()

def test_deesser():
    """Test de-esser"""
    deesser = DeEsser(sample_rate=16000)
    
    # Create audio with sibilance (high frequency content)
    t = np.linspace(0, 1, 16000)
    audio = 0.1 * np.sin(2 * np.pi * 6000 * t)  # 6kHz
    
    processed = deesser.process(audio)
    
    assert processed.shape == audio.shape
    assert not np.isnan(processed).any()

def test_compressor():
    """Test dynamic compressor"""
    compressor = DynamicCompressor(ratio=1.8, sample_rate=16000)
    audio = create_test_audio()
    
    compressed = compressor.process(audio)
    
    assert compressed.shape == audio.shape
    assert not np.isnan(compressed).any()

def test_limiter():
    """Test limiter"""
    limiter = Limiter(true_peak_dbfs=-1.0, sample_rate=16000)
    audio = create_test_audio()
    
    limited = limiter.process(audio)
    
    assert limited.shape == audio.shape
    assert not np.isnan(limited).any()
    
    # Peak should be limited
    peak = limiter.get_peak_level(limited)
    assert peak <= -1.0 + 0.1  # Allow small margin

def test_loudness_normalizer():
    """Test loudness normalizer"""
    normalizer = LoudnessNormalizer(target_lufs=-16.0, sample_rate=16000)
    audio = create_test_audio(duration=2.0)
    
    normalized = normalizer.normalize(audio, target_lufs=-16.0)
    
    assert normalized.shape == audio.shape
    assert not np.isnan(normalized).any()
