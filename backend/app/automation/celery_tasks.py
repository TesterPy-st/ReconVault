"""
Celery Tasks for ReconVault OSINT Pipeline

This module provides Celery task definitions for all OSINT collectors,
orchestrating collection, normalization, risk analysis, and database synchronization.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from celery import Task, shared_task
from datetime import datetime
import traceback

from .celery_config import app, get_task_queue, get_collector_priority
from ..collectors import (
    WebCollector, SocialCollector, DomainCollector, IPCollector,
    EmailCollector, MediaCollector, DarkWebCollector, GeoCollector,
    CollectorConfig
)

# Configure logging
logger = logging.getLogger(__name__)

# Base task class with common functionality
class OSINTBaseTask(Task):
    """Base task class for OSINT collection tasks"""
    
    abstract = True
    
    def __init__(self):
        self.max_retries = 3
        self.retry_backoff = True
        self.retry_backoff_max = 1800  # 30 minutes

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Log task failures"""
        logger.error(f"Task {task_id} failed: {exc}")
        logger.error(f"Traceback: {einfo}")
        
        # Store failure in metadata if result backend supports it
        if hasattr(self, 'meta'):
            self.meta['status'] = 'FAILED'
            self.meta['error'] = str(exc)
            self.meta['completed_at'] = datetime.utcnow().isoformat()

    def on_success(self, retval, task_id, args, kwargs):
        """Log task success"""
        logger.info(f"Task {task_id} completed successfully")

        # Update metadata
        if hasattr(self, 'meta'):
            self.meta['status'] = 'COMPLETED'
            self.meta['completed_at'] = datetime.utcnow().isoformat()

# Individual collector tasks
@app.task(bind=True, base=OSINTBaseTask, queue=get_task_queue('web'))
def collect_web_osint(self, target: str, **kwargs) -> Dict[str, Any]:
    """Task for web OSINT collection"""
    try:
        logger.info(f"Starting web collection task for: {target}")
        
        # Update task metadata
        self.meta = {
            'task_id': self.request.id,
            'target': target,
            'collector_type': 'web',
            'status': 'PROCESSING',
            'started_at': datetime.utcnow().isoformat()
        }
        self.update_state(state='PROCESSING', meta=self.meta)
        
        # Create collector config
        config = CollectorConfig(
            target=target,
            data_type='domain',
            timeout=kwargs.get('timeout', 180),
            max_retries=kwargs.get('max_retries', 3),
            rate_limit=kwargs.get('rate_limit', 1.0),
            respect_robots_txt=kwargs.get('respect_robots_txt', True)
        )
        
        # Run collection
        async def run_collection():
            async with WebCollector(config) as collector:
                return await collector.execute()
        
        entities, validation_errors = asyncio.run(run_collection())
        
        # Prepare results
        results = {
            'task_id': self.request.id,
            'target': target,
            'collector_type': 'web',
            'entities_created': len(entities),
            'validation_errors': len(validation_errors),
            'entities': entities,
            'errors': validation_errors,
            'status': 'COMPLETED',
            'collection_stats': {
                'entities_found': len(entities),
                'errors_count': len(validation_errors)
            }
        }
        
        logger.info(f"Web collection completed: {len(entities)} entities found")
        return results
        
    except Exception as e:
        logger.error(f"Web collection failed for {target}: {e}")
        logger.error(traceback.format_exc())
        raise self.retry(exc=e)

@app.task(bind=True, base=OSINTBaseTask, queue=get_task_queue('social'))
def collect_social_osint(self, target: str, **kwargs) -> Dict[str, Any]:
    """Task for social media OSINT collection"""
    try:
        logger.info(f"Starting social collection task for: {target}")
        
        self.meta = {
            'task_id': self.request.id,
            'target': target,
            'collector_type': 'social',
            'status': 'PROCESSING',
            'started_at': datetime.utcnow().isoformat()
        }
        self.update_state(state='PROCESSING', meta=self.meta)
        
        config = CollectorConfig(
            target=target,
            data_type='social',
            timeout=kwargs.get('timeout', 150),
            max_retries=kwargs.get('max_retries', 3),
            rate_limit=kwargs.get('rate_limit', 2.0)
        )
        
        async def run_collection():
            async with SocialCollector(config) as collector:
                return await collector.execute()
        
        entities, validation_errors = asyncio.run(run_collection())
        
        results = {
            'task_id': self.request.id,
            'target': target,
            'collector_type': 'social',
            'entities_created': len(entities),
            'validation_errors': len(validation_errors),
            'entities': entities,
            'errors': validation_errors,
            'status': 'COMPLETED'
        }
        
        logger.info(f"Social collection completed: {len(entities)} entities found")
        return results
        
    except Exception as e:
        logger.error(f"Social collection failed for {target}: {e}")
        raise self.retry(exc=e)

