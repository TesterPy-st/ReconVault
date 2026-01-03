"""
Data Normalization Service

Provides data cleaning, deduplication, and enrichment for OSINT data.
Uses Pandas and Dask for processing.
"""

import hashlib
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Set
from urllib.parse import urlparse

import pandas as pd
from loguru import logger

from app.collectors.base_collector import DataType, RiskLevel


class NormalizationService:
    """
    Service for normalizing OSINT data.

    Handles:
    - Entity deduplication
    - Data merging
    - Validation
    - Metadata enrichment
    - Timestamp normalization
    - Batch processing
    """

    def __init__(self):
        self.processed_hashes: Set[str] = set()

    def deduplicate_entities(
        self, entities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Remove duplicate entities by value and type.

        Args:
            entities: List of entity dictionaries

        Returns:
            Deduplicated list of entities
        """
        if not entities:
            return []

        logger.info(f"Deduplicating {len(entities)} entities")

        # Create DataFrame for efficient processing
        df = pd.DataFrame(entities)

        # Deduplicate by entity_type and value
        # Keep the one with highest risk level
        risk_priority = {
            RiskLevel.CRITICAL.value: 5,
            RiskLevel.HIGH.value: 4,
            RiskLevel.MEDIUM.value: 3,
            RiskLevel.LOW.value: 2,
            RiskLevel.INFO.value: 1,
        }

        if "risk_level" in df.columns:
            df["risk_priority"] = df["risk_level"].map(risk_priority).fillna(0)
        else:
            df["risk_priority"] = 0

        # Sort by risk priority (descending)
        df_sorted = df.sort_values("risk_priority", ascending=False)

        # Drop duplicates, keeping first (highest risk)
        df_deduplicated = df_sorted.drop_duplicates(
            subset=["entity_type", "value"], keep="first"
        )

        # Convert back to list of dicts
        deduplicated = df_deduplicated.drop(columns=["risk_priority"]).to_dict(
            "records"
        )

        logger.info(
            f"Deduplicated to {len(deduplicated)} entities "
            f"({len(entities) - len(deduplicated)} removed)"
        )

        return deduplicated

    def merge_entity_data(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge data from multiple sources for same entities.

        Args:
            entities: List of entity dictionaries

        Returns:
            List of merged entities
        """
        if not entities:
            return []

        logger.info("Merging entity data from multiple sources")

        df = pd.DataFrame(entities)

        # Group by entity_type and value
        grouped = (
            df.groupby(["entity_type", "value"], as_index=False)
            .apply(lambda x: self._merge_group(x))
            .reset_index(drop=True)
        )

        merged = grouped.to_dict("records")

        logger.info(f"Merged {len(entities)} entities into {len(merged)} entities")

        return merged

    def _merge_group(self, group: pd.DataFrame) -> pd.Series:
        """Merge a group of same entities"""
        # Keep first row as base
        result = group.iloc[0].copy()

        # Merge metadata
        metadata = {}

        for _, row in group.iterrows():
            if pd.notna(row.get("metadata")):
                if isinstance(row["metadata"], dict):
                    metadata.update(row["metadata"])

        # Update metadata
        result["metadata"] = metadata

        # Merge sources
        sources = group["source"].dropna().unique().tolist()
        if sources:
            result["sources"] = sources

        # Keep highest risk level
        risk_levels = group["risk_level"].dropna().tolist()
        if risk_levels:
            risk_priority = {
                RiskLevel.CRITICAL.value: 5,
                RiskLevel.HIGH.value: 4,
                RiskLevel.MEDIUM.value: 3,
                RiskLevel.LOW.value: 2,
                RiskLevel.INFO.value: 1,
            }
            highest_risk = max(risk_levels, key=lambda x: risk_priority.get(x, 0))
            result["risk_level"] = highest_risk

        return result

    def validate_entity_data(self, entity: Dict[str, Any]) -> bool:
        """
        Validate entity data quality and completeness.

        Args:
            entity: Entity dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["entity_type", "value"]

        # Check required fields
        if not all(field in entity for field in required_fields):
            return False

        # Validate entity type
        try:
            DataType(entity["entity_type"])
        except ValueError:
            return False

        # Validate value is not empty
        if not entity["value"] or not str(entity["value"]).strip():
            return False

        # Type-specific validation
        entity_type = entity["entity_type"]
        value = str(entity["value"])

        if entity_type == DataType.EMAIL.value:
            if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", value):
                return False

        elif entity_type == DataType.IP.value:
            ip_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
            if not re.match(ip_pattern, value):
                return False

        elif entity_type == DataType.DOMAIN.value:
            if not re.match(
                r"^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?(\.[a-zA-Z]{2,})+$", value
            ):
                return False

        return True

    def enrich_entity_metadata(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add additional computed fields to entity.

        Args:
            entity: Entity dictionary to enrich

        Returns:
            Enriched entity
        """
        if "metadata" not in entity:
            entity["metadata"] = {}

        metadata = entity["metadata"]

        # Add normalized timestamp
        metadata["normalized_at"] = datetime.utcnow().isoformat() + "Z"

        # Add hash for easy comparison
        value_str = str(entity["value"]).lower()
        entity["value_hash"] = hashlib.md5(value_str.encode()).hexdigest()

        # Type-specific enrichment
        if entity["entity_type"] == DataType.EMAIL.value:
            parts = entity["value"].split("@")
            if len(parts) == 2:
                metadata["local_part"] = parts[0]
                metadata["domain"] = parts[1]

        elif entity["entity_type"] == DataType.DOMAIN.value:
            # Extract domain parts
            domain_parts = entity["value"].split(".")
            if len(domain_parts) >= 2:
                metadata["tld"] = domain_parts[-1]
                metadata["sld"] = domain_parts[-2]
                if len(domain_parts) > 2:
                    metadata["subdomain"] = ".".join(domain_parts[:-2])

        elif entity["entity_type"] == DataType.URL.value:
            try:
                parsed = urlparse(entity["value"])
                metadata["scheme"] = parsed.scheme
                metadata["netloc"] = parsed.netloc
                metadata["path"] = parsed.path
                metadata["query"] = parsed.query
            except Exception:
                pass

        return entity

    def normalize_timestamps(
        self, entities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Convert all timestamps to UTC.

        Args:
            entities: List of entity dictionaries

        Returns:
            List of entities with normalized timestamps
        """
        logger.info("Normalizing timestamps")

        for entity in entities:
            if "metadata" in entity and isinstance(entity["metadata"], dict):
                metadata = entity["metadata"]

                for key, value in metadata.items():
                    if (
                        key.endswith("_date")
                        or key.endswith("_at")
                        or key.endswith("_time")
                    ):
                        if isinstance(value, str):
                            # Try to parse and convert to UTC
                            try:
                                # Try different date formats
                                parsed = None

                                # ISO format
                                if "T" in value or "Z" in value:
                                    parsed = datetime.fromisoformat(
                                        value.replace("Z", "+00:00")
                                    )

                                # Common formats
                                if not parsed:
                                    from dateparser import parse

                                    parsed = parse(value)

                                if parsed:
                                    if parsed.tzinfo:
                                        parsed = parsed.astimezone(timezone.utc)
                                    else:
                                        parsed = parsed.replace(tzinfo=timezone.utc)

                                    metadata[key] = parsed.isoformat() + "Z"
                            except Exception as e:
                                logger.debug(f"Could not parse timestamp {key}: {e}")

        return entities

    async def batch_normalize(
        self, entity_list: List[Dict[str, Any]], batch_size: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Parallel batch processing with Dask.

        Args:
            entity_list: List of entities to normalize
            batch_size: Number of entities per batch

        Returns:
            List of normalized entities
        """
        if not entity_list:
            return []

        logger.info(
            f"Batch normalizing {len(entity_list)} entities in batches of {batch_size}"
        )

        # For now, use pandas in-memory
        # For very large datasets, would use Dask

        # Step 1: Deduplicate
        deduplicated = self.deduplicate_entities(entity_list)

        # Step 2: Merge data
        merged = self.merge_entity_data(deduplicated)

        # Step 3: Validate and filter
        valid_entities = [e for e in merged if self.validate_entity_data(e)]

        if len(valid_entities) < len(merged):
            logger.warning(
                f"Filtered out {len(merged) - len(valid_entities)} invalid entities"
            )

        # Step 4: Enrich metadata
        enriched = [self.enrich_entity_metadata(e) for e in valid_entities]

        # Step 5: Normalize timestamps
        normalized = self.normalize_timestamps(enriched)

        logger.info(f"Batch normalization complete: {len(normalized)} entities")

        return normalized

    def extract_relationships(
        self, entities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract relationships from entity data.

        Args:
            entities: List of entity dictionaries

        Returns:
            List of relationship dictionaries
        """
        relationships = []

        for entity in entities:
            # Check for embedded relationships in metadata
            if "metadata" in entity and isinstance(entity["metadata"], dict):
                metadata = entity["metadata"]

                # Extract related entities
                for key, value in metadata.items():
                    # Domain from email
                    if (
                        key == "domain"
                        and entity["entity_type"] == DataType.EMAIL.value
                    ):
                        relationships.append(
                            {
                                "relationship_type": "RELATED_TO",
                                "source": entity["value"],
                                "target": value,
                                "metadata": {"relationship": "email_domain"},
                            }
                        )

                    # Registrant org from WHOIS
                    elif key == "registrant_org" and value:
                        relationships.append(
                            {
                                "relationship_type": "REGISTERED_BY",
                                "source": entity["value"],
                                "target": value,
                                "metadata": {"relationship": "whois"},
                            }
                        )

        logger.info(
            f"Extracted {len(relationships)} relationships from {len(entities)} entities"
        )

        return relationships

    def normalize_for_storage(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Normalize entities for database storage.

        Args:
            entities: List of entity dictionaries

        Returns:
            Dictionary with entities and relationships
        """
        # Separate entities from relationships
        pure_entities = []
        pure_relationships = []

        for item in entities:
            if isinstance(item, dict):
                if "relationship_type" in item:
                    pure_relationships.append(item)
                elif "entity_type" in item:
                    pure_entities.append(item)

        # Also extract from entity metadata
        extracted_relationships = self.extract_relationships(pure_entities)
        pure_relationships.extend(extracted_relationships)

        # Deduplicate relationships
        if pure_relationships:
            df_rel = pd.DataFrame(pure_relationships)
            df_rel_dedup = df_rel.drop_duplicates(
                subset=["relationship_type", "source", "target"], keep="first"
            )
            pure_relationships = df_rel_dedup.to_dict("records")

        logger.info(
            f"Normalized for storage: {len(pure_entities)} entities, "
            f"{len(pure_relationships)} relationships"
        )

        return {"entities": pure_entities, "relationships": pure_relationships}
