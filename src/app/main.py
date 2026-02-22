# src/app/main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from src.app.core.db import SessionLocal
from src.app.models.task import Task
from src.app.celery_app import celery
from celery.result import AsyncResult
import json

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/tasks/add")
def enqueue_add(x: int, y: int, db: Session = Depends(get_db)):
    result = celery.send_task("src.app.celery_app.add", args=[x, y])

    task = Task(
        id=result.id,
        status="PENDING",
        task_name="add",
        payload=json.dumps({"x": x, "y": y})
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return {"task_id": result.id, "status": task.status}
    

@app.get("/tasks/{task_id}")
def get_task_status(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return {"error": "Task not found"}
    return {
        "task_id": task.id,
        "status": task.status,
        "result": task.result,
        "error_message": task.error_message
    }
