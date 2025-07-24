from celery import Celery
from celery.schedules import crontab

from apps.settings.config import get_settings

settings = get_settings()

celery_app = Celery(
    "station_tasks",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/1",
    include=["apps.celery.tasks"],  # путь до tasks
)

celery_app.conf.timezone = "UTC"
celery_app.conf.beat_schedule = {
    "check-all-stations-every-2-minutes": {
        "task": "check_all_stations_availability",
        "schedule": crontab(minute="*/1"),
    }
}
