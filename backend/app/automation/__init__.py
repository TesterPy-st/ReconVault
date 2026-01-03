"""
ReconVault Automation Module

Handles async task orchestration with Celery.
"""

from app.automation.celery_config import celery_app
from app.automation.celery_tasks import (cleanup_old_results,
                                         collect_darkweb_osint,
                                         collect_domain_osint,
                                         collect_email_osint,
                                         collect_geo_osint, collect_ip_osint,
                                         collect_media_osint,
                                         collect_social_osint,
                                         collect_web_osint,
                                         full_reconnaissance, health_check,
                                         queue_collection,
                                         queue_multiple_collections)

__all__ = [
    # Celery app
    "celery_app",
    # Celery tasks
    "collect_web_osint",
    "collect_social_osint",
    "collect_domain_osint",
    "collect_ip_osint",
    "collect_email_osint",
    "collect_media_osint",
    "collect_darkweb_osint",
    "collect_geo_osint",
    "full_reconnaissance",
    "cleanup_old_results",
    "health_check",
    # Helper functions
    "queue_collection",
    "queue_multiple_collections",
]
