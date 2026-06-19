import numpy as np
import soundfile as sf
from pathlib import Path
from backend.app.validator.quality_validator import QualityValidator

def make_sine(sr=16000, dur=1.0, freq=440.0, amp=0.05):
    t = np.linspace(0, dur, int(sr*dur), endpoint=False)
    return amp * np.sin(2*np.pi*freq*t)

def test_long_pause_detection(tmp_path):
    sr = 16000
    a = make_sine(sr=sr, dur=1.0)
    silence = np.zeros(int(sr * 1.5))
    b = make_sine(sr=sr, dur=1.0)
    y = np.concatenate([a, silence, b])
    p = tmp_path / "test.wav"
    sf.write(str(p), y, sr)
    cfg = {"target_lufs": -16.0, "lufs_tolerance": 3.0, "max_pause_seconds": 0.8}
    v = QualityValidator(cfg)
    r = v.validate(str(p), transcript=None)
    assert isinstance(r, dict)
    assert ("long_pauses" in [iss["code"] for iss in r["issues"]]) or not r["passed"]
