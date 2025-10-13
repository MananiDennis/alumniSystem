from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid
from datetime import datetime
from threading import Lock

from src.services.alumni_collector import AlumniCollector
from src.api.utils import format_alumni

router = APIRouter(prefix="", tags=["collection"])  # keep root-level endpoints

# Simple in-memory task store for demo; in prod use Redis/RQ/Celery
task_store: Dict[str, Dict[str, Any]] = {}
task_lock = Lock()


class CollectRequest(BaseModel):
    names: List[str]
    use_web_research: bool = False


@router.post("/collect")
def collect_alumni(request: CollectRequest, background_tasks: BackgroundTasks, user_email: str = Depends(lambda: "admin")):
    task_id = str(uuid.uuid4())
    with task_lock:
        task_store[task_id] = {
            "status": "running",
            "names": request.names,
            "method": "web-research" if request.use_web_research else "brightdata",
            "start_time": datetime.utcnow(),
            "results_count": 0,
            "results": [],
            "error": None
        }

    background_tasks.add_task(run_collection_task, task_id, request.names, request.use_web_research)

    return {"task_id": task_id, "message": "Collection started", "status": "running"}


def run_collection_task(task_id: str, names: List[str], use_web_research: bool):
    collector = None
    try:
        collector = AlumniCollector()
        method = "web-research" if use_web_research else "brightdata"
        profiles = collector.collect_alumni(names, method=method)

        with task_lock:
            if len(profiles) == 0:
                task_store[task_id].update({
                    "status": "failed",
                    "error": "No alumni profiles were collected.",
                    "end_time": datetime.utcnow()
                })
            else:
                task_store[task_id].update({
                    "status": "completed",
                    "results_count": len(profiles),
                    "results": [format_alumni(p) for p in profiles],
                    "end_time": datetime.utcnow()
                })
    except Exception as e:
        with task_lock:
            task_store[task_id].update({"status": "failed", "error": str(e), "end_time": datetime.utcnow()})
    finally:
        if collector:
            collector.close()


@router.get("/collect/status/{task_id}")
def get_collect_status(task_id: str, user_email: str = Depends(lambda: "admin")):
    with task_lock:
        task = task_store.get(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "task_id": task_id,
        "status": task["status"],
        "results_count": task.get("results_count", 0),
        "results": task.get("results", []),
        "error": task.get("error"),
        "start_time": task.get("start_time").isoformat() if task.get("start_time") else None,
        "end_time": task.get("end_time").isoformat() if task.get("end_time") else None
    }
