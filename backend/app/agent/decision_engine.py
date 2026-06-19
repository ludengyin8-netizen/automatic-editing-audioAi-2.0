"""Decision engine: converts content analysis into structured editing decisions."""
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class DecisionEngine:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    def decide(self, analysis: Dict[str, Any], transcript: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, Any]:
        """Produce a conservative decision set based on analysis.
        - remove_fillers: count to remove
        - fix_stutters: count
        - pause_adjustments: list of {start,end,target}
        - dsp: adjustments
        - confidence: 0..1
        """
        decision = {
            "remove_fillers": 0,
            "fix_stutters": 0,
            "pause_adjustments": [],
            "dsp": {},
            "confidence": 0.0
        }

        # Simple heuristics based on analysis keys
        fillers = analysis.get("fillers", [])
        stutters = analysis.get("stutters", [])
        pauses = analysis.get("pauses", [])

        # conservative: remove up to 1 filler per sentence
        decision["remove_fillers"] = min(len(fillers), max(0, int(len(transcript) * 0.1)))
        decision["fix_stutters"] = min(len(stutters), max(0, int(len(transcript) * 0.05)))

        # pause adjustments: only for pauses longer than configured threshold
        pause_thresh = config.get("pause_opt_threshold", 0.8)
        for p in pauses:
            if p.get("duration", 0) > pause_thresh:
                # target in [0.5,0.8]
                target = max(0.5, min(0.8, p["duration"] * 0.7))
                decision["pause_adjustments"].append({"start": p.get("start"), "end": p.get("end"), "target": target})

        # dsp defaults
        decision["dsp"] = {
            "noise_reduction_db": config.get("noise_reduction_db", 2.5),
            "deesser_strength": config.get("deesser_strength", 0.8),
            "compressor_ratio": config.get("compressor_ratio", 1.8),
        }

        # confidence heuristic
        issues = analysis.get("issues", [])
        decision["confidence"] = max(0.0, 1.0 - min(1.0, len(issues) * 0.1))

        logger.debug("DecisionEngine produced: %s", decision)
        return decision
