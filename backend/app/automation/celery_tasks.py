"""
Celery Tasks

Async tasks for OSINT collection using Celery and Redis.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from celery import Task
from loguru import logger

from app.automation.celery_config import celery_app
from app.collectors import (CollectorConfig, DarkWebCollector, DataType,
                            DomainCollector, EmailCollector, GeoCollector,
                            IPCollector, MediaCollector, SocialCollector,
                            WebCollector)
from app.services.collection_pipeline_service import CollectionPipelineService
from app.services.normalization_service import NormalizationService
from app.services.risk_analysis_service import RiskAnalysisService

# Configure Celery logger
celery_logger = logging.getLogger("celery")
celery_logger.setLevel(logging.INFO)


class AsyncTaskContext:
    """Context manager for async tasks in Celery"""

    def __enter__(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        return self.loop

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.loop.close()


@celery_app.task(bind=True, name="app.automation.celery_tasks.collect_web_osint")
def collect_web_osint(self: Task, target: str, task_id: str) -> Dict[str, Any]:
    """
    Queue web OSINT collection task.

    Args:
        target: Target URL or domain
        task_id: Task ID for tracking

    Returns:
        Collection result
    """
    logger.info(f"Web OSINT task started for {target} (task_id: {task_id})")

    try:
        with AsyncTaskContext() as loop:
            config = CollectorConfig(target=target, data_type=DataType.URL)
            collector = WebCollector(config)

            async def run_collector():
                async with collector:
                    result = await collector.execute()
                    return result

            result = loop.run_until_complete(run_collector())

            logger.info(f"Web OSINT task completed for {target}: {result.success}")
            return {
                "success": result.success,
                "data": result.data,
                "errors": result.errors,
                "risk_level": result.risk_level.value,
                "collection_time": result.collection_time,
            }

    except Exception as e:
        logger.exception(f"Web OSINT task failed for {target}: {e}")
        return {
            "success": False,
            "errors": [str(e)],
            "risk_level": "INFO",
            "collection_time": 0,
        }


@celery_app.task(bind=True, name="app.automation.celery_tasks.collect_social_osint")
def collect_social_osint(self: Task, target: str, task_id: str) -> Dict[str, Any]:
    """
    Queue social media OSINT collection task.

    Args:
        target: Target username or social URL
        task_id: Task ID for tracking

    Returns:
        Collection result
    """
    logger.info(f"Social OSINT task started for {target} (task_id: {task_id})")

    try:
        with AsyncTaskContext() as loop:
            config = CollectorConfig(target=target, data_type=DataType.USERNAME)
            collector = SocialCollector(config)

            async def run_collector():
                async with collector:
                    result = await collector.execute()
                    return result

            result = loop.run_until_complete(run_collector())

            logger.info(f"Social OSINT task completed for {target}: {result.success}")
            return {
                "success": result.success,
                "data": result.data,
                "errors": result.errors,
                "risk_level": result.risk_level.value,
                "collection_time": result.collection_time,
            }

    except Exception as e:
        logger.exception(f"Social OSINT task failed for {target}: {e}")
        return {
            "success": False,
            "errors": [str(e)],
            "risk_level": "INFO",
            "collection_time": 0,
        }


@celery_app.task(bind=True, name="app.automation.celery_tasks.collect_domain_osint")
def collect_domain_osint(self: Task, target: str, task_id: str) -> Dict[str, Any]:
    """
    Queue domain OSINT collection task.

    Args:
        target: Target domain
        task_id: Task ID for tracking

    Returns:
        Collection result
    """
    logger.info(f"Domain OSINT task started for {target} (task_id: {task_id})")

    try:
        with AsyncTaskContext() as loop:
            config = CollectorConfig(target=target, data_type=DataType.DOMAIN)
            collector = DomainCollector(config)

            async def run_collector():
                async with collector:
                    result = await collector.execute()
                    return result

            result = loop.run_until_complete(run_collector())

            logger.info(f"Domain OSINT task completed for {target}: {result.success}")
            return {
                "success": result.success,
                "data": result.data,
                "errors": result.errors,
                "risk_level": result.risk_level.value,
                "collection_time": result.collection_time,
            }

    except Exception as e:
        logger.exception(f"Domain OSINT task failed for {target}: {e}")
        return {
            "success": False,
            "errors": [str(e)],
            "risk_level": "INFO",
            "collection_time": 0,
        }


@celery_app.task(bind=True, name="app.automation.celery_tasks.collect_ip_osint")
def collect_ip_osint(self: Task, target: str, task_id: str) -> Dict[str, Any]:
    """
    Queue IP address OSINT collection task.

    Args:
        target: Target IP address
        task_id: Task ID for tracking

    Returns:
        Collection result
    """
    logger.info(f"IP OSINT task started for {target} (task_id: {task_id})")

    try:
        with AsyncTaskContext() as loop:
            config = CollectorConfig(target=target, data_type=DataType.IP)
            collector = IPCollector(config)

            async def run_collector():
                async with collector:
                    result = await collector.execute()
                    return result

            result = loop.run_until_complete(run_collector())

            logger.info(f"IP OSINT task completed for {target}: {result.success}")
            return {
                "success": result.success,
                "data": result.data,
                "errors": result.errors,
                "risk_level": result.risk_level.value,
                "collection_time": result.collection_time,
            }

    except Exception as e:
        logger.exception(f"IP OSINT task failed for {target}: {e}")
        return {
            "success": False,
            "errors": [str(e)],
            "risk_level": "INFO",
            "collection_time": 0,
        }


@celery_app.task(bind=True, name="app.automation.celery_tasks.collect_email_osint")
def collect_email_osint(self: Task, target: str, task_id: str) -> Dict[str, Any]:
    """
    Queue email OSINT collection task.

    Args:
        target: Target email address
        task_id: Task ID for tracking

    Returns:
        Collection result
    """
    logger.info(f"Email OSINT task started for {target} (task_id: {task_id})")

    try:
        with AsyncTaskContext() as loop:
            config = CollectorConfig(target=target, data_type=DataType.EMAIL)
            collector = EmailCollector(config)

            async def run_collector():
                async with collector:
                    result = await collector.execute()
                    return result

            result = loop.run_until_complete(run_collector())

            logger.info(f"Email OSINT task completed for {target}: {result.success}")
            return {
                "success": result.success,
                "data": result.data,
                "errors": result.errors,
                "risk_level": result.risk_level.value,
                "collection_time": result.collection_time,
            }

    except Exception as e:
        logger.exception(f"Email OSINT task failed for {target}: {e}")
        return {
            "success": False,
            "errors": [str(e)],
            "risk_level": "INFO",
            "collection_time": 0,
        }


@celery_app.task(bind=True, name="app.automation.celery_tasks.collect_media_osint")
def collect_media_osint(self: Task, target: str, task_id: str) -> Dict[str, Any]:
    """
    Queue media OSINT collection task.

    Args:
        target: Target media URL
        task_id: Task ID for tracking

    Returns:
        Collection result
    """
    logger.info(f"Media OSINT task started for {target} (task_id: {task_id})")

    try:
        with AsyncTaskContext() as loop:
            config = CollectorConfig(target=target, data_type=DataType.TEXT)
            collector = MediaCollector(config)

            async def run_collector():
                async with collector:
                    result = await collector.execute()
                    return result

            result = loop.run_until_complete(run_collector())

            logger.info(f"Media OSINT task completed for {target}: {result.success}")
            return {
                "success": result.success,
                "data": result.data,
                "errors": result.errors,
                "risk_level": result.risk_level.value,
                "collection_time": result.collection_time,
            }

    except Exception as e:
        logger.exception(f"Media OSINT task failed for {target}: {e}")
        return {
            "success": False,
            "errors": [str(e)],
            "risk_level": "INFO",
            "collection_time": 0,
        }


@celery_app.task(bind=True, name="app.automation.celery_tasks.collect_darkweb_osint")
def collect_darkweb_osint(self: Task, target: str, task_id: str) -> Dict[str, Any]:
    """
    Queue dark web OSINT collection task.

    Args:
        target: Target to search for
        task_id: Task ID for tracking

    Returns:
        Collection result
    """
    logger.info(f"Dark web OSINT task started for {target} (task_id: {task_id})")

    try:
        with AsyncTaskContext() as loop:
            config = CollectorConfig(target=target, data_type=DataType.TEXT)
            collector = DarkWebCollector(config)

            async def run_collector():
                async with collector:
                    result = await collector.execute()
                    return result

            result = loop.run_until_complete(run_collector())

            logger.info(f"Dark web OSINT task completed for {target}: {result.success}")
            return {
                "success": result.success,
                "data": result.data,
                "errors": result.errors,
                "risk_level": result.risk_level.value,
                "collection_time": result.collection_time,
            }

    except Exception as e:
        logger.exception(f"Dark web OSINT task failed for {target}: {e}")
        return {
            "success": False,
            "errors": [str(e)],
            "risk_level": "INFO",
            "collection_time": 0,
        }


@celery_app.task(bind=True, name="app.automation.celery_tasks.collect_geo_osint")
def collect_geo_osint(self: Task, target: str, task_id: str) -> Dict[str, Any]:
    """
    Queue geolocation OSINT collection task.

    Args:
        target: Target (address or coordinates)
        task_id: Task ID for tracking

    Returns:
        Collection result
    """
    logger.info(f"Geo OSINT task started for {target} (task_id: {task_id})")

    try:
        with AsyncTaskContext() as loop:
            config = CollectorConfig(target=target, data_type=DataType.TEXT)
            collector = GeoCollector(config)

            async def run_collector():
                async with collector:
                    result = await collector.execute()
                    return result

            result = loop.run_until_complete(run_collector())

            logger.info(f"Geo OSINT task completed for {target}: {result.success}")
            return {
                "success": result.success,
                "data": result.data,
                "errors": result.errors,
                "risk_level": result.risk_level.value,
                "collection_time": result.collection_time,
            }

    except Exception as e:
        logger.exception(f"Geo OSINT task failed for {target}: {e}")
        return {
            "success": False,
            "errors": [str(e)],
            "risk_level": "INFO",
            "collection_time": 0,
        }


@celery_app.task(bind=True, name="app.automation.celery_tasks.full_reconnaissance")
def full_reconnaissance(
    self: Task,
    target: str,
    task_id: str,
    include_dark_web: bool = False,
    include_media: bool = False,
) -> Dict[str, Any]:
    """
    Run full reconnaissance with all applicable collectors.

    Args:
        target: Target to collect
        task_id: Task ID for tracking
        include_dark_web: Include dark web collection
        include_media: Include media collection

    Returns:
        Full collection result
    """
    logger.info(f"Full reconnaissance started for {target} (task_id: {task_id})")

    try:
        with AsyncTaskContext() as loop:
            # Initialize pipeline service
            pipeline = CollectionPipelineService()

            async def run_pipeline():
                await pipeline.initialize()
                result = await pipeline.start_collection_task(
                    target=target,
                    include_dark_web=include_dark_web,
                    include_media=include_media,
                )
                return result

            result = loop.run_until_complete(run_pipeline())

            logger.info(
                f"Full reconnaissance completed for {target}: {result.get('status')}"
            )

            return result

    except Exception as e:
        logger.exception(f"Full reconnaissance failed for {target}: {e}")
        return {
            "task_id": task_id,
            "target": target,
            "status": "FAILED",
            "errors": [str(e)],
        }


@celery_app.task(bind=True, name="app.automation.celery_tasks.cleanup_old_results")
def cleanup_old_results(self: Task) -> Dict[str, Any]:
    """
    Cleanup old Celery results from Redis.

    Returns:
        Cleanup result
    """
    logger.info("Starting cleanup of old results")

    try:
        # This is a placeholder - actual implementation would:
        # 1. Query Redis for old results
        # 2. Delete results older than retention period
        # 3. Return count of deleted items

        logger.info("Cleanup completed")
        return {"success": True, "deleted_count": 0}

    except Exception as e:
        logger.exception(f"Cleanup failed: {e}")
        return {"success": False, "errors": [str(e)]}


@celery_app.task(bind=True, name="app.automation.celery_tasks.health_check")
def health_check(self: Task) -> Dict[str, Any]:
    """
    Health check for Celery workers.

    Returns:
        Health status
    """
    logger.info("Running health check")

    try:
        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "worker": str(self.request.hostname),
            "status": "healthy",
        }

    except Exception as e:
        logger.exception(f"Health check failed: {e}")
        return {"success": False, "errors": [str(e)], "status": "unhealthy"}


# Helper function to queue collection tasks
def queue_collection(
    target: str, collection_type: str, task_id: str, **kwargs
) -> Optional[str]:
    """
    Queue a collection task.

    Args:
        target: Target to collect
        collection_type: Type of collection (web, social, domain, ip, email, media, darkweb, geo)
        task_id: Task ID for tracking
        **kwargs: Additional arguments

    Returns:
        Celery task ID or None
    """
    task_map = {
        "web": collect_web_osint,
        "social": collect_social_osint,
        "domain": collect_domain_osint,
        "ip": collect_ip_osint,
        "email": collect_email_osint,
        "media": collect_media_osint,
        "darkweb": collect_darkweb_osint,
        "geo": collect_geo_osint,
        "full": full_reconnaissance,
    }

    task_func = task_map.get(collection_type)

    if not task_func:
        logger.error(f"Unknown collection type: {collection_type}")
        return None

    if collection_type == "full":
        return task_func.delay(target, task_id, **kwargs).id
    else:
        return task_func.delay(target, task_id).id


def queue_multiple_collections(
    target: str, collection_types: List[str], task_id: str, **kwargs
) -> List[str]:
    """
    Queue multiple collection tasks.

    Args:
        target: Target to collect
        collection_types: List of collection types
        task_id: Task ID for tracking
        **kwargs: Additional arguments

    Returns:
        List of Celery task IDs
    """
    task_ids = []

    for collection_type in collection_types:
        task_id = queue_collection(target, collection_type, task_id, **kwargs)
        if task_id:
            task_ids.append(task_id)

    return task_ids


@celery_app.task(bind=True, name="app.automation.celery_tasks.calculate_risks_async")
def calculate_risks_async(self: Task, entity_ids: List[int]) -> Dict[str, Any]:
    """
    Calculate risk scores for entities asynchronously.

    Args:
        entity_ids: List of entity IDs to process

    Returns:
        Calculation results
    """
    logger.info(f"Async risk calculation started for {len(entity_ids)} entities")

    try:
        from app.database import get_db_session
        from app.models.entity import Entity
        from app.risk_engine.risk_analyzer import RiskAnalyzer

        # Get database session
        db = next(get_db_session())

        try:
            # Initialize risk analyzer
            analyzer = RiskAnalyzer(db=db)

            # Process entities
            processed = 0
            errors = []

            for entity_id in entity_ids:
                try:
                    entity = db.query(Entity).filter(Entity.id == entity_id).first()

                    if entity:
                        entity_dict = entity.to_dict()
                        risk_assessment = analyzer.calculate_entity_risk(entity_dict)

                        # Update entity risk score
                        entity.risk_score = risk_assessment["risk_score"]
                        processed += 1
                    else:
                        errors.append(f"Entity {entity_id} not found")

                except Exception as e:
                    logger.error(f"Error processing entity {entity_id}: {e}")
                    errors.append(f"Entity {entity_id}: {str(e)}")

            # Commit changes
            db.commit()

            logger.info(f"Async risk calculation completed: {processed} entities processed")

            return {
                "success": True,
                "entities_processed": processed,
                "total_entities": len(entity_ids),
                "errors": errors,
                "timestamp": datetime.utcnow().isoformat(),
            }

        finally:
            db.close()

    except Exception as e:
        logger.exception(f"Async risk calculation failed: {e}")
        return {
            "success": False,
            "errors": [str(e)],
            "timestamp": datetime.utcnow().isoformat(),
        }


@celery_app.task(bind=True, name="app.automation.celery_tasks.periodic_risk_update")
def periodic_risk_update(self: Task) -> Dict[str, Any]:
    """
    Periodic task to update risk scores for all active entities.

    Returns:
        Update results
    """
    logger.info("Starting periodic risk update")

    try:
        from app.database import get_db_session
        from app.models.entity import Entity
        from app.risk_engine.risk_analyzer import RiskAnalyzer

        # Get database session
        db = next(get_db_session())

        try:
            # Get all active entities
            entities = db.query(Entity).filter(Entity.is_active == True).all()

            logger.info(f"Updating risks for {len(entities)} entities")

            # Initialize risk analyzer
            analyzer = RiskAnalyzer(db=db)

            # Process entities in batches
            batch_size = 100
            processed = 0

            for i in range(0, len(entities), batch_size):
                batch = entities[i : i + batch_size]

                for entity in batch:
                    try:
                        entity_dict = entity.to_dict()
                        risk_assessment = analyzer.calculate_entity_risk(entity_dict)
                        entity.risk_score = risk_assessment["risk_score"]
                        processed += 1
                    except Exception as e:
                        logger.error(f"Error processing entity {entity.id}: {e}")

                # Commit batch
                db.commit()
                logger.info(f"Processed {processed}/{len(entities)} entities")

            logger.info(f"Periodic risk update completed: {processed} entities updated")

            return {
                "success": True,
                "entities_updated": processed,
                "timestamp": datetime.utcnow().isoformat(),
            }

        finally:
            db.close()

    except Exception as e:
        logger.exception(f"Periodic risk update failed: {e}")
        return {"success": False, "errors": [str(e)], "timestamp": datetime.utcnow().isoformat()}
