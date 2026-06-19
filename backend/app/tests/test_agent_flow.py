"""Tests for basic agent flow using lightweight stubs."""
import numpy as np
import soundfile as sf
from pathlib import Path
from backend.app.agent.decision_engine import DecisionEngine
from backend.app.agent.controller import AgentController
from backend.app.core.edit_logger import EditLogger

class StubASR:
    def transcribe(self, path):
        # return a fake transcript: list of words with start/end
        return [{"word": "你好", "start": 0.0, "end": 0.5, "confidence": 0.98}]

class StubAnalyzer:
    def analyze(self, path, transcript):
        return {"fillers": [], "stutters": [], "pauses": [], "issues": []}

class StubEditor:
    def apply_edits(self, path, decision):
        return path  # no-op

class StubDSP:
    def process(self, path, dsp_cfg):
        return path

class StubValidator:
    def validate(self, path, transcript):
        return {"passed": True, "severity_score": 0}

class InMemoryTaskStore:
    def __init__(self):
        self.store = {}
    def update(self, task_id, info):
        self.store.setdefault(task_id, {}).update(info)
    def get(self, task_id):
        return self.store.get(task_id)

def make_sine(sr=16000, dur=0.6, freq=440.0, amp=0.05):
    t = np.linspace(0, dur, int(sr*dur), endpoint=False)
    return amp * np.sin(2*np.pi*freq*t)


def test_agent_controller_end_to_end(tmp_path):
    sr = 16000
    y = make_sine(sr=sr)
    p = tmp_path / "s.wav"
    sf.write(str(p), y, sr)

    task_store = InMemoryTaskStore()
    asr = StubASR()
    analyzer = StubAnalyzer()
    decision_engine = DecisionEngine()
    editor = StubEditor()
    dsp = StubDSP()
    validator = StubValidator()
    edit_logger = EditLogger(base_dir=str(tmp_path / "outputs"))

    controller = AgentController(asr, analyzer, decision_engine, editor, dsp, validator, task_store, None, edit_logger)
    r = controller.start_task("t1", str(p), {})
    assert "export_path" in r
    assert task_store.get("t1")["status"] == "finished"
