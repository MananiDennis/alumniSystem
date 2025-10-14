from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid
from datetime import datetime
from threading import Lock
import json

from src.services.alumni_collector import AlumniCollector
from src.api.utils import format_alumni
from src.database.connection import db_manager
from src.database.models import TaskDB

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
    
    # Create database task
    session = db_manager.get_session()
    try:
        db_task = TaskDB(
            id=task_id,
            status="running",
            names=json.dumps(request.names),
            method="web-research" if request.use_web_research else "brightdata",
            start_time=datetime.utcnow(),
            results_count=0,
            results=json.dumps([]),
            failed_names=json.dumps([]),
            error=None
        )
        session.add(db_task)
        session.commit()
    finally:
        session.close()

    background_tasks.add_task(run_collection_task, task_id, request.names, request.use_web_research)

    return {"task_id": task_id, "message": "Collection started", "status": "running"}


def run_collection_task(task_id: str, names: List[str], use_web_research: bool):
    collector = None
    try:
        collector = AlumniCollector()
        method = "web-research" if use_web_research else "brightdata"
        result = collector.collect_alumni(names, method=method)

        # Handle new return format with successful_profiles and failed_names
        successful_profiles = result.get("successful_profiles", [])
        failed_names = result.get("failed_names", [])

        with task_lock:
            if len(successful_profiles) == 0 and len(failed_names) == len(names):
                # All failed
                task_store[task_id].update({
                    "status": "failed",
                    "error": "No alumni profiles were collected.",
                    "results_count": 0,
                    "failed_names": failed_names,
                    "end_time": datetime.utcnow()
                })
            else:
                # Some succeeded, some failed
                task_store[task_id].update({
                    "status": "completed",
                    "results_count": len(successful_profiles),
                    "results": [format_alumni(p) for p in successful_profiles],
                    "failed_names": failed_names,
                    "end_time": datetime.utcnow()
                })
    except Exception as e:
        with task_lock:
            task_store[task_id].update({"status": "failed", "error": str(e), "end_time": datetime.utcnow()})
    finally:
        if collector:
            collector.close()


@router.get("/collect/failed/{task_id}")
def get_failed_names(task_id: str, user_email: str = Depends(lambda: "admin")):
    """Get failed names from a collection task for manual entry"""
    with task_lock:
        task = task_store.get(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task["status"] not in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="Task is still running")

    failed_names = task.get("failed_names", [])
    return {
        "task_id": task_id,
        "failed_names": failed_names,
        "count": len(failed_names)
    }
