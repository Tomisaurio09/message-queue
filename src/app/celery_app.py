# src/app/celery_app.py
from celery import Celery
from sqlalchemy.orm import Session
from src.app.core.db import SessionLocal
from src.app.models.task import Task
from src.app.core.config import settings
from kombu import Exchange, Queue
from src.app.models.image import Image
from PIL import Image as PILImage
import os
from src.app.core.config import PROCESSED_DIR
import smtplib
from email.mime.text import MIMEText


tasks_exchange = Exchange("tasks", type="direct")

image_queue = Queue(
    "image_queue",
    exchange=tasks_exchange,
    routing_key="image.#",
    queue_arguments={
        "x-dead-letter-exchange": "dlx_exchange"
    }
)

email_queue = Queue(
    "email_queue",
    exchange=tasks_exchange,
    routing_key="email.#",
    queue_arguments={
        "x-dead-letter-exchange": "dlx_exchange"
    }
)

task_queues = (image_queue, email_queue)

celery = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

#Aditionals Celery configuration
celery.conf.update(
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_queues=task_queues,
)

@celery.task(bind=True)
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

# Example of a task that simulates failure and retries
# Countdown is set to 5 seconds before retrying, and it will retry up to 3 times before giving up.
@celery.task(bind=True, max_retries=3)
def unstable_task(self):
    try:
        raise Exception("fail")
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)



@celery.task(queue="image_queue", routing_key="image.process")
def process_image(image_id: str, max_retries=3):
    db = SessionLocal()
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        return

    try:
        with PILImage.open(image.path) as img:
            resized = img.resize((800, 600))
            thumb = img.copy()
            thumb.thumbnail((200, 200))

            processed_path = os.path.join(PROCESSED_DIR, image.filename)
            resized.save(processed_path)

            image.processed_path = processed_path
            image.status = "SUCCESS"
            db.commit()
    except Exception as e:
        image.status = "FAILURE"
        db.commit()
        print(f"Error procesando imagen {image.id}: {e}")

    finally:
        db.close()

#captura todos los mails que manda la app
@celery.task(queue="email_queue")
def send_email(to, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.MAIL_FROM
    msg["To"] = to

    with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
        server.send_message(msg)
