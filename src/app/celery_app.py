from celery import Celery
import os

celery = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND")
)


@celery.task(bind=True)
def add(self, x, y):
    return x + y