@app.task(bind=True, base=OSINTBaseTask, queue=get_task_queue('domain'))
def collect_domain_osint(self, target: str, **kwargs) -> Dict[str, Any]:
    """Task for domain OSINT collection"""
    try:
        logger.info(f"Starting domain collection task for: {target}")
        
        self.meta = {
            'task_id': self.request.id,
            'target': target,
            'collector_type': 'domain',
            'status': 'PROCESSING',
            'started_at': datetime.utcnow().isoformat()
        }
        self.update_state(state='PROCESSING', meta=self.meta)
        
        config = CollectorConfig(
            target=target,
            data_type='domain',
            timeout=kwargs.get('timeout', 120),
            max_retries=kwargs.get('max_retries', 3),
            rate_limit=kwargs.get('rate_limit', 1.5)
        )
        
        async def run_collection():
            async with DomainCollector(config) as collector:
                return await collector.execute()
        
        entities, validation_errors = asyncio.run(run_collection())
        
        results = {
            'task_id': self.request.id,
            'target': target,
            'collector_type': 'domain',
            'entities_created': len(entities),
            'validation_errors': len(validation_errors),
            'entities': entities,
            'errors': validation_errors,
            'status': 'COMPLETED'
        }
        
        logger.info(f"Domain collection completed: {len(entities)} entities found")
        return results
        
    except Exception as e:
        logger.error(f"Domain collection failed for {target}: {e}")
        raise self.retry(exc=e)

@app.task(bind=True, base=OSINTBaseTask, queue=get_task_queue('ip'))
def collect_ip_osint(self, target: str, **kwargs) -> Dict[str, Any]:
    """Task for IP OSINT collection"""
    try:
        logger.info(f"Starting IP collection task for: {target}")
        
        self.meta = {
            'task_id': self.request.id,
            'target': target,
            'collector_type': 'ip',
            'status': 'PROCESSING',
            'started_at': datetime.utcnow().isoformat()
        }
        self.update_state(state='PROCESSING', meta=self.meta)
        
        config = CollectorConfig(
            target=target,
            data_type='ip',
            timeout=kwargs.get('timeout', 200),
            max_retries=kwargs.get('max_retries', 3),
            rate_limit=kwargs.get('rate_limit', 1.0)
        )
        
        async def run_collection():
            async with IPCollector(config) as collector:
                return await collector.execute()
        
        entities, validation_errors = asyncio.run(run_collection())
        
        results = {
            'task_id': self.request.id,
            'target': target,
            'collector_type': 'ip',
            'entities_created': len(entities),
            'validation_errors': len(validation_errors),
            'entities': entities,
            'errors': validation_errors,
            'status': 'COMPLETED'
        }
        
        logger.info(f"IP collection completed: {len(entities)} entities found")
        return results
        
    except Exception as e:
        logger.error(f"IP collection failed for {target}: {e}")
        raise self.retry(exc=e)

@app.task(bind=True, base=OSINTBaseTask, queue=get_task_queue('email'))
def collect_email_osint(self, target: str, **kwargs) -> Dict[str, Any]:
    """Task for email OSINT collection"""
    try:
        logger.info(f"Starting email collection task for: {target}")
        
        self.meta = {
            'task_id': self.request.id,
            'target': target,
            'collector_type': 'email',
            'status': 'PROCESSING',
            'started_at': datetime.utcnow().isoformat()
        }
        self.update_state(state='PROCESSING', meta=self.meta)
        
        config = CollectorConfig(
            target=target,
            data_type='email',
            timeout=kwargs.get('timeout', 100),
            max_retries=kwargs.get('max_retries', 3),
            rate_limit=kwargs.get('rate_limit', 3.0)
        )
        
        async def run_collection():
            async with EmailCollector(config) as collector:
                return await collector.execute()
        
        entities, validation_errors = asyncio.run(run_collection())
        
        results = {
            'task_id': self.request.id,
            'target': target,
            'collector_type': 'email',
            'entities_created': len(entities),
            'validation_errors': len(validation_errors),
            'entities': entities,
            'errors': validation_errors,
            'status': 'COMPLETED'
        }
        
        logger.info(f"Email collection completed: {len(entities)} entities found")
        return results
        
    except Exception as e:
        logger.error(f"Email collection failed for {target}: {e}")
        raise self.retry(exc=e)

