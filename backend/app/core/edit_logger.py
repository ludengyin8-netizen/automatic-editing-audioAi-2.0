"""Edit decision logger: writes edit_decision JSON and keeps audit logs."""
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class EditLogger:
    def __init__(self, base_dir: str = "outputs"):
        self.base = Path(base_dir)
        self.base.mkdir(parents=True, exist_ok=True)

    def write_edit_decision(self, task_id: str, decision: dict):
        out_dir = self.base / task_id
        out_dir.mkdir(parents=True, exist_ok=True)
        p = out_dir / "edit_decision.json"
        with open(p, "w", encoding="utf-8") as f:
            json.dump(decision, f, ensure_ascii=False, indent=2)
        logger.info("Wrote edit_decision for %s -> %s", task_id, str(p))
        return str(p)
