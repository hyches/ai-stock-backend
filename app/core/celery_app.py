"""
Celery application configuration for background tasks
"""
from celery import Celery
from celery.schedules import crontab
from app.config.settings import get_settings

settings = get_settings()

# Initialize Celery app
celery_app = Celery(
    "ai_stock_backend",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.policy_tracker",
        "app.tasks.ml_training",
        "app.tasks.alerts",
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Scheduled tasks (Celery Beat)
celery_app.conf.beat_schedule = {
    "check-policy-updates-every-30-minutes": {
        "task": "app.tasks.policy_tracker.check_policy_updates",
        "schedule": crontab(minute="*/30"),  # Every 30 minutes
    },
    "train-ml-models-daily": {
        "task": "app.tasks.ml_training.train_all_models",
        "schedule": crontab(hour=2, minute=0),  # 2 AM daily
    },
    "check-price-alerts-every-minute": {
        "task": "app.tasks.alerts.check_price_alerts",
        "schedule": crontab(minute="*/1"),  # Every minute
    },
}

# Task routes (optional - for multiple queues)
celery_app.conf.task_routes = {
    "app.tasks.policy_tracker.*": {"queue": "policy"},
    "app.tasks.ml_training.*": {"queue": "ml"},
    "app.tasks.alerts.*": {"queue": "alerts"},
}