@app.task(bind=True, base=OSINTBaseTask, queue=get_task_queue('media'))
def collect_media_osint(self, target: str, **kwargs) -> Dict[str, Any]:
    """Task for media OSINT collection"""
    try:
        logger.info(f"Starting media collection task for: {target}")
        
        self.meta = {
            'task_id': self.request.id,
            'target': target,
            'collector_type': 'media',
            'status': 'PROCESSING',
            'started_at': datetime.utcnow().isoformat()
        }
        self.update_state(state='PROCESSING', meta=self.meta)
        
        config = CollectorConfig(
            target=target,
            data_type='media',
            timeout=kwargs.get('timeout', 300),  # Media processing can take longer
            max_retries=kwargs.get('max_retries', 2),
            rate_limit=kwargs.get('rate_limit', 0.5)  # Be gentle with media processing
        )
        
        async def run_collection():
            async with MediaCollector(config) as collector:
                return await collector.execute()
        
        entities, validation_errors = asyncio.run(run_collection())
        
        results = {
            'task_id': self.request.id,
            'target': target,
            'collector_type': 'media',
            'entities_created': len(entities),
            'validation_errors': len(validation_errors),
            'entities': entities,
            'errors': validation_errors,
            'status': 'COMPLETED'
        }
        
        logger.info(f"Media collection completed: {len(entities)} entities found")
        return results
        
    except Exception as e:
        logger.error(f"Media collection failed for {target}: {e}")
        raise self.retry(exc=e)

@app.task(bind=True, base=OSINTBaseTask, queue=get_task_queue('darkweb'))
def collect_darkweb_osint(self, target: str, **kwargs) -> Dict[str, Any]:
    """Task for dark web OSINT collection"""
    try:
        logger.info(f"Starting dark web collection task for: {target}")
        
        self.meta = {
            'task_id': self.request.id,
            'target': target,
            'collector_type': 'darkweb',
            'status': 'PROCESSING',
            'started_at': datetime.utcnow().isoformat()
        }
        self.update_state(state='PROCESSING', meta=self.meta)
        
        config = CollectorConfig(
            target=target,
            data_type='darkweb',
            timeout=kwargs.get('timeout', 240),  # Dark web slower
            max_retries=kwargs.get('max_retries', 2),
            rate_limit=kwargs.get('rate_limit', 0.3),  # Very slow for Tor
            use_proxy=True
        )
        
        async def run_collection():
            async with DarkWebCollector(config) as collector:
                return await collector.execute()
        
        entities, validation_errors = asyncio.run(run_collection())
        
        results = {
            'task_id': self.request.id,
            'target': target,
            'collector_type': 'darkweb',
            'entities_created': len(entities),
            'validation_errors': len(validation_errors),
            'entities': entities,
            'errors': validation_errors,
            'status': 'COMPLETED'
        }
        
        logger.info(f"Dark web collection completed: {len(entities)} entities found")
        return results
        
    except Exception as e:
        logger.error(f"Dark web collection failed for {target}: {e}")
        raise self.retry(exc=e)

@app.task(bind=True, base=OSINTBaseTask, queue=get_task_queue('geo'))
def collect_geo_osint(self, target: str, **kwargs) -> Dict[str, Any]:
    """Task for geolocation OSINT collection"""
    try:
        logger.info(f"Starting geolocation collection task for: {target}")
        
        self.meta = {
            'task_id': self.request.id,
            'target': target,
            'collector_type': 'geo',
            'status': 'PROCESSING',
            'started_at': datetime.utcnow().isoformat()
        }
        self.update_state(state='PROCESSING', meta=self.meta)
        
        config = CollectorConfig(
            target=target,
            data_type='geo',
            timeout=kwargs.get('timeout', 90),
            max_retries=kwargs.get('max_retries', 3),
            rate_limit=kwargs.get('rate_limit', 1.0)
        )
        
        async def run_collection():
            async with GeoCollector(config) as collector:
                return await collector.execute()
        
        entities, validation_errors = asyncio.run(run_collection())
        
        results = {
            'task_id': self.request.id,
            'target': target,
            'collector_type': 'geo',
            'entities_created': len(entities),
            'validation_errors': len(validation_errors),
            'entities': entities,
            'errors': validation_errors,
            'status': 'COMPLETED'
        }
        
        logger.info(f"Geolocation collection completed: {len(entities)} entities found")
        return results
        
    except Exception as e:
        logger.error(f"Geolocation collection failed for {target}: {e}")
        raise self.retry(exc=e)

