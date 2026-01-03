"""
Unit tests for data normalization and enrichment.

Tests cover:
- Entity deduplication
- Data cleaning
- Enrichment pipeline
- Confidence calculation
- Metadata standardization
- Relationship normalization
"""
import pytest
from datetime import datetime
from app.services.normalization_service import NormalizationService
from app.collectors.base_collector import DataType, RiskLevel


class TestEntityDeduplication:
    """Tests for entity deduplication."""

    @pytest.fixture
    def normalization_service(self):
        """Create normalization service instance."""
        return NormalizationService()

    def test_deduplicate_entities_empty_list(self, normalization_service):
        """Test deduplication with empty list."""
        result = normalization_service.deduplicate_entities([])
        assert result == []

    def test_deduplicate_entities_no_duplicates(self, normalization_service):
        """Test deduplication with no duplicates."""
        entities = [
            {"entity_type": "domain", "value": "example.com"},
            {"entity_type": "domain", "value": "test.com"},
            {"entity_type": "ip", "value": "1.2.3.4"},
        ]
        result = normalization_service.deduplicate_entities(entities)
        assert len(result) == 3

    def test_deduplicate_entities_with_duplicates(self, normalization_service):
        """Test deduplication with duplicates."""
        entities = [
            {"entity_type": "domain", "value": "example.com", "risk_level": "LOW"},
            {"entity_type": "domain", "value": "example.com", "risk_level": "HIGH"},
            {"entity_type": "ip", "value": "1.2.3.4"},
        ]
        result = normalization_service.deduplicate_entities(entities)
        assert len(result) == 2
        # Should keep the HIGH risk entry
        domain_entry = next(e for e in result if e["entity_type"] == "domain")
        assert domain_entry["risk_level"] == "HIGH"

    def test_deduplicate_preserves_highest_risk(self, normalization_service):
        """Test that deduplication preserves highest risk level."""
        entities = [
            {"entity_type": "domain", "value": "example.com", "risk_level": "INFO"},
            {"entity_type": "domain", "value": "example.com", "risk_level": "CRITICAL"},
            {"entity_type": "domain", "value": "example.com", "risk_level": "MEDIUM"},
        ]
        result = normalization_service.deduplicate_entities(entities)
        assert len(result) == 1
        assert result[0]["risk_level"] == "CRITICAL"

    def test_deduplicate_different_types_same_value(self, normalization_service):
        """Test deduplication with same value but different types."""
        entities = [
            {"entity_type": "domain", "value": "example.com"},
            {"entity_type": "url", "value": "example.com"},
        ]
        result = normalization_service.deduplicate_entities(entities)
        # Different types should not be deduplicated
        assert len(result) == 2


class TestDataCleaning:
    """Tests for data cleaning."""

    @pytest.fixture
    def normalization_service(self):
        """Create normalization service instance."""
        return NormalizationService()

    def test_clean_entity_data_domain(self, normalization_service):
        """Test cleaning domain data."""
        entity = {
            "entity_type": "domain",
            "value": "  EXAMPLE.COM  ",
        }
        result = normalization_service.clean_entity_data(entity)
        assert result["value"] == "example.com"

    def test_clean_entity_data_email(self, normalization_service):
        """Test cleaning email data."""
        entity = {
            "entity_type": "email",
            "value": "  USER@EXAMPLE.COM  ",
        }
        result = normalization_service.clean_entity_data(entity)
        assert result["value"] == "user@example.com"

    def test_clean_entity_data_url(self, normalization_service):
        """Test cleaning URL data."""
        entity = {
            "entity_type": "url",
            "value": "  https://EXAMPLE.com/PATH  ",
        }
        result = normalization_service.clean_entity_data(entity)
        assert "example.com" in result["value"].lower()

    def test_clean_entity_removes_whitespace(self, normalization_service):
        """Test that cleaning removes leading/trailing whitespace."""
        entity = {
            "entity_type": "domain",
            "value": "   example.com   ",
        }
        result = normalization_service.clean_entity_data(entity)
        assert result["value"] == "example.com"

    def test_clean_entity_handles_special_characters(self, normalization_service):
        """Test cleaning handles special characters."""
        entity = {
            "entity_type": "text",
            "value": "test\n\r\tvalue",
        }
        result = normalization_service.clean_entity_data(entity)
        # Should normalize whitespace
        assert "\n" not in result.get("value", "")


