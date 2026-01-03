"""
Celery Configuration for ReconVault OSINT Pipeline

This module provides Celery configuration for asynchronous task processing
of OSINT collection tasks across all collector types.
"""

import os
from celery import Celery
from celery.schedules import crontab
from datetime import timedelta

# Build paths
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Initialize Celery app
app = Celery('reconvault')

# Configure Celery
app.conf.update(
    # Broker settings
    broker_url=CELERY_BROKER_URL,
    result_backend=CELERY_RESULT_BACKEND,
    
    # Task serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Timezone settings
    enable_utc=True,
    timezone='UTC',
    
    # Task settings
    task_track_started=True,
    task_send_sent_event=True,
    result_expires=timedelta(hours=24),  # Results expire after 24 hours
    
    # Worker settings
    worker_prefetch_multiplier=1,  # Fair distribution of tasks
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks
    worker_pool_restarts=True,
    
    # Retry settings
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,
    broker_connection_retry=False,  # Disable for development
    
    # Performance settings
    worker_hijack_root_logger=False,  # Let our logger handle logging
    worker_redirect_stdouts=False,
    
    # Routing settings
    task_default_queue='osint_default',
    task_queues={
        'osint_web': {
            'exchange': 'osint',
            'exchange_type': 'direct',
            'routing_key': 'osint.web',
            'priority': 5
        },
        'osint_social': {
            'exchange': 'osint',
            'exchange_type': 'direct',
            'routing_key': 'osint.social',
            'priority': 5
        },
        'osint_domain': {
            'exchange': 'osint',
            'exchange_type': 'direct',
            'routing_key': 'osint.domain',
            'priority': 7
        },
        'osint_ip': {
            'exchange': 'osint',
            'exchange_type': 'direct',
            'routing_key': 'osint.ip',
            'priority': 6
        },
        'osint_email': {
            'exchange': 'osint',
            'exchange_type': 'direct',
            'routing_key': 'osint.email',
            'priority': 8
        },
        'osint_media': {
            'exchange': 'osint',
            'exchange_type': 'direct',
            'routing_key': 'osint.media',
            'priority': 4
        },
        'osint_darkweb': {
            'exchange': 'osint',
            'exchange_type': 'direct',
            'routing_key': 'osint.darkweb',
            'priority': 3
        },
        'osint_geo': {
            'exchange': 'osint',
            'exchange_type': 'direct',
            'routing_key': 'osint.geo',
            'priority': 5
        },
        'osint_high_priority': {
            'exchange': 'osint',
            'exchange_type': 'direct',
            'routing_key': 'osint.priority.high',
            'priority': 10
        }
    },
    
    # Task timeouts (30 minutes default, varies by collector)
    task_time_limit=1800,  # 30 minutes
    task_soft_time_limit=1500,  # 25 minutes
    
    # Retry policy
    task_annotations={
        '*': {
            'autoretry_for': (Exception,),
            'retry_backtrade': True,
            'retry_backtrade_max': 3600,  # 1 hour max backoff
            'retry_kwargs': {'max_retries': 3}
        }
    }
)

# Beat schedule for periodic tasks
app.conf.beat_schedule = {
    'cleanup-obsolete-tasks': {
        'task': 'app.automation.celery_tasks.cleanup_obsolete_results',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
        'options': {'queue': 'osint_default'}
    },
    'verify-tor-connection': {
        'task': 'app.automation.celery_tasks.verify_tor_connection',
        'schedule': crontab(hour='*/6', minute=0),  # Every 6 hours
        'options': {'queue': 'osint_darkweb'}
    }
}

# Import tasks
try:
    from . import celery_tasks  # noqa
except ImportError:
    # Tasks may not be importable during initial setup
    pass

def get_task_queue(collector_type: str) -> str:
    """Get appropriate queue name for collector type"""
    queue_mapping = {
        'web': 'osint_web',
        'social': 'osint_social',
        'domain': 'osint_domain',
        'ip': 'osint_ip',
        'email': 'osint_email',
        'media': 'osint_media',
        'darkweb': 'osint_darkweb',
        'geo': 'osint_geo'
    }
    return queue_mapping.get(collector_type, 'osint_default')

def get_collector_priority(collector_type: str) -> int:
    """Get task priority for collector type (0-10, higher = more priority)"""
    priority_mapping = {
        'email': 8,      # High priority
        'domain': 7,     # High priority
        'ip': 6,         # Medium-high
        'web': 5,        # Medium
        'social': 5,     # Medium
        'geo': 5,        # Medium
        'media': 4,      # Medium-low
        'darkweb': 3     # Low (slow)
    }
    return priority_mapping.get(collector_type, 5)