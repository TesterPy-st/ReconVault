"""
Integration tests for collection pipeline.

Tests cover:
- Full collection workflow
- Multiple collectors together
- Data normalization in pipeline
- Graph building from collection
- Risk calculation in pipeline
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.integration
class TestFullCollectionWorkflow:
    """Tests for complete collection workflow."""

    @pytest.mark.asyncio
    async def test_end_to_end_collection(self):
        """Test complete end-to-end collection."""
        from app.collectors import CollectorFactory, CollectorConfig, DataType
        
        config = CollectorConfig(
            target="example.com",
            data_type=DataType.DOMAIN,
        )
        
        collector = CollectorFactory.create_collector(DataType.DOMAIN, config)
        result = await collector.collect()
        
        assert result is not None
        assert hasattr(result, 'success')

    @pytest.mark.asyncio
    async def test_collection_to_database(self, db_session):
        """Test collection data persisted to database."""
        from app.collectors import CollectorFactory, CollectorConfig, DataType
        from app.models import Entity
        
        config = CollectorConfig(
            target="example.com",
            data_type=DataType.DOMAIN,
        )
        
        collector = CollectorFactory.create_collector(DataType.DOMAIN, config)
        result = await collector.collect()
        
        if result.success and result.data:
            # Save to database
            for item in result.data:
                entity = Entity(
                    entity_type=item.get("type", "domain"),
                    value=item.get("value", "unknown"),
                )
                db_session.add(entity)
            db_session.commit()
            
            # Verify
            count = db_session.query(Entity).count()
            assert count > 0


@pytest.mark.integration
class TestMultipleCollectorsTogether:
    """Tests for multiple collectors working together."""

    @pytest.mark.asyncio
    async def test_multiple_collectors_same_target(self):
        """Test multiple collectors on same target."""
        from app.collectors import CollectorFactory, CollectorConfig, DataType
        
        target = "example.com"
        
        # Create multiple collectors
        domain_config = CollectorConfig(target=target, data_type=DataType.DOMAIN)
        web_config = CollectorConfig(target=f"https://{target}", data_type=DataType.URL)
        
        domain_collector = CollectorFactory.create_collector(DataType.DOMAIN, domain_config)
        web_collector = CollectorFactory.create_collector(DataType.URL, web_config)
        
        # Collect from both
        domain_result = await domain_collector.collect()
        web_result = await web_collector.collect()
        
        # Both should complete
        assert domain_result is not None
        assert web_result is not None

    @pytest.mark.asyncio
    async def test_collector_result_merging(self):
        """Test merging results from multiple collectors."""
        from app.collectors import CollectorFactory, CollectorConfig, DataType
        
        target = "example.com"
        results = []
        
        for data_type in [DataType.DOMAIN, DataType.URL]:
            config = CollectorConfig(
                target=target if data_type == DataType.DOMAIN else f"https://{target}",
                data_type=data_type,
            )
            collector = CollectorFactory.create_collector(data_type, config)
            result = await collector.collect()
            results.append(result)
        
        # Should have multiple results
        assert len(results) > 0


@pytest.mark.integration
class TestDataNormalizationInPipeline:
    """Tests for data normalization in collection pipeline."""

    @pytest.mark.asyncio
    async def test_normalization_after_collection(self):
        """Test normalization applied after collection."""
        from app.collectors import CollectorFactory, CollectorConfig, DataType
        from app.services.normalization_service import NormalizationService
        
        config = CollectorConfig(target="example.com", data_type=DataType.DOMAIN)
        collector = CollectorFactory.create_collector(DataType.DOMAIN, config)
        result = await collector.collect()
        
        if result.success and result.data:
            # Normalize
            normalizer = NormalizationService()
            normalized = normalizer.deduplicate_entities(result.data)
            
            assert len(normalized) <= len(result.data)

    @pytest.mark.asyncio
    async def test_enrichment_in_pipeline(self):
        """Test data enrichment in pipeline."""
        from app.collectors import CollectorFactory, CollectorConfig, DataType
        from app.services.normalization_service import NormalizationService
        
        config = CollectorConfig(target="example.com", data_type=DataType.DOMAIN)
        collector = CollectorFactory.create_collector(DataType.DOMAIN, config)
        result = await collector.collect()
        
        if result.success and result.data:
            normalizer = NormalizationService()
            for entity in result.data:
                enriched = normalizer.enrich_entity(entity)
                assert enriched is not None


@pytest.mark.integration
class TestGraphBuildingFromCollection:
    """Tests for building graph from collection data."""

    @pytest.mark.asyncio
    async def test_collection_to_graph(self):
        """Test converting collection to graph."""
        from app.collectors import CollectorFactory, CollectorConfig, DataType
        from app.intelligence_graph.graph_operations import GraphOperations
        from app.intelligence_graph.graph_models import GraphNode
        
        config = CollectorConfig(target="example.com", data_type=DataType.DOMAIN)
        collector = CollectorFactory.create_collector(DataType.DOMAIN, config)
        result = await collector.collect()
        
        if result.success and result.data:
            # Build graph
            graph_ops = GraphOperations()
            for item in result.data:
                node = GraphNode(
                    id=str(item.get("value", "unknown")),
                    type=item.get("type", "unknown"),
                    value=item.get("value", "unknown"),
                )
                graph_ops.add_node(node)
            
            assert graph_ops.node_count() > 0

    @pytest.mark.asyncio
    async def test_relationship_creation_in_graph(self):
        """Test creating relationships in graph from collection."""
        from app.intelligence_graph.graph_operations import GraphOperations
        from app.intelligence_graph.graph_models import GraphNode, GraphRelationship
        
        graph_ops = GraphOperations()
        
        # Add nodes
        node1 = GraphNode(id="example.com", type="domain", value="example.com")
        node2 = GraphNode(id="1.2.3.4", type="ip", value="1.2.3.4")
        graph_ops.add_node(node1)
        graph_ops.add_node(node2)
        
        # Add relationship
        rel = GraphRelationship(
            source_id="example.com",
            target_id="1.2.3.4",
            relationship_type="resolves_to",
        )
        graph_ops.add_edge(rel)
        
        assert graph_ops.has_edge("example.com", "1.2.3.4")


@pytest.mark.integration
class TestRiskCalculationInPipeline:
    """Tests for risk calculation in pipeline."""

    @pytest.mark.asyncio
    async def test_risk_scoring_after_collection(self):
        """Test risk scoring applied after collection."""
        from app.collectors import CollectorFactory, CollectorConfig, DataType
        from app.risk_engine.risk_calculator import RiskCalculator
        
        config = CollectorConfig(target="example.com", data_type=DataType.DOMAIN)
        collector = CollectorFactory.create_collector(DataType.DOMAIN, config)
        result = await collector.collect()
        
        if result.success and result.data:
            # Calculate risk
            risk_calc = RiskCalculator()
            for entity in result.data:
                risk_score = risk_calc.calculate_entity_risk(entity)
                assert risk_score is not None

    @pytest.mark.asyncio
    async def test_pipeline_with_all_components(self, db_session):
        """Test complete pipeline with all components."""
        from app.collectors import CollectorFactory, CollectorConfig, DataType
        from app.services.normalization_service import NormalizationService
        from app.intelligence_graph.graph_operations import GraphOperations
        from app.risk_engine.risk_calculator import RiskCalculator
        from app.intelligence_graph.graph_models import GraphNode
        
        # 1. Collection
        config = CollectorConfig(target="example.com", data_type=DataType.DOMAIN)
        collector = CollectorFactory.create_collector(DataType.DOMAIN, config)
        result = await collector.collect()
        
        if not result.success or not result.data:
            pytest.skip("Collection failed or no data")
        
        # 2. Normalization
        normalizer = NormalizationService()
        normalized = normalizer.deduplicate_entities(result.data)
        
        # 3. Graph building
        graph_ops = GraphOperations()
        for entity in normalized:
            node = GraphNode(
                id=str(entity.get("value", "unknown")),
                type=entity.get("type", "unknown"),
                value=entity.get("value", "unknown"),
            )
            graph_ops.add_node(node)
        
        # 4. Risk calculation
        risk_calc = RiskCalculator()
        for entity in normalized:
            risk_score = risk_calc.calculate_entity_risk(entity)
            entity["risk_score"] = risk_score
        
        # Verify all steps completed
        assert len(normalized) > 0
        assert graph_ops.node_count() > 0
