from fastapi import FastAPI
from celery_app import add,celery
from celery.result import AsyncResult
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI + Celery"}

@app.post("/tasks/add")
def enqueue_add(x: int, y: int):
    result = add.delay(x, y)
    return {"task_id": result.id}

@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    result = AsyncResult(task_id,app=celery)
    return {"task_id": task_id, "status": result.status, "result": result.result}

#corre en docke