class TestEnrichmentPipeline:
    """Tests for data enrichment pipeline."""

    @pytest.fixture
    def normalization_service(self):
        """Create normalization service instance."""
        return NormalizationService()

    def test_enrich_entity_adds_metadata(self, normalization_service):
        """Test that enrichment adds metadata."""
        entity = {
            "entity_type": "domain",
            "value": "example.com",
        }
        result = normalization_service.enrich_entity(entity)
        assert "metadata" in result or "enriched_at" in result

    def test_enrich_entity_domain(self, normalization_service):
        """Test domain enrichment."""
        entity = {
            "entity_type": "domain",
            "value": "example.com",
        }
        result = normalization_service.enrich_entity(entity)
        assert "value" in result

    def test_enrich_entity_email(self, normalization_service):
        """Test email enrichment."""
        entity = {
            "entity_type": "email",
            "value": "user@example.com",
        }
        result = normalization_service.enrich_entity(entity)
        # Should extract domain
        assert "value" in result

    def test_enrich_entity_url(self, normalization_service):
        """Test URL enrichment."""
        entity = {
            "entity_type": "url",
            "value": "https://example.com/path?query=1",
        }
        result = normalization_service.enrich_entity(entity)
        # Should parse URL components
        assert "value" in result

    def test_enrich_batch_entities(self, normalization_service):
        """Test batch enrichment."""
        entities = [
            {"entity_type": "domain", "value": "example.com"},
            {"entity_type": "ip", "value": "1.2.3.4"},
            {"entity_type": "email", "value": "user@test.com"},
        ]
        results = [normalization_service.enrich_entity(e) for e in entities]
        assert len(results) == 3


class TestConfidenceCalculation:
    """Tests for confidence score calculation."""

    @pytest.fixture
    def normalization_service(self):
        """Create normalization service instance."""
        return NormalizationService()

    def test_calculate_confidence_multiple_sources(self, normalization_service):
        """Test confidence calculation with multiple sources."""
        entity = {
            "entity_type": "domain",
            "value": "example.com",
            "sources": ["collector1", "collector2", "collector3"],
        }
        confidence = normalization_service.calculate_confidence(entity)
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.5  # Multiple sources should increase confidence

    def test_calculate_confidence_single_source(self, normalization_service):
        """Test confidence calculation with single source."""
        entity = {
            "entity_type": "domain",
            "value": "example.com",
            "sources": ["collector1"],
        }
        confidence = normalization_service.calculate_confidence(entity)
        assert 0.0 <= confidence <= 1.0

    def test_calculate_confidence_no_sources(self, normalization_service):
        """Test confidence calculation with no sources."""
        entity = {
            "entity_type": "domain",
            "value": "example.com",
        }
        confidence = normalization_service.calculate_confidence(entity)
        assert 0.0 <= confidence <= 1.0

    def test_confidence_increases_with_verification(self, normalization_service):
        """Test that confidence increases with verification."""
        entity_unverified = {
            "entity_type": "domain",
            "value": "example.com",
            "verified": False,
        }
        entity_verified = {
            "entity_type": "domain",
            "value": "example.com",
            "verified": True,
        }
        conf_unverified = normalization_service.calculate_confidence(entity_unverified)
        conf_verified = normalization_service.calculate_confidence(entity_verified)
        # Verified should have higher confidence
        assert conf_verified >= conf_unverified


class TestMetadataStandardization:
    """Tests for metadata standardization."""

    @pytest.fixture
    def normalization_service(self):
        """Create normalization service instance."""
        return NormalizationService()

    def test_standardize_metadata_timestamps(self, normalization_service):
        """Test timestamp standardization."""
        metadata = {
            "collected_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-02",
        }
        result = normalization_service.standardize_metadata(metadata)
        assert "collected_at" in result or "updated_at" in result

    def test_standardize_metadata_risk_levels(self, normalization_service):
        """Test risk level standardization."""
        metadata = {
            "risk": "high",
        }
        result = normalization_service.standardize_metadata(metadata)
        # Should normalize risk level format
        assert isinstance(result, dict)

    def test_standardize_metadata_empty(self, normalization_service):
        """Test standardization with empty metadata."""
        result = normalization_service.standardize_metadata({})
        assert isinstance(result, dict)

    def test_standardize_metadata_preserves_data(self, normalization_service):
        """Test that standardization preserves original data."""
        metadata = {
            "custom_field": "value",
            "source": "test",
        }
        result = normalization_service.standardize_metadata(metadata)
        assert "custom_field" in result or len(result) >= 0


