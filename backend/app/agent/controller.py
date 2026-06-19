"""Agent controller: orchestrates ASR -> Analysis -> Decision -> Editing -> DSP -> Validate -> Export
This module uses dependency injection for components so it can be integrated with the project's real implementations.
"""
from typing import Dict, Any
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class AgentController:
    def __init__(self, asr, analyzer, decision_engine, editor, dsp, validator, task_store, processor, edit_logger):
        self.asr = asr
        self.analyzer = analyzer
        self.decision_engine = decision_engine
        self.editor = editor
        self.dsp = dsp
        self.validator = validator
        self.task_store = task_store
        self.processor = processor
        self.edit_logger = edit_logger

    def start_task(self, task_id: str, audio_path: str, config: Dict[str, Any]):
        """Synchronous simplified flow for MVP. In production this should run in a worker.
        Returns the final export path and the decision JSON.
        """
        self.task_store.update(task_id, {"status": "started"})
        logger.info("Agent start_task %s %s", task_id, audio_path)

        # 1) ASR
        transcript = self.asr.transcribe(audio_path)
        self.task_store.update(task_id, {"transcript": transcript})

        # 2) Analysis
        analysis = self.analyzer.analyze(audio_path, transcript)
        self.task_store.update(task_id, {"analysis": analysis})

        # 3) Decision
        decision = self.decision_engine.decide(analysis, transcript, config)
        self.edit_logger.write_edit_decision(task_id, decision)
        self.task_store.update(task_id, {"decision": decision})

        # 4) Editing
        edited_path = self.editor.apply_edits(audio_path, decision)
        self.task_store.update(task_id, {"edited_path": edited_path})

        # 5) DSP
        dsp_out = self.dsp.process(edited_path, decision.get("dsp", {}))
        self.task_store.update(task_id, {"dsp_out": dsp_out})

        # 6) Validate
        quality = self.validator.validate(dsp_out, transcript)
        self.task_store.update(task_id, {"quality": quality})

        # 7) Export
        export_path = self._export_final(dsp_out, task_id)
        self.task_store.update(task_id, {"status": "finished", "export_path": export_path})

        logger.info("Agent task %s finished, export=%s", task_id, export_path)
        return {"export_path": export_path, "decision": decision, "quality": quality}

    def _export_final(self, file_path: str, task_id: str) -> str:
        out_dir = Path("outputs") / task_id
        out_dir.mkdir(parents=True, exist_ok=True)
        dest = out_dir / Path(file_path).name
        # simple copy to outputs as export step
        with open(file_path, "rb") as rf, open(dest, "wb") as wf:
            wf.write(rf.read())
        return str(dest)
