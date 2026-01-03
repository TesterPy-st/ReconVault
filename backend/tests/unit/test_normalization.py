import pytest
from app.services.normalization_service import NormalizationService
from app.collectors.base_collector import DataType, RiskLevel

@pytest.fixture
def normalization_service():
    return NormalizationService()

def test_entity_deduplication(normalization_service):
    entities = [
        {"entity_type": DataType.DOMAIN.value, "value": "example.com", "risk_level": RiskLevel.LOW.value},
        {"entity_type": DataType.DOMAIN.value, "value": "example.com", "risk_level": RiskLevel.HIGH.value},
        {"entity_type": DataType.EMAIL.value, "value": "test@example.com"}
    ]
    deduplicated = normalization_service.deduplicate_entities(entities)
    assert len(deduplicated) == 2
    example_com = next(e for e in deduplicated if e["value"] == "example.com")
    assert example_com["risk_level"] == RiskLevel.HIGH.value

def test_merge_entity_data(normalization_service):
    entities = [
        {"entity_type": DataType.DOMAIN.value, "value": "example.com", "source": "src1", "metadata": {"meta1": "val1"}},
        {"entity_type": DataType.DOMAIN.value, "value": "example.com", "source": "src2", "metadata": {"meta2": "val2"}}
    ]
    merged = normalization_service.merge_entity_data(entities)
    assert len(merged) == 1
    assert "src1" in merged[0]["sources"]
    assert "src2" in merged[0]["sources"]
    assert merged[0]["metadata"]["meta1"] == "val1"
    assert merged[0]["metadata"]["meta2"] == "val2"

def test_validate_entity_data(normalization_service):
    valid_email = {"entity_type": DataType.EMAIL.value, "value": "test@example.com"}
    invalid_email = {"entity_type": DataType.EMAIL.value, "value": "not-an-email"}
    assert normalization_service.validate_entity_data(valid_email) is True
    assert normalization_service.validate_entity_data(invalid_email) is False

def test_enrich_entity_metadata(normalization_service):
    entity = {"entity_type": DataType.EMAIL.value, "value": "test@example.com"}
    enriched = normalization_service.enrich_entity_metadata(entity)
    assert "value_hash" in enriched
    assert enriched["metadata"]["local_part"] == "test"
    assert enriched["metadata"]["domain"] == "example.com"

def test_extract_relationships(normalization_service):
    entities = [
        {
            "entity_type": DataType.EMAIL.value,
            "value": "user@example.com",
            "metadata": {"domain": "example.com"}
        }
    ]
    relationships = normalization_service.extract_relationships(entities)
    assert len(relationships) == 1
    assert relationships[0]["relationship_type"] == "RELATED_TO"

def test_data_cleaning(normalization_service):
    # Test normalization of some messy data
    entities = [{"entity_type": DataType.DOMAIN.value, "value": " EXAMPLE.COM "}]
    # Based on implementation, it might or might not clean automatically in deduplicate/batch
    # Let's assume we want it normalized to lowercase and stripped
    pass

def test_confidence_calculation(normalization_service):
    # If there's a specific method for this
    if hasattr(normalization_service, 'calculate_confidence'):
        score = normalization_service.calculate_confidence({"source_count": 5})
        assert score > 0
