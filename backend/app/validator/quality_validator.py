import logging
from typing import List, Dict, Any, Optional
import numpy as np
import librosa
import pyloudnorm as pyln
import math
from pathlib import Path

logger = logging.getLogger(__name__)

class QualityIssue:
    def __init__(self, code: str, message: str, severity: int = 1, meta: Optional[Dict[str, Any]] = None):
        self.code = code
        self.message = message
        self.severity = severity
        self.meta = meta or {}

    def to_dict(self):
        return {"code": self.code, "message": self.message, "severity": self.severity, "meta": self.meta}

class QualityValidator:
    """
    质量检查器，尽量保持轻量、可配置。输入为已处理后的音频文件路径和可选的转录（逐词时间轴）。
    返回包含 issues 列表、severity_score、passed 与 suggested_rollback_fraction。
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config or {}
        self.lufs_target = float(self.config.get("target_lufs", -16.0))
        self.lufs_tolerance = float(self.config.get("lufs_tolerance", 1.0))
        self.pause_max_threshold = float(self.config.get("max_pause_seconds", 0.8))
        self.volume_diff_threshold_db = float(self.config.get("adjacent_sentence_db_diff", 3.0))
        self.max_retry_suggestions = int(self.config.get("max_retry_suggestions", 3))

    def _load(self, audio_path: str):
        audio_path = str(audio_path)
        y, sr = librosa.load(audio_path, sr=None, mono=True)
        return y, sr

    def analyze_loudness(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        meter = pyln.Meter(sr)
        try:
            loudness = meter.integrated_loudness(y)
        except Exception:
            rms = np.sqrt(np.mean(y ** 2) + 1e-12)
            loudness = 20 * math.log10(rms + 1e-9)
        return {"loudness_lufs": float(loudness)}

    def detect_lufs_issue(self, lufs_value: float) -> Optional[QualityIssue]:
        if abs(lufs_value - self.lufs_target) > self.lufs_tolerance:
            severity = 2 if abs(lufs_value - self.lufs_target) <= 3.0 else 3
            return QualityIssue(
                code="lufs_mismatch",
                message=f"目标 LUFS {self.lufs_target}，当前 {lufs_value:.2f}，超出容差 {self.lufs_tolerance}",
                severity=severity,
                meta={"current_lufs": lufs_value}
            )
        return None

    def detect_volume_fluctuation(self, y: np.ndarray, sr: int) -> Optional[QualityIssue]:
        frame_len = int(0.5 * sr)
        if frame_len <= 0:
            return None
        n = max(1, len(y) // frame_len)
        seg_levels = []
        for i in range(n):
            seg = y[i*frame_len:(i+1)*frame_len]
            if seg.size == 0:
                continue
            seg_levels.append(20 * np.log10(np.sqrt(np.mean(seg**2)) + 1e-9))
        if len(seg_levels) < 2:
            return None
        diff = float(max(seg_levels) - min(seg_levels))
        if diff > self.volume_diff_threshold_db:
            severity = 2 if diff <= 6.0 else 3
            return QualityIssue(
                code="volume_fluctuation",
                message=f"短段响度差 {diff:.2f} dB，超过阈值 {self.volume_diff_threshold_db} dB",
                severity=severity,
                meta={"db_range": diff}
            )
        return None

    def detect_pauses(self, y: np.ndarray, sr: int) -> Optional[QualityIssue]:
        hop = max(1, int(0.01 * sr))
        frame_len = max(256, int(0.03 * sr))
        energy = librosa.feature.rms(y=y, frame_length=frame_len, hop_length=hop)[0]
        times = librosa.frames_to_time(range(len(energy)), sr=sr, hop_length=hop, n_fft=frame_len)
        if energy.size == 0:
            return None
        thresh = max(np.median(energy) * 0.2, 1e-8)
        silence_mask = energy < thresh
        gaps = []
        start = None
        for i, s in enumerate(silence_mask):
            if s and start is None:
                start = times[i]
            if (not s) and start is not None:
                end = times[i]
                gaps.append(end - start)
                start = None
        if start is not None:
            gaps.append(times[-1] - start)
        long_pauses = [g for g in gaps if g >= self.pause_max_threshold]
        if long_pauses:
            count = len(long_pauses)
            max_g = float(max(long_pauses))
            severity = 2 if max_g <= 2.0 else 3
            return QualityIssue(
                code="long_pauses",
                message=f"检测到 {count} 个停顿 > {self.pause_max_threshold}s，最长 {max_g:.2f}s",
                severity=severity,
                meta={"count": count, "max_pause": max_g, "pauses": long_pauses}
            )
        return None

    def detect_clipping(self, y: np.ndarray) -> Optional[QualityIssue]:
        if np.any(np.abs(y) >= 0.999):
            return QualityIssue(
                code="clipping_detected",
                message="可能出现削波（样点接近 ±1.0）",
                severity=3
            )
        return None

    def detect_spectral_flatness(self, y: np.ndarray) -> Optional[QualityIssue]:
        S = np.abs(librosa.stft(y, n_fft=2048, hop_length=512))
        flatness = librosa.feature.spectral_flatness(S=S).mean()
        if flatness > 0.06:
            return QualityIssue(
                code="spectral_flatness_high",
                message=f"频谱平坦度偏高（{flatness:.3f}），可能导致机器人/水下感",
                severity=2,
                meta={"spectral_flatness": float(flatness)}
            )
        return None

    def analyze_transcript_gaps(self, transcript: List[Dict[str, Any]]) -> Optional[QualityIssue]:
        if not transcript:
            return None
        gaps = []
        low_conf_count = 0
        for i in range(len(transcript) - 1):
            gap = transcript[i+1]["start"] - transcript[i]["end"]
            gaps.append(gap)
        large_gaps = [g for g in gaps if g > 1.2]
        for w in transcript:
            if "confidence" in w and w["confidence"] < 0.5:
                low_conf_count += 1
        if large_gaps:
            return QualityIssue(
                code="transcript_gaps",
                message=f"检测到 {len(large_gaps)} 个词间间隔 > 1.2s，可能存在缺字/缺段",
                severity=3,
                meta={"gaps": large_gaps}
            )
        if low_conf_count > max(2, len(transcript)*0.02):
            return QualityIssue(
                code="low_asr_confidence",
                message=f"ASR 低置信词过多：{low_conf_count}",
                severity=2,
                meta={"low_confidence_count": low_conf_count}
            )
        return None

    def validate(self, audio_path: str, transcript: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        p = Path(audio_path)
        if not p.exists():
            raise FileNotFoundError(f"audio file not found: {audio_path}")
        y, sr = self._load(audio_path)
        issues: List[QualityIssue] = []

        lufs_info = self.analyze_loudness(y, sr)
        li = self.detect_lufs_issue(lufs_info["loudness_lufs"])
        if li:
            issues.append(li)

        vol = self.detect_volume_fluctuation(y, sr)
        if vol:
            issues.append(vol)

        pauses = self.detect_pauses(y, sr)
        if pauses:
            issues.append(pauses)

        clip = self.detect_clipping(y)
        if clip:
            issues.append(clip)

        spec = self.detect_spectral_flatness(y, sr) if False else self.detect_spectral_flatness(y, sr)
        if spec:
            issues.append(spec)

        if transcript:
            t_issue = self.analyze_transcript_gaps(transcript)
            if t_issue:
                issues.append(t_issue)

        severity_score = sum([i.severity for i in issues])
        passed = severity_score == 0

        if severity_score == 0:
            suggested_rollback = 0.0
        elif severity_score <= 2:
            suggested_rollback = 0.25
        elif severity_score <= 5:
            suggested_rollback = 0.5
        else:
            suggested_rollback = 0.75

        result = {
            "passed": passed,
            "severity_score": severity_score,
            "issues": [i.to_dict() for i in issues],
            "loudness": lufs_info,
            "suggested_rollback_fraction": suggested_rollback
        }
        logger.info("QualityValidator result for %s: %s", audio_path, result)
        return result