# Comprehensive collection task
@app.task(bind=True, base=OSINTBaseTask, queue='osint_high_priority')
def full_reconnaissance(self, target: str, collection_types: List[str] = None, **kwargs) -> Dict[str, Any]:
    """Perform full OSINT reconnaissance across multiple collector types"""
    try:
        logger.info(f"Starting full reconnaissance for: {target}")
        
        # Default to all collectors if not specified
        if not collection_types:
            collection_types = ['web', 'social', 'domain', 'ip', 'email', 'media', 'darkweb', 'geo']
        
        self.meta = {
            'task_id': self.request.id,
            'target': target,
            'collector_type': 'full_recon',
            'status': 'PROCESSING',
            'started_at': datetime.utcnow().isoformat(),
            'collectors_pending': len(collection_types),
            'collectors_completed': 0,
            'total_entities': 0
        }
        self.update_state(state='PROCESSING', meta=self.meta)
        
        # Define task mapping
        task_mapping = {
            'web': collect_web_osint.s(target),
            'social': collect_social_osint.s(target),
            'domain': collect_domain_osint.s(target),
            'ip': collect_ip_osint.s(target),
            'email': collect_email_osint.s(target),
            'media': collect_media_osint.s(target) if self._is_media_target(target) else None,
            'darkweb': collect_darkweb_osint.s(target),
            'geo': collect_geo_osint.s(target) if self._is_geo_target(target) else None
        }
        
        # Filter tasks based on target appropriateness
        tasks = []
        for collector_type in collection_types:
            if collector_type in task_mapping and task_mapping[collector_type]:
                tasks.append(task_mapping[collector_type])
        
        if not tasks:
            logger.warning(f"No valid collectors for target: {target}")
            return {
                'task_id': self.request.id,
                'target': target,
                'status': 'COMPLETED',
                'warning': 'No suitable collectors found for target',
                'entities_created': 0
            }
        
        # Execute tasks in parallel
        from celery import group
        job = group(tasks)
        result = job.apply_async()
        
        # Wait for completion with progress tracking
        total_collectors = len(tasks)
        completed_collectors = 0
        all_results = []
        total_entities = 0
        
        # Wait for all sub-tasks to complete
        while not result.ready():
            # Update progress
            completed = sum(1 for r in result.children if r.ready())
            if completed > completed_collectors:
                completed_collectors = completed
                self.meta['collectors_completed'] = completed_collectors
                self.meta['progress_percent'] = (completed_collectors / total_collectors) * 100
                self.update_state(state='PROCESSING', meta=self.meta)
            
            asyncio.run(asyncio.sleep(2))  # Non-blocking sleep
        
        # Process results
        for task_result in result.get():
            if task_result and task_result.get('status') == 'COMPLETED':
                all_results.append(task_result)
                total_entities += task_result.get('entities_created', 0)
        
        # Final metadata update
        self.meta['collectors_completed'] = total_collectors
        self.meta['total_entities'] = total_entities
        self.meta['progress_percent'] = 100
        
        # Deduplicate entities across collectors
        final_results = self._deduplicate_results(all_results)
        
        final_response = {
            'task_id': self.request.id,
            'target': target,
            'collector_type': 'full_recon',
            'status': 'COMPLETED',
            'collectors_used': len(tasks),
            'entities_created': final_results['total_entities'],
            'entities_by_collector': final_results['entity_counts'],
            'sources': final_results['sources'],
            'metadata': self.meta
        }
        
        logger.info(f"Full reconnaissance completed: {final_results['total_entities']} unique entities found")
        return final_response
        
    except Exception as e:
        logger.error(f"Full reconnaissance failed for {target}: {e}")
        logger.error(traceback.format_exc())
        raise self.retry(exc=e)

    @staticmethod
    def _is_media_target(target: str) -> bool:
        """Check if target is a media file or URL"""
        media_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.mp3', '.wav', '.mp4', '.avi', '.mov']
        return any(target.lower().endswith(ext) for ext in media_extensions) or target.startswith('http')
    
    @staticmethod
    def _is_geo_target(target: str) -> bool:
        """Check if target is a location or coordinates"""
        # Check for coordinates pattern
        import re
        coord_pattern = r'[-+]?\d+\.\d+\s*,\s*[-+]?\d+\.\d+'
        
        # Check for address indicators
        address_indicators = ['street', 'avenue', 'road', 'city', 'state', 'country', 'zip']
        
        return bool(re.match(coord_pattern, target.replace(' ', ''))) or \
               any(indicator in target.lower() for indicator in address_indicators)
    
    @staticmethod
    def _deduplicate_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Deduplicate entities across multiple collector results"""
        unique_entities = {}
        entity_counts = {}
        sources = set()
        
        for result in results:
            collector_type = result.get('collector_type', 'unknown')
            entities = result.get('entities', [])
            
            entity_counts[collector_type] = len(entities)
            
            for entity in entities:
                entity_key = f"{entity.get('type')}:{entity.get('value')}"
                
                if entity_key not in unique_entities:
                    unique_entities[entity_key] = entity
                else:
                    # Merge metadata from duplicate entities
                    existing = unique_entities[entity_key]
                    if 'metadata' in entity:
                        if 'metadata' not in existing:
                            existing['metadata'] = {}
                        existing['metadata'].update(entity['metadata'])
                
                if 'source' in entity:
                    sources.add(entity['source'])
        
        return {
            'total_entities': len(unique_entities),
            'entity_counts': entity_counts,
            'sources': list(sources),
            'entities': list(unique_entities.values())
        }

# Utility and maintenance tasks
@app.task(bind=True, queue='osint_default')
def cleanup_obsolete_results(self, max_age_hours: int = 24) -> Dict[str, Any]:
    """Clean up obsolete task results from backend"""
    try:
        logger.info("Running cleanup of obsolete task results")
        
        # This would interact with result backend to delete old entries
        # Implementation depends on specific backend (Redis, memcached, etc.)
        
        cleaned_count = 0
        
        # For Redis backend example:
        # from app.automation.celery_config import app
        # result_backend = app.backend
        # # ... cleanup logic ...
        
        return {
            'task_id': self.request.id,
            'status': 'COMPLETED',
            'cleaned_entries': cleaned_count,
            'max_age_hours': max_age_hours
        }
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise self.retry(exc=e)

@app.task(bind=True, queue='osint_darkweb')
def verify_tor_connection(self) -> Dict[str, Any]:
    """Verify Tor connection is working"""
    try:
        from ..collectors.darkweb_collector import DarkWebCollector, CollectorConfig
        
        config = CollectorConfig(
            target="check.torproject.org",
            data_type='darkweb',
            timeout=60
        )
        
        darkweb_collector = DarkWebCollector(config)
        tor_available = darkweb_collector.tor_available
        
        if tor_available:
            logger.info("Tor connection verified successfully")
        else:
            logger.warning("Tor connection not available")
        
        return {
            'task_id': self.request.id,
            'status': 'VERIFIED' if tor_available else 'FAILED',
            'tor_available': tor_available
        }
        
    except Exception as e:
        logger.error(f"Tor verification failed: {e}")
        return {
            'task_id': self.request.id,
            'status': 'ERROR',
            'error': str(e)
        }

@app.task(bind=True, queue='osint_default')
def normalize_collected_data(self, collection_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Normalize and deduplicate collected data across collectors"""
    try:
        logger.info("Normalizing collected data")
        
        # This would integrate with normalization_service.py
        # For now, basic deduplication
        
        all_entities = []
        entity_map = {}
        
        for result in collection_results:
            if result.get('status') == 'COMPLETED':
                entities = result.get('entities', [])
                all_entities.extend(entities)
                
                for entity in entities:
                    key = f"{entity.get('type')}:{entity.get('value')}"
                    entity_map[key] = entity
        
        # Deduplicated entities
        unique_entities = list(entity_map.values())
        
        logger.info(f"Normalized {len(all_entities)} -> {len(unique_entities)} unique entities")
        
        return {
            'task_id': self.request.id,
            'status': 'COMPLETED',
            'total_input_entities': len(all_entities),
            'unique_entities': len(unique_entities),
            'entities': unique_entities
        }
        
    except Exception as e:
        logger.error(f"Normalization failed: {e}")
        raise self.retry(exc=e)

@app.task(bind=True, queue='osint_default')
def update_task_progress(self, task_id: str, progress_data: Dict[str, Any]) -> None:
    """Update task progress metadata"""
    # This is a utility task for async progress updates
    logger.debug(f"Updating progress for task {task_id}: {progress_data}")