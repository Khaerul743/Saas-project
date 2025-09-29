from celery import Celery

from app.configs.config import settings

celery_app = Celery(
    "saas_backend",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Jakarta",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=25 * 60,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    task_routes={
        "app.tasks.agent_task.*": {"queue": "queue_agent_task"},
    },
    task_default_queue="default",
)

# Import tasks to ensure they are registered
from app.tasks import (
    agent_task,  # noqa: F401
    test_task,  # noqa: F401
)

# Auto-discover tasks from the app.tasks module
celery_app.autodiscover_tasks(["app.tasks"])
