from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "cinema_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Kyiv',
    enable_utc=True,
)

celery_app.autodiscover_tasks(['app.services'])