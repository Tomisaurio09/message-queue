# src/app/celery_app.py
from celery import Celery
from sqlalchemy.orm import Session
from src.app.core.db import SessionLocal
from src.app.models.task import Task
from src.app.core.config import settings

celery = Celery("worker", broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)

@celery.task(bind=True, name="src.app.celery_app.add")
def add(self, x, y):
    db: Session = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == self.request.id).first()
        result_value = x + y
        if task:
            task.status = "SUCCESS"
            task.result = str(result_value)
            db.commit()
        return result_value
    except Exception as e:
        if task:
            task.status = "FAILURE"
            task.error_message = str(e)
            db.commit()
        raise
    finally:
        db.close()
