"""
Collection Pipeline Service

Main orchestration service for OSINT data collection.
"""

import asyncio
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from loguru import logger

from app.automation.celery_tasks import celery_app
from app.collectors import (CollectorConfig, CollectorFactory,
                            DarkWebCollector, DataType, DomainCollector,
                            EmailCollector, GeoCollector, IPCollector,
                            MediaCollector, SocialCollector, WebCollector,
                            infer_data_type)
from app.ethics.osint_compliance import OSINTCompliance
from app.services.entity_service import EntityService
from app.services.graph_service import GraphService
from app.services.normalization_service import NormalizationService
from app.services.risk_analysis_service import RiskAnalysisService


class TaskStatus(Enum):
    """Collection task statuses"""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class CollectionPipelineService:
    """
    Main orchestration service for OSINT collection.

    Handles:
    - Task management and routing
    - Collector execution
    - Data normalization
    - Entity/relationship creation
    - Neo4j sync
    - Risk assessment
    - Progress tracking
    """

    def __init__(self):
        self.normalization_service = NormalizationService()
        self.risk_service = RiskAnalysisService()
        self.compliance_checker = OSINTCompliance()
        self.entity_service = None
        self.graph_service = None

        # Active tasks (in production, use Redis/database)
        self.active_tasks: Dict[str, Dict[str, Any]] = {}

    async def initialize(self):
        """Initialize services with database connections"""
        from app.database import get_db

        self.entity_service = EntityService(next(get_db()))
        self.graph_service = GraphService()
        logger.info("Collection pipeline service initialized")

    async def start_collection_task(
        self,
        target: str,
        collection_types: Optional[List[str]] = None,
        include_dark_web: bool = False,
        include_media: bool = False,
    ) -> Dict[str, Any]:
        """
        Start a new collection task.

        Args:
            target: Target to collect (domain, email, IP, etc.)
            collection_types: Specific collection types to run (default: auto-detect)
            include_dark_web: Include dark web collection
            include_media: Include media collection

        Returns:
            Task information
        """
        task_id = str(uuid.uuid4())
        start_time = datetime.utcnow()

        logger.info(f"Starting collection task {task_id} for target: {target}")

        # Create task record
        task = {
            "task_id": task_id,
            "target": target,
            "status": TaskStatus.PENDING.value,
            "progress": 0,
            "collectors_completed": [],
            "collectors_failed": [],
            "entities_collected": 0,
            "relationships_collected": 0,
            "start_time": start_time.isoformat(),
            "end_time": None,
            "errors": [],
            "include_dark_web": include_dark_web,
            "include_media": include_media,
        }

        self.active_tasks[task_id] = task

        # Check ethics compliance
        ethical_verdict = await self.compliance_checker.get_ethical_verdict(
            target, "collection"
        )
        if not ethical_verdict.get("allowed", False):
            task["status"] = TaskStatus.FAILED.value
            task["errors"].append(
                f"Ethics check failed: {ethical_verdict.get('reason', '')}"
            )
            task["end_time"] = datetime.utcnow().isoformat()
            return task

        try:
            # Route to collectors
            collectors = await self.route_to_collectors(
                target, collection_types, include_dark_web, include_media
            )

            if not collectors:
                task["status"] = TaskStatus.FAILED.value
                task["errors"].append("No collectors found for target type")
                task["end_time"] = datetime.utcnow().isoformat()
                return task

            task["status"] = TaskStatus.RUNNING.value
            task["total_collectors"] = len(collectors)

            # Execute collection
            logger.info(f"Task {task_id}: Starting {len(collectors)} collectors")

            results = await self.execute_collection(target, collectors, task_id)

            # Process results
            logger.info(f"Task {task_id}: Collection complete, processing results")

            normalized_data = await self.normalize_results(results)

            # Create entities and relationships
            logger.info(f"Task {task_id}: Creating entities and relationships")

            if self.entity_service:
                created_data = await self.create_entities_from_results(
                    normalized_data, task_id
                )
            else:
                # If no DB, just use normalized data
                created_data = {
                    "entities": normalized_data.get("entities", []),
                    "relationships": normalized_data.get("relationships", []),
                }

            # Sync to Neo4j
            logger.info(f"Task {task_id}: Syncing to Neo4j")

            if self.graph_service:
                await self.sync_to_neo4j(
                    created_data["entities"], created_data["relationships"]
                )

            # Assess risk
            logger.info(f"Task {task_id}: Assessing risk")

            await self.assess_risk(created_data["entities"])

            # Update task status
            task["status"] = TaskStatus.COMPLETED.value
            task["progress"] = 100
            task["entities_collected"] = len(created_data["entities"])
            task["relationships_collected"] = len(created_data["relationships"])
            task["end_time"] = datetime.utcnow().isoformat()
            task["data_sources"] = list(
                set(r.get("collector_name", "") for r in results if isinstance(r, dict))
            )

            logger.info(f"Task {task_id}: Completed successfully")

        except Exception as e:
            logger.exception(f"Task {task_id} failed: {e}")
            task["status"] = TaskStatus.FAILED.value
            task["errors"].append(str(e))
            task["end_time"] = datetime.utcnow().isoformat()

        return task

    async def route_to_collectors(
        self,
        target: str,
        collection_types: Optional[List[str]] = None,
        include_dark_web: bool = False,
        include_media: bool = False,
    ) -> List[Any]:
        """
        Select appropriate collectors for target.

        Args:
            target: Target to collect
            collection_types: Specific collection types (None = auto-detect)
            include_dark_web: Include dark web collector
            include_media: Include media collector

        Returns:
            List of collector instances
        """
        collectors = []

        # Infer data type
        data_type = infer_data_type(target)
        logger.info(f"Inferred data type for {target}: {data_type.value}")

        # If specific types requested, use them
        if collection_types:
            for collection_type in collection_types:
                try:
                    if collection_type == "web":
                        config = CollectorConfig(target=target, data_type=DataType.URL)
                        collectors.append(WebCollector(config))
                    elif collection_type == "social":
                        config = CollectorConfig(
                            target=target, data_type=DataType.USERNAME
                        )
                        collectors.append(SocialCollector(config))
                    elif collection_type == "domain":
                        config = CollectorConfig(
                            target=target, data_type=DataType.DOMAIN
                        )
                        collectors.append(DomainCollector(config))
                    elif collection_type == "ip":
                        config = CollectorConfig(target=target, data_type=DataType.IP)
                        collectors.append(IPCollector(config))
                    elif collection_type == "email":
                        config = CollectorConfig(
                            target=target, data_type=DataType.EMAIL
                        )
                        collectors.append(EmailCollector(config))
                    elif collection_type == "geo":
                        config = CollectorConfig(target=target, data_type=DataType.TEXT)
                        collectors.append(GeoCollector(config))
                except Exception as e:
                    logger.error(f"Failed to create {collection_type} collector: {e}")

        else:
            # Auto-select based on data type
            try:
                config = CollectorConfig(target=target, data_type=data_type)

                if data_type == DataType.URL:
                    collectors.append(WebCollector(config))
                elif data_type == DataType.DOMAIN:
                    collectors.append(DomainCollector(config))
                elif data_type == DataType.IP:
                    collectors.append(IPCollector(config))
                elif data_type == DataType.EMAIL:
                    collectors.append(EmailCollector(config))
                elif data_type in [DataType.USERNAME, DataType.SOCIAL_PROFILE]:
                    collectors.append(SocialCollector(config))
                elif data_type in [DataType.IMAGE, DataType.AUDIO, DataType.VIDEO]:
                    collectors.append(MediaCollector(config))

            except Exception as e:
                logger.error(f"Failed to create collector for {data_type}: {e}")

        # Add dark web collector if requested
        if include_dark_web:
            try:
                config = CollectorConfig(target=target, data_type=DataType.TEXT)
                collectors.append(DarkWebCollector(config))
            except Exception as e:
                logger.error(f"Failed to create dark web collector: {e}")

        # Add media collector if requested and not already added
        if include_media and data_type not in [
            DataType.IMAGE,
            DataType.AUDIO,
            DataType.VIDEO,
        ]:
            try:
                config = CollectorConfig(target=target, data_type=DataType.TEXT)
                collectors.append(MediaCollector(config))
            except Exception as e:
                logger.error(f"Failed to create media collector: {e}")

        logger.info(f"Routed to {len(collectors)} collectors")

        return collectors

    async def execute_collection(
        self, target: str, collectors: List[Any], task_id: str
    ) -> List[Dict[str, Any]]:
        """
        Execute collection with all collectors.

        Args:
            target: Target to collect
            collectors: List of collector instances
            task_id: Task ID for tracking

        Returns:
            List of collection results
        """
        results = []
        total = len(collectors)

        for i, collector in enumerate(collectors):
            logger.info(
                f"Task {task_id}: Running collector {i+1}/{total}: {collector.name}"
            )

            try:
                async with collector:
                    result = await collector.execute()
                    results.append(result)

                    # Update task progress
                    if task_id in self.active_tasks:
                        self.active_tasks[task_id]["collectors_completed"].append(
                            collector.name
                        )
                        self.active_tasks[task_id]["progress"] = int(
                            (i + 1) / total * 80
                        )  # Reserve 20% for processing

                    if result.errors:
                        if task_id in self.active_tasks:
                            self.active_tasks[task_id]["collectors_failed"].append(
                                collector.name
                            )
                            self.active_tasks[task_id]["errors"].extend(result.errors)

            except Exception as e:
                logger.error(f"Task {task_id}: Collector {collector.name} failed: {e}")
                results.append(
                    {
                        "success": False,
                        "collector_name": collector.name,
                        "errors": [str(e)],
                    }
                )

                if task_id in self.active_tasks:
                    self.active_tasks[task_id]["collectors_failed"].append(
                        collector.name
                    )
                    self.active_tasks[task_id]["errors"].append(str(e))

        return results

    async def normalize_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Normalize, deduplicate, and validate collected data.

        Args:
            results: List of collection results

        Returns:
            Normalized data with entities and relationships
        """
        logger.info(f"Normalizing {len(results)} collection results")

        # Extract all entities and relationships from results
        all_data = []

        for result in results:
            if isinstance(result, dict):
                # Add entities
                if "data" in result and isinstance(result["data"], list):
                    all_data.extend(result["data"])

        # Batch normalize
        normalized = await self.normalization_service.batch_normalize(all_data)

        # Separate entities and relationships
        separated = self.normalization_service.normalize_for_storage(normalized)

        logger.info(
            f"Normalized: {len(separated['entities'])} entities, {len(separated['relationships'])} relationships"
        )

        return separated

    async def create_entities_from_results(
        self, normalized_data: Dict[str, Any], task_id: str
    ) -> Dict[str, Any]:
        """
        Create Entity and Relationship records in database.

        Args:
            normalized_data: Normalized data with entities and relationships
            task_id: Task ID

        Returns:
            Created data
        """
        entities_data = []
        relationships_data = []

        # Create entities
        for entity_data in normalized_data.get("entities", []):
            try:
                entity = await self.entity_service.create_entity(
                    {
                        "entity_type": entity_data.get("entity_type"),
                        "value": entity_data.get("value"),
                        "risk_level": entity_data.get("risk_level", "INFO"),
                        "metadata": entity_data.get("metadata", {}),
                        "source": entity_data.get("source", "unknown"),
                    }
                )
                entities_data.append(entity)

                # Store mapping of value to ID for relationships
                entity_data["_db_id"] = entity.id

            except Exception as e:
                logger.error(f"Failed to create entity: {e}")

        # Create relationships
        for rel_data in normalized_data.get("relationships", []):
            try:
                # Find entity IDs
                source_entities = [
                    e for e in entities_data if e.value == rel_data.get("source")
                ]
                target_entities = [
                    e for e in entities_data if e.value == rel_data.get("target")
                ]

                if source_entities and target_entities:
                    relationship = await self.entity_service.create_relationship(
                        {
                            "source_id": source_entities[0].id,
                            "target_id": target_entities[0].id,
                            "relationship_type": rel_data.get("relationship_type"),
                            "metadata": rel_data.get("metadata", {}),
                        }
                    )
                    relationships_data.append(relationship)

            except Exception as e:
                logger.error(f"Failed to create relationship: {e}")

        logger.info(
            f"Created {len(entities_data)} entities and {len(relationships_data)} relationships in DB"
        )

        return {
            "entities": [
                {
                    "id": e.id,
                    "entity_type": e.entity_type,
                    "value": e.value,
                    "risk_level": e.risk_level,
                    "metadata": e.metadata,
                }
                for e in entities_data
            ],
            "relationships": [
                {
                    "id": r.id,
                    "source_id": r.source_id,
                    "target_id": r.target_id,
                    "relationship_type": r.relationship_type,
                }
                for r in relationships_data
            ],
        }

    async def sync_to_neo4j(
        self, entities: List[Dict[str, Any]], relationships: List[Dict[str, Any]]
    ):
        """
        Sync entities and relationships to Neo4j.

        Args:
            entities: List of entity dictionaries
            relationships: List of relationship dictionaries
        """
        try:
            # Create nodes for each entity
            for entity in entities:
                await self.graph_service.create_node(
                    entity_type=entity["entity_type"],
                    value=entity["value"],
                    properties={
                        "risk_level": entity.get("risk_level"),
                        "metadata": entity.get("metadata", {}),
                    },
                )

            # Create relationships
            for rel in relationships:
                # Find nodes by value
                source_nodes = await self.graph_service.find_nodes_by_value(
                    rel.get("source_id")
                )
                target_nodes = await self.graph_service.find_nodes_by_value(
                    rel.get("target_id")
                )

                if source_nodes and target_nodes:
                    await self.graph_service.create_relationship(
                        source_node_id=source_nodes[0]["id"],
                        target_node_id=target_nodes[0]["id"],
                        relationship_type=rel["relationship_type"],
                        properties=rel.get("metadata", {}),
                    )

            logger.info(
                f"Synced {len(entities)} entities and {len(relationships)} relationships to Neo4j"
            )

        except Exception as e:
            logger.error(f"Failed to sync to Neo4j: {e}")

    async def assess_risk(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run risk analysis on entities.

        Args:
            entities: List of entity dictionaries

        Returns:
            Risk assessment summary
        """
        logger.info("Assessing risk for collected entities")

        # Batch analyze risk
        entities_with_risk = self.risk_service.batch_analyze_risk(entities)

        # Get overall assessment
        assessment = self.risk_service.assess_collection_risk(entities_with_risk)

        logger.info(f"Risk assessment: {assessment}")

        return assessment

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a collection task.

        Args:
            task_id: Task ID

        Returns:
            Task information or None if not found
        """
        return self.active_tasks.get(task_id)

    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a running task.

        Args:
            task_id: Task ID

        Returns:
            True if cancelled, False otherwise
        """
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            if task["status"] == TaskStatus.RUNNING.value:
                task["status"] = TaskStatus.CANCELLED.value
                task["end_time"] = datetime.utcnow().isoformat()
                logger.info(f"Task {task_id} cancelled")
                return True

        return False

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks"""
        return list(self.active_tasks.values())
