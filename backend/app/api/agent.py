"""FastAPI routes for agent control (minimal implementation)."""
from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import Dict, Any
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# placeholders to be injected by application startup
agent_controller = None
task_store = None

@router.post("/agent/start")
async def agent_start(payload: Dict[str, Any], background_tasks: BackgroundTasks):
    """payload: {"task_id":..., "audio_path":..., "config": {...}}"""
    if agent_controller is None or task_store is None:
        raise HTTPException(status_code=500, detail="agent not initialized")
    task_id = payload.get("task_id")
    audio_path = payload.get("audio_path")
    config = payload.get("config", {})
    if not task_id or not audio_path:
        raise HTTPException(status_code=400, detail="task_id and audio_path required")

    # create task record
    task_store.update(task_id, {"status": "queued", "audio_path": audio_path})

    # run in background
    def _run():
        try:
            agent_controller.start_task(task_id, audio_path, config)
        except Exception as e:
            logger.exception("Agent run failed for %s", task_id)
            task_store.update(task_id, {"status": "failed", "error": str(e)})

    background_tasks.add_task(_run)
    return {"status": "accepted", "task_id": task_id}

@router.get("/agent/status/{task_id}")
async def agent_status(task_id: str):
    if task_store is None:
        raise HTTPException(status_code=500, detail="task store not initialized")
    return task_store.get(task_id) or {"status": "not_found"}
