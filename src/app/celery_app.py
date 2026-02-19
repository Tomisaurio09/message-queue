from celery import Celery


celery = Celery(
    "worker",
    broker="amqp://guest:guest@rabbitmq:5672//",
    backend="rpc://"
)


@celery.task(bind=True)
def add(self, x, y):
    return x + y
