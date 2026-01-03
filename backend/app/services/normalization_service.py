"""
Data Normalization Service for ReconVault OSINT Pipeline

This module provides entity deduplication, data merging, validation, and
enrichment using Pandas and Dask for distributed processing.
"""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime
from functools import lru_cache
import hashlib
import json
import asyncio

# Conditional imports for optional dependencies
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

try:
    import dask.dataframe as dd
    from dask import delayed, compute
    DASK_AVAILABLE = True
except ImportError:
    DASK_AVAILABLE = False
    dd = None
    delayed = None
    compute = None

try:
    from datasketch import MinHash, MinHashLSH
    DATASKETCH_AVAILABLE = True
except ImportError:
    DATASKETCH_AVAILABLE = False
    MinHash = None
    MinHashLSH = None

# Standard library imports
from collections import defaultdict
from email_validator import validate_email, EmailNotValidError
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class NormalizationService:
    """Service for normalizing and deduplicating OSINT entities"""
    
    def __init__(self, use_dask: bool = True, use_minhash: bool = True):
        self.use_dask = DASK_AVAILABLE and use_dask
        self.use_minhash = DATASKETCH_AVAILABLE and use_minhash
        self.logger = logger
        
        # Initialize LSH for fuzzy matching if available
        if self.use_minhash and MinHashLSH:
            self.lsh_index = MinHashLSH(threshold=0.5, num_perm=128)
        else:
            self.lsh_index = None
    
    def deduplicate_entities(self, entities: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Deduplicate entities based on value, type, and metadata similarity
        
        Args:
            entities: List of entity dictionaries
            
        Returns:
            Tuple of (unique_entities, duplicate_metadata)
        """
        if not entities:
            return [], []
        
        self.logger.info(f"Starting deduplication of {len(entities)} entities")
        
        try:
            # Pre-validate entities
            valid_entities = self._pre_validate_entities(entities)
            
            # Create entity fingerprints for deduplication
            entity_fingerprints = self._create_entity_fingerprints(valid_entities)
            
            # Deduplicate based on fingerprints
            unique_entities, duplicates = self._deduplicate_by_fingerprint(valid_entities, entity_fingerprints)
            
            # Fuzzy matching for similar entities
            if self.use_minhash:
                unique_entities = self._fuzzy_deduplicate(unique_entities)
            
            # Merge duplicate metadata
            merged_entities = self._merge_duplicate_metadata(unique_entities)
            
            self.logger.info(f"Deduplication complete: {len(entities)} -> {len(merged_entities)} entities ({len(duplicates)} duplicates detected)")
            
            return merged_entities, duplicates
            
        except Exception as e:
            self.logger.error(f"Deduplication failed: {e}")
            return entities, []
    
    def _pre_validate_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Pre-validate and normalize entity structures"""
        validated = []
        
        for entity in entities:
            try:
                # Ensure required fields
                if 'value' not in entity or 'type' not in entity:
                    continue
                
                # Normalize string values
                if isinstance(entity['value'], str):
                    entity['value'] = entity['value'].strip().lower()
                
                # Default metadata if missing
                if 'metadata' not in entity:
                    entity['metadata'] = {}
                
                # Add normalization timestamp
                entity['metadata']['normalized_at'] = datetime.utcnow().isoformat()
                
                validated.append(entity)
                
            except Exception as e:
                self.logger.debug(f"Entity pre-validation failed: {e}")
                continue
        
        return validated
    
    def _create_entity_fingerprints(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create fingerprints for entity deduplication"""
        fingerprints = []
        
        for entity in entities:
            try:
                fingerprint = {
                    'exact_key': self._create_exact_key(entity),
                    'type_key': entity['type'],
                    'value_hash': self._hash_value(entity['value']),
                    'content_hash': self._hash_content(entity)
                }
                fingerprints.append(fingerprint)
            except Exception as e:
                self.logger.debug(f"Fingerprint creation failed: {e}")
                # Use fallback fingerprint
                fingerprints.append({
                    'exact_key': f"{entity['type']}:{str(entity['value'])}",
                    'type_key': entity['type'],
                    'value_hash': hash(str(entity['value'])),
                    'content_hash': hash(str(entity))
                })
        
        return fingerprints
    
    def _create_exact_key(self, entity: Dict[str, Any]) -> str:
        """Create exact match key for entity"""
        value = entity['value']
        entity_type = entity['type']
        
        # Normalize by entity type
        if entity_type == 'EMAIL':
            return f"email:{self._normalize_email_key(value)}"
        
        elif entity_type == 'DOMAIN':
            return f"domain:{self._normalize_domain_key(value)}"
        
        elif entity_type == 'IP_ADDRESS':
            return f"ip:{self._normalize_ip_key(value)}"
        
        elif entity_type == 'SOCIAL_PROFILE':
            platform = entity.get('platform', 'unknown')
            return f"social:{platform}:{value}"
        
        elif entity_type == 'URL':
            return f"url:{self._normalize_url_key(value)}"
        
        else:
            return f"{entity_type.lower()}:{value}"
    
    @staticmethod
    def _normalize_email_key(email: str) -> str:
        """Normalize email for deduplication"""
        try:
            # Validate and normalize email
            valid = validate_email(email)
            return valid.normalized
        except EmailNotValidError:
            return email.lower().strip()
    
    @staticmethod
    def _normalize_domain_key(domain: str) -> str:
        """Normalize domain for deduplication"""
        domain = domain.lower().strip()
        # Remove protocol if present
        if '://' in domain:
            domain = urlparse(domain).netloc
        # Remove www prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    
    @staticmethod
    def _normalize_ip_key(ip: str) -> str:
        """Normalize IP address"""
        import ipaddress
        try:
            ip_obj = ipaddress.ip_address(ip.strip())
            return str(ip_obj)
        except:
            return ip.strip()
    
    @staticmethod
    def _normalize_url_key(url: str) -> str:
        """Normalize URL for deduplication"""
        from urllib.parse import urlparse, urlunparse
        parsed = urlparse(url.lower().strip())
        # Reconstruct without query params and fragments
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
    
    @staticmethod
    def _hash_value(value: Any) -> int:
        """Create hash of entity value"""
        return hash(str(value))
    
    @staticmethod
    def _hash_content(entity: Dict[str, Any]) -> str:
        """Create content hash for similarity comparison"""
        content = f"{entity['type']}:{entity['value']}"
        if 'metadata' in entity and entity['metadata']:
            content += f":{str(sorted(entity['metadata'].items()))}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _deduplicate_by_fingerprint(self, entities: List[Dict[str, Any]], 
                                   fingerprints: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Deduplicate entities using fingerprints"""
        seen_keys = set()
        unique_entities = []
        duplicates = []
        
        for entity, fingerprint in zip(entities, fingerprints):
            exact_key = fingerprint['exact_key']
            content_hash = fingerprint['content_hash']
            
            # Use exact key for primary deduplication
            if exact_key in seen_keys:
                # Mark as duplicate
                duplicate_info = {
                    'duplicate_entity': entity,
                    'duplicate_key': exact_key,
                    'original_content_hash': content_hash,
                    'detected_at': datetime.utcnow().isoformat()
                }
                duplicates.append(duplicate_info)
            else:
                seen_keys.add(exact_key)
                unique_entities.append(entity)
        
        return unique_entities, duplicates
    
    def _fuzzy_deduplicate(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply fuzzy matching for similar entities using MinHash"""
        if not self.lsh_index:
            return entities
        
        deduplicated = []
        similar_groups = defaultdict(list)
        
        # Build MinHash for each entity
        for i, entity in enumerate(entities):
            minhash = self._create_minhash(entity)
            
            # Query for similar entities
            similar_entities = self.lsh_index.query(minhash)
            
            if similar_entities:
                # Add to first similar group
                group_key = similar_entities[0]
                similar_groups[group_key].append(entity)
            else:
                # Add to LSH index and deduplicated list
                self.lsh_index.insert(f"entity_{i}", minhash)
                deduplicated.append(entity)
        
        # Merge similar entity groups
        for group_key, entity_group in similar_groups.items():
            merged = self._merge_similar_entities(entity_group)
            deduplicated.append(merged)
        
        return deduplicated
    
    def _create_minhash(self, entity: Dict[str, Any]) -> MinHash:
        """Create MinHash for entity similarity"""
        if not MinHash:
            return None
        
        minhash = MinHash(num_perm=128)
        
        # Add entity value
        value_str = str(entity.get('value', ''))
        for word in value_str.split():
            minhash.update(word.encode('utf-8'))
        
        # Add entity type
        minhash.update(entity.get('type', '').encode('utf-8'))
        
        # Add metadata if available
        if 'metadata' in entity and entity['metadata']:
            metadata_str = str(entity['metadata'])
            for word in metadata_str.split():
                minhash.update(word.encode('utf-8'))
        
        return minhash
    
    def _merge_similar_entities(self, entity_group: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge a group of similar entities"""
        if not entity_group:
            return {}
        
        # Use first entity as base
        base_entity = entity_group[0].copy()
        
        # Merge metadata from all entities
        merged_metadata = base_entity.get('metadata', {}).copy()
        
        for entity in entity_group[1:]:
            entity_metadata = entity.get('metadata', {})
            for key, value in entity_metadata.items():
                if key not in merged_metadata:
                    merged_metadata[key] = value
                elif isinstance(merged_metadata[key], list) and isinstance(value, list):
                    merged_metadata[key].extend(value)
                elif isinstance(merged_metadata[key], dict) and isinstance(value, dict):
                    merged_metadata[key].update(value)
        
        # Remove duplicates from lists
        for key, value in merged_metadata.items():
            if isinstance(value, list):
                # Preserve order while removing duplicates
                seen = set()
                merged_metadata[key] = [x for x in value if not (x in seen or seen.add(x))]
        
        base_entity['metadata'] = merged_metadata
        base_entity['metadata']['merged_from_similar'] = len(entity_group)
        
        return base_entity
    
    def merge_entity_data(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge data from multiple sources for same entities
        
        Args:
            entities: List of entity dictionaries
            
        Returns:
            List of merged entities
        """
        if not entities:
            return []
        
        # Group entities by exact key
        entity_groups = defaultdict(list)
        for entity in entities:
            key = self._create_exact_key(entity)
            entity_groups[key].append(entity)
        
        # Merge each group
        merged_entities = []
        for key, entity_group in entity_groups.items():
            if len(entity_group) == 1:
                merged_entities.append(entity_group[0])
            else:
                merged = self._merge_duplicate_metadata(entity_group)
                merged_entities.append(merged)
        
        return merged_entities
    
    def _merge_duplicate_metadata(self, entity_group: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge metadata across duplicate entities"""
        if not entity_group:
            return {}
        
        # Start with first entity as base
        base_entity = entity_group[0].copy()
        base_metadata = base_entity.get('metadata', {}).copy()
        
        # Track source information
        sources = {base_entity.get('source')}
        collection_timestamps = []
        
        if 'collected_at' in base_metadata:
            collection_timestamps.append(base_metadata['collected_at'])
        
        # Merge from all entities
        for entity in entity_group[1:]:
            # Add source
            source = entity.get('source')
            if source:
                sources.add(source)
            
            # Merge metadata
            entity_metadata = entity.get('metadata', {})
            for key, value in entity_metadata.items():
                if key not in base_metadata:
                    base_metadata[key] = value
                elif isinstance(base_metadata[key], list) and isinstance(value, list):
                    base_metadata[key].extend(value)
                elif isinstance(base_metadata[key], dict) and isinstance(value, dict):
                    base_metadata[key].update(value)
                elif key == 'collected_at':
                    collection_timestamps.append(value)
                # If values differ but aren't mergable, keep original
            
            # Merge top-level fields if different
            if entity.get('confidence') and not base_entity.get('confidence'):
                base_entity['confidence'] = entity['confidence']
            elif entity.get('confidence') and base_entity.get('confidence'):
                # Keep higher confidence
                if entity['confidence'] > base_entity['confidence']:
                    base_entity['confidence'] = entity['confidence']
        
        # Update sources and timestamps
        if sources:
            base_metadata['sources'] = list(sources)
        
        if len(collection_timestamps) > 1:
            base_metadata['first_collected'] = min(collection_timestamps)
            base_metadata['last_collected'] = max(collection_timestamps)
            base_metadata['collection_count'] = len(collection_timestamps)
        
        base_entity['metadata'] = base_metadata
        base_entity['merged_sources'] = len(entity_group)
        
        return base_entity
    
    def validate_entity_data(self, entities: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Validate data quality and completeness of entities
        
        Args:
            entities: List of entity dictionaries
            
        Returns:
            Tuple of (valid_entities, invalid_entities)
        """
        valid_entities = []
        invalid_entities = []
        
        for entity in entities:
            try:
                validation_result = self._validate_single_entity(entity)
                
                if validation_result['is_valid']:
                    # Add validation metadata
                    entity['metadata'] = entity.get('metadata', {})
                    entity['metadata']['validation'] = validation_result
                    entity['metadata']['validation_score'] = validation_result['quality_score']
                    valid_entities.append(entity)
                else:
                    # Add validation error info
                    entity['validation_error'] = validation_result['errors']
                    invalid_entities.append(entity)
            
            except Exception as e:
                self.logger.debug(f"Entity validation failed: {e}")
                entity['validation_error'] = str(e)
                invalid_entities.append(entity)
        
        return valid_entities, invalid_entities
    
    def _validate_single_entity(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single entity"""
        errors = []
        warnings = []
        quality_score = 100
        
        # Check required fields
        if 'value' not in entity or not entity['value']:
            errors.append("Missing or empty 'value' field")
            quality_score -= 40
        
        if 'type' not in entity or not entity['type']:
            errors.append("Missing or empty 'type' field")
            quality_score -= 40
        
        # Validate value based on type
        entity_type = entity.get('type', '')
        value = entity.get('value', '')
        
        if entity_type == 'EMAIL' and value:
            try:
                validate_email(value)
            except EmailNotValidError:
                warnings.append("Invalid email format")
                quality_score -= 20
        
        elif entity_type == 'DOMAIN' and value:
            if not self._is_valid_domain(value):
                warnings.append("Invalid domain format")
                quality_score -= 20
        
        elif entity_type == 'IP_ADDRESS' and value:
            if not self._is_valid_ip(value):
                warnings.append("Invalid IP address format")
                quality_score -= 20
        
        elif entity_type == 'URL' and value:
            if not self._is_valid_url(value):
                warnings.append("Invalid URL format")
                quality_score -= 20
        
        # Check metadata quality
        if 'metadata' not in entity:
            warnings.append("Missing metadata")
            quality_score -= 10
        else:
            # Check for required metadata fields based on type
            metadata = entity['metadata']
            
            if 'source' not in metadata:
                warnings.append("Missing source in metadata")
                quality_score -= 10
            
            if 'collected_at' not in metadata:
                warnings.append("Missing collection timestamp in metadata")
                quality_score -= 5
        
        # Check for confidence scores
        if 'confidence' in entity and entity['confidence'] is not None:
            if not (0 <= entity['confidence'] <= 1):
                warnings.append("Confidence score out of range [0,1]")
                quality_score -= 5
        else:
            warnings.append("Missing confidence score (defaulting to 0.5)")
            entity['confidence'] = 0.5
            quality_score -= 5
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'quality_score': max(0, min(100, quality_score))
        }
    
    @staticmethod
    def _is_valid_domain(domain: str) -> bool:
        """Check if string is a valid domain"""
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
        return bool(re.match(pattern, domain))
    
    @staticmethod
    def _is_valid_ip(ip: str) -> bool:
        """Check if string is a valid IP address"""
        pattern = r'^([0-9]{1,3}\.){3}[0-9]{1,3}$|^([a-fA-F0-9:]+:+)+[a-fA-F0-9]+$'
        return bool(re.match(pattern, ip))
    
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Check if string is a valid URL"""
        try:
            result = urlparse(url.strip())
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def enrich_entity_metadata(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich entity with additional computed fields
        
        Args:
            entity: Entity dictionary
            
        Returns:
            Enriched entity dictionary
        """
        enriched = entity.copy()
        metadata = enriched.get('metadata', {})
        
        # Add enrichment timestamp
        metadata['enriched_at'] = datetime.utcnow().isoformat()
        
        # Enrich based on entity type
        entity_type = enriched.get('type', '')
        value = enriched.get('value', '')
        
        if entity_type == 'DOMAIN' and value:
            metadata.update(self._enrich_domain(value))
        
        elif entity_type == 'EMAIL' and value:
            metadata.update(self._enrich_email(value))
        
        elif entity_type == 'SOCIAL_PROFILE' and value:
            metadata.update(self._enrich_social_profile(value, metadata))
        
        # Add entity age if timestamp available
        if 'collected_at' in metadata:
            try:
                collected_time = datetime.fromisoformat(metadata['collected_at'])
                age_seconds = (datetime.utcnow() - collected_time).total_seconds()
                metadata['entity_age_seconds'] = age_seconds
                metadata['entity_age_readable'] = self._format_age(age_seconds)
            except:
                pass
        
        enriched['metadata'] = metadata
        return enriched
    
    def _enrich_domain(self, domain: str) -> Dict[str, Any]:
        """Enrich domain entity with additional metadata"""
        enrichment = {}
        
        try:
            # Extract TLD
            parts = domain.split('.')
            if len(parts) >= 2:
                enrichment['tld'] = '.'.join(parts[-2:])
                enrichment['root_domain'] = '.'.join(parts[-2:])
            
            # Determine domain type
            if domain.startswith('www.'):
                enrichment['subtype'] = 'www_subdomain'
            elif len(domain.split('.')) > 2:
                enrichment['subtype'] = 'subdomain'
            else:
                enrichment['subtype'] = 'root_domain'
            
            # Common subdomain patterns
            subdomain = parts[0] if len(parts) > 2 else None
            if subdomain in ['mail', 'email', 'smtp']:
                enrichment['likely_mail_server'] = True
            elif subdomain in ['www', 'www2', 'web']:
                enrichment['likely_web_server'] = True
            elif subdomain in ['ftp']:
                enrichment['likely_ftp_server'] = True
            
        except Exception as e:
            self.logger.debug(f"Domain enrichment failed: {e}")
        
        return enrichment
    
    def _enrich_email(self, email: str) -> Dict[str, Any]:
        """Enrich email entity with additional metadata"""
        enrichment = {}
        
        try:
            # Extract local part and domain
            local_part, domain = email.split('@')
            
            enrichment['local_part'] = local_part
            enrichment['domain_part'] = domain
            
            # Analyze local part patterns
            if '.' in local_part:
                enrichment['pattern'] = 'dot_separated'
                parts = local_part.split('.')
                if len(parts) == 2:
                    enrichment['first_name_guess'] = parts[0]
                    enrichment['last_name_guess'] = parts[1]
            elif '_' in local_part:
                enrichment['pattern'] = 'underscore_separated'
            elif '-' in local_part:
                enrichment['pattern'] = 'dash_separated'
            else:
                enrichment['pattern'] = 'single_string'
            
            # Check for role accounts
            role_prefixes = [
                'admin', 'administrator', 'root', 'support', 'info',
                'sales', 'contact', 'help', 'billing', 'abuse'
            ]
            enrichment['is_role_account'] = local_part.lower() in role_prefixes
            
            # Length analysis
            enrichment['local_part_length'] = len(local_part)
            enrichment['total_length'] = len(email)
            
        except Exception as e:
            self.logger.debug(f"Email enrichment failed: {e}")
        
        return enrichment
    
    def _enrich_social_profile(self, profile: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich social profile entity with additional metadata"""
        enrichment = {}
        
        try:
            # Profile popularity indicators
            follower_count = metadata.get('followers_count', 0)
            following_count = metadata.get('following_count', 0)
            
            if follower_count > 100000:
                enrichment['influence_level'] = 'high'
            elif follower_count > 10000:
                enrichment['influence_level'] = 'medium'
            elif follower_count > 1000:
                enrichment['influence_level'] = 'low'
            else:
                enrichment['influence_level'] = 'minimal'
            
            # Account age
            if 'account_age_days' in metadata:
                age_days = metadata['account_age_days']
                if age_days > 365 * 5:
                    enrichment['account_age_category'] = 'veteran'
                elif age_days > 365 * 2:
                    enrichment['account_age_category'] = 'established'
                elif age_days > 365:
                    enrichment['account_age_category'] = 'moderate'
                else:
                    enrichment['account_age_category'] = 'new'
            
            # Follower ratio
            if following_count > 0:
                enrichment['follower_ratio'] = follower_count / following_count
            
            # Verified status
            enrichment['is_verified'] = metadata.get('verified', False)
            
        except Exception as e:
            self.logger.debug(f"Social profile enrichment failed: {e}")
        
        return enrichment
    
    @staticmethod
    def _format_age(seconds: float) -> str:
        """Format age in seconds to human-readable format"""
        days = seconds / 86400
        if days >= 365:
            return f"{int(days / 365)} years ago"
        elif days >= 30:
            return f"{int(days / 30)} months ago"
        elif days >= 1:
            return f"{int(days)} days ago"
        else:
            hours = seconds / 3600
            return f"{int(hours)} hours ago"
    
    def normalize_timestamps(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert all timestamps to UTC format"""
        normalized = []
        
        for entity in entities:
            normalized_entity = entity.copy()
            metadata = normalized_entity.get('metadata', {})
            
            # Normalize common timestamp fields
            timestamp_fields = ['collected_at', 'created_at', 'updated_at', 'published_at']
            
            for field in timestamp_fields:
                if field in metadata and metadata[field]:
                    try:
                        # Try to parse and normalize timestamp
                        ts = self._normalize_timestamp(metadata[field])
                        metadata[field] = ts.isoformat() if ts else metadata[field]
                    except Exception as e:
                        self.logger.debug(f"Timestamp normalization failed for {field}: {e}")
            
            normalized_entity['metadata'] = metadata
            normalized.append(normalized_entity)
        
        return normalized
    
    @staticmethod
    def _normalize_timestamp(timestamp: Any) -> Optional[datetime]:
        """Normalize timestamp to datetime object"""
        if isinstance(timestamp, datetime):
            return timestamp
        
        if isinstance(timestamp, str):
            # Try multiple datetime formats
            formats = [
                '%Y-%m-%dT%H:%M:%S.%f',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d %H:%M:%S',
                '%Y/%m/%d %H:%M:%S',
                '%Y-%m-%d',
                '%d/%m/%Y %H:%M:%S'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(timestamp, fmt)
                except ValueError:
                    continue
        
        return None
    
    def enrich_timestamps(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add age calculations and temporal patterns"""
        enriched = []
        
        for entity in entities:
            enriched_entity = entity.copy()
            metadata = enriched_entity.get('metadata', {})
            
            # Calculate entity age if timestamp available
            if 'collected_at' in metadata:
                try:
                    collected_time = datetime.fromisoformat(metadata['collected_at'])
                    age_seconds = (datetime.utcnow() - collected_time).total_seconds()
                    
                    # Add age-related metadata
                    metadata['entity_age_seconds'] = age_seconds
                    metadata['entity_age_readable'] = self._format_age(age_seconds)
                    metadata['entity_staleness'] = self._calculate_staleness_level(age_seconds)
                    
                except Exception as e:
                    self.logger.debug(f"Age calculation failed: {e}")
            
            enriched_entity['metadata'] = metadata
            enriched.append(enriched_entity)
        
        return enriched
    
    @staticmethod
    def _calculate_staleness_level(age_seconds: float) -> str:
        """Calculate staleness level based on age"""
        if age_seconds < 3600:  # < 1 hour
            return "fresh"
        elif age_seconds < 86400:  # < 1 day
            return "recent"
        elif age_seconds < 604800:  # < 1 week
            return "aging"
        elif age_seconds < 2592000:  # < 30 days
            return "stale"
        else:
            return "very_stale"
    
    def batch_normalize(self, entity_lists: List[List[Dict[str, Any]]]) -> List[List[Dict[str, Any]]]:
        """
        Parallel processing of entity normalization using Dask
        
        Args:
            entity_lists: List of entity lists to normalize
            
        Returns:
            List of normalized entity lists
        """
        if not entity_lists:
            return []
        
        if not self.use_dask or not DASK_AVAILABLE:
            # Fallback to sequential processing
            self.logger.info("Dask not available, using sequential normalization")
            return [self._normalize_single_batch(entities) for entities in entity_lists]
        
        try:
            self.logger.info(f"Starting batch normalization of {len(entity_lists)} entity lists with Dask")
            
            # Create Dask delayed tasks
            delayed_tasks = [delayed(self._normalize_single_batch)(entities) for entities in entity_lists]
            
            # Execute in parallel
            results = compute(*delayed_tasks)
            
            self.logger.info(f"Batch normalization completed")
            
            return list(results)
            
        except Exception as e:
            self.logger.error(f"Batch normalization failed: {e}")
            # Fallback to sequential
            return [self._normalize_single_batch(entities) for entities in entity_lists]
    
    def _normalize_single_batch(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize a single batch of entities"""
        try:
            # Apply all normalization steps
            deduped, _ = self.deduplicate_entities(entities)
            merged = self.merge_entity_data(deduped)
            normalized_ts = self.normalize_timestamps(merged)
            validated, _ = self.validate_entity_data(normalized_ts)
            enriched = [self.enrich_entity_metadata(entity) for entity in validated]
            timestamp_enriched = self.enrich_timestamps(enriched)
            
            return timestamp_enriched
            
        except Exception as e:
            self.logger.error(f"Single batch normalization failed: {e}")
            return entities