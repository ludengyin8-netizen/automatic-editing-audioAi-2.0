import logging
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)

class RetryManager:
    """
    依据质量检测结果决定是否重试或回退。
    依赖注入：
      - task_store: 提供 get(task_id)->dict 和 update(task_id, dict) 接口
      - processor: 提供 enqueue(task_id, job_config) 接口（重新排队处理）
    """
    def __init__(self, task_store, processor, max_retries: int = 3):
        self.task_store = task_store
        self.processor = processor
        self.max_retries = max_retries

    def handle_quality_result(self, task_id: str, quality_result: Dict[str, Any], current_config: Dict[str, Any]) -> Dict[str, Any]:
        if quality_result.get("passed"):
            self.task_store.update(task_id, {"quality_status": "passed", "quality_report": quality_result})
            return {"action": "none", "reason": "passed"}

        meta = self.task_store.get(task_id) or {}
        retries = int(meta.get("retries", 0))
        logger.info("Task %s quality failed severity=%s retries=%s", task_id, quality_result.get("severity_score"), retries)

        if retries >= self.max_retries:
            logger.warning("Task %s reached max retries, enqueueing final fallback (minimal processing)", task_id)
            self.task_store.update(task_id, {"quality_status": "failed_final", "quality_report": quality_result})
            fallback_cfg = dict(current_config or {})
            fallback_cfg.update({"bypass_processing": True, "note": "final_fallback_min_processing"})
            self.processor.enqueue(task_id, fallback_cfg)
            return {"action": "fallback", "reason": "max_retries_reached"}

        suggested = float(quality_result.get("suggested_rollback_fraction", 0.5))
        suggested = max(0.0, min(1.0, suggested))

        new_config = dict(current_config or {})
        # keys likely present in config — 请与 backend/config.yaml 保持一致
        for key in ["noise_reduction_db", "deesser_strength", "compressor_ratio", "clearifier_gain", "clearer_strength"]:
            if key in new_config and isinstance(new_config[key], (int, float)):
                # 保守减少：根据建议回退比例再减半，避免一次性过度回退
                new_config[key] = float(new_config[key]) * (1.0 - suggested * 0.5)

        new_meta = dict(meta)
        new_meta["retries"] = retries + 1
        new_meta["last_retry_at"] = int(time.time())
        self.task_store.update(task_id, new_meta)

        logger.info("Task %s enqueue retry #%s with reduced processing (suggested=%s)", task_id, new_meta["retries"], suggested)
        self.processor.enqueue(task_id, {"audio_path": new_config.get("audio_path"), "config": new_config})
        return {"action": "retry", "retry_number": new_meta["retries"], "new_config": new_config}
