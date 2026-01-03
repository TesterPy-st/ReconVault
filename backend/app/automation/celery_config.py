"""
Celery Configuration

Configuration for async task queue using Redis as broker and backend.
"""

import os

from celery import Celery
from celery.schedules import crontab

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = os.getenv("REDIS_DB", "0")
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# Create Celery app
celery_app = Celery(
    "reconvault",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "app.automation.celery_tasks",
    ],
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Result backend settings
    result_expires=86400,  # 24 hours
    result_backend_transport_options={
        "retry_policy": {
            "timeout": 5.0,
        }
    },
    # Task execution settings
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    # Task routing
    task_routes={
        "app.automation.celery_tasks.collect_web_osint": {"queue": "web"},
        "app.automation.celery_tasks.collect_social_osint": {"queue": "social"},
        "app.automation.celery_tasks.collect_domain_osint": {"queue": "domain"},
        "app.automation.celery_tasks.collect_ip_osint": {"queue": "ip"},
        "app.automation.celery_tasks.collect_email_osint": {"queue": "email"},
        "app.automation.celery_tasks.collect_media_osint": {"queue": "media"},
        "app.automation.celery_tasks.collect_darkweb_osint": {"queue": "darkweb"},
        "app.automation.celery_tasks.collect_geo_osint": {"queue": "geo"},
        "app.automation.celery_tasks.full_reconnaissance": {"queue": "full"},
    },
    # Task timeouts
    task_soft_time_limit=1800,  # 30 minutes soft limit
    task_time_limit=3600,  # 1 hour hard limit
    # Retry settings
    task_default_retry_delay=60,
    task_max_retries=3,
    task_autoretry_for=(Exception,),
    # Worker settings
    worker_concurrency=4,
    worker_max_tasks_per_child=1000,
    # Beat scheduler for periodic tasks
    beat_schedule={
        # Cleanup old results (daily at midnight)
        "cleanup-old-results": {
            "task": "app.automation.celery_tasks.cleanup_old_results",
            "schedule": crontab(hour=0, minute=0),
        },
        # Health check (every 5 minutes)
        "health-check": {
            "task": "app.automation.celery_tasks.health_check",
            "schedule": crontab(minute="*/5"),
        },
    },
)

# Optional: Configure specific queues
# celery_app.conf.task_queues = (
#     Queue("web", routing_key="web"),
#     Queue("social", routing_key="social"),
#     Queue("domain", routing_key="domain"),
#     Queue("ip", routing_key="ip"),
#     Queue("email", routing_key="email"),
#     Queue("media", routing_key="media"),
#     Queue("darkweb", routing_key="darkweb"),
#     Queue("geo", routing_key="geo"),
#     Queue("full", routing_key="full"),
# )
