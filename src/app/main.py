from fastapi import FastAPI
from src.app.celery_app import add

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI + Celery"}

@app.get("/add")
def enqueue_add(x: int, y: int):
    result = add.delay(x, y)
    return {"task_id": result.id}