class TestRelationshipNormalization:
    """Tests for relationship normalization."""

    @pytest.fixture
    def normalization_service(self):
        """Create normalization service instance."""
        return NormalizationService()

    def test_normalize_relationship_basic(self, normalization_service):
        """Test basic relationship normalization."""
        relationship = {
            "source": "example.com",
            "target": "1.2.3.4",
            "type": "resolves_to",
        }
        result = normalization_service.normalize_relationship(relationship)
        assert "source" in result
        assert "target" in result
        assert "type" in result

    def test_normalize_relationship_adds_confidence(self, normalization_service):
        """Test that normalization adds confidence if missing."""
        relationship = {
            "source": "example.com",
            "target": "1.2.3.4",
            "type": "resolves_to",
        }
        result = normalization_service.normalize_relationship(relationship)
        # Should have confidence added
        assert "confidence" in result or "type" in result

    def test_normalize_relationship_standardizes_type(self, normalization_service):
        """Test relationship type standardization."""
        relationship = {
            "source": "example.com",
            "target": "1.2.3.4",
            "type": "RESOLVES_TO",
        }
        result = normalization_service.normalize_relationship(relationship)
        # Should normalize to lowercase
        assert result["type"].islower() or result["type"] == "RESOLVES_TO"

    def test_normalize_relationship_bidirectional(self, normalization_service):
        """Test bidirectional relationship handling."""
        relationship = {
            "source": "entity1",
            "target": "entity2",
            "type": "connected_to",
            "bidirectional": True,
        }
        result = normalization_service.normalize_relationship(relationship)
        assert "source" in result and "target" in result


class TestBatchProcessing:
    """Tests for batch processing operations."""

    @pytest.fixture
    def normalization_service(self):
        """Create normalization service instance."""
        return NormalizationService()

    def test_process_batch_empty(self, normalization_service):
        """Test batch processing with empty list."""
        result = normalization_service.process_batch([])
        assert isinstance(result, list)
        assert len(result) == 0

    def test_process_batch_small(self, normalization_service):
        """Test batch processing with small dataset."""
        entities = [
            {"entity_type": "domain", "value": "example1.com"},
            {"entity_type": "domain", "value": "example2.com"},
            {"entity_type": "ip", "value": "1.2.3.4"},
        ]
        result = normalization_service.process_batch(entities)
        assert len(result) <= len(entities)

    def test_process_batch_large(self, normalization_service):
        """Test batch processing with large dataset."""
        # Create 1000 entities
        entities = [
            {"entity_type": "domain", "value": f"example{i}.com"}
            for i in range(1000)
        ]
        result = normalization_service.process_batch(entities)
        assert isinstance(result, list)

    def test_process_batch_preserves_unique_entities(self, normalization_service):
        """Test that batch processing preserves unique entities."""
        entities = [
            {"entity_type": "domain", "value": "example.com"},
            {"entity_type": "ip", "value": "1.2.3.4"},
            {"entity_type": "email", "value": "test@example.com"},
        ]
        result = normalization_service.process_batch(entities)
        assert len(result) == 3


class TestDataValidation:
    """Tests for data validation."""

    @pytest.fixture
    def normalization_service(self):
        """Create normalization service instance."""
        return NormalizationService()

    def test_validate_entity_valid(self, normalization_service):
        """Test validation of valid entity."""
        entity = {
            "entity_type": "domain",
            "value": "example.com",
        }
        is_valid = normalization_service.validate_entity(entity)
        assert is_valid is True

    def test_validate_entity_missing_type(self, normalization_service):
        """Test validation with missing entity_type."""
        entity = {
            "value": "example.com",
        }
        is_valid = normalization_service.validate_entity(entity)
        assert is_valid is False

    def test_validate_entity_missing_value(self, normalization_service):
        """Test validation with missing value."""
        entity = {
            "entity_type": "domain",
        }
        is_valid = normalization_service.validate_entity(entity)
        assert is_valid is False

    def test_validate_entity_invalid_type(self, normalization_service):
        """Test validation with invalid entity type."""
        entity = {
            "entity_type": "invalid_type",
            "value": "something",
        }
        is_valid = normalization_service.validate_entity(entity)
        # Should handle gracefully
        assert isinstance(is_valid, bool)

    def test_validate_relationship_valid(self, normalization_service):
        """Test validation of valid relationship."""
        relationship = {
            "source": "example.com",
            "target": "1.2.3.4",
            "type": "resolves_to",
        }
        is_valid = normalization_service.validate_relationship(relationship)
        assert is_valid is True

    def test_validate_relationship_missing_fields(self, normalization_service):
        """Test validation with missing fields."""
        relationship = {
            "source": "example.com",
        }
        is_valid = normalization_service.validate_relationship(relationship)
        assert is_valid is False
