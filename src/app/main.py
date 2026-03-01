# src/app/main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from src.app.core.db import SessionLocal
from src.app.models.task import Task
from src.app.celery_app import celery, add, unstable_task, process_image
import json
from fastapi import UploadFile, File, Depends
from sqlalchemy.orm import Session
from src.app.models.image import Image
import os
from src.app.core.config import UPLOAD_DIR

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/tasks/add")
def enqueue_add(x: int, y: int, db: Session = Depends(get_db)):
    result = add.delay(x, y)

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
    

@app.post("/tasks/unstable")
def enqueue_unstable(db: Session = Depends(get_db)):
    result = unstable_task.delay()
    return {"task_id": result.id}


@app.get("/tasks/{task_id}")
def get_task_status(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    #if not task:
    #   return {"error": "Task not found"}
    return {
        "task_id": task.id,
        "status": task.status,
        "result": task.result,
        "error_message": task.error_message
    }


@app.post("/upload")
def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(file.file.read())

    new_image = Image(filename=file.filename, path=file_location)
    db.add(new_image)
    db.commit()
    db.refresh(new_image)

    return {"id": str(new_image.id), "filename": new_image.filename, "status": new_image.status}


#necesitas los dos endpoints
@app.post("/images/{image_id}/process")
def enqueue_process_image(image_id: str, db: Session = Depends(get_db)):
    result = process_image.delay(image_id)

    task = Task(
        id=result.id,
        status="PENDING",
        task_name="process_image",
        payload=json.dumps({"image_id": image_id})
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return {"task_id": result.id, "status": task.status}

