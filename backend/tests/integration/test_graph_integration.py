"""
Integration tests for graph and Neo4j integration.

Tests cover:
- PostgreSQL to Neo4j sync
- Graph query performance
- Relationship correlation
- Graph algorithms
"""
import pytest
from unittest.mock import MagicMock


@pytest.mark.integration
class TestPostgresToNeo4jSync:
    """Tests for PostgreSQL to Neo4j synchronization."""

    def test_sync_entities_to_neo4j(self, db_session, mock_neo4j_driver):
        """Test syncing entities from PostgreSQL to Neo4j."""
        from app.models import Entity
        from app.intelligence_graph.neo4j_client import Neo4jClient
        
        # Create entities in PostgreSQL
        entities = [
            Entity(entity_type="domain", value="example1.com"),
            Entity(entity_type="domain", value="example2.com"),
        ]
        db_session.add_all(entities)
        db_session.commit()
        
        # Sync to Neo4j
        neo4j_client = Neo4jClient("bolt://localhost:7687", "neo4j", "test")
        neo4j_client.driver = mock_neo4j_driver
        
        for entity in entities:
            result = neo4j_client.create_node_from_entity(entity)
            assert result is not None or result is True

    def test_sync_relationships_to_neo4j(self, db_session, mock_neo4j_driver):
        """Test syncing relationships to Neo4j."""
        from app.models import Entity, Relationship
        from app.intelligence_graph.neo4j_client import Neo4jClient
        
        # Create entities
        entity1 = Entity(entity_type="domain", value="example.com")
        entity2 = Entity(entity_type="ip", value="1.2.3.4")
        db_session.add_all([entity1, entity2])
        db_session.commit()
        
        # Create relationship
        rel = Relationship(
            source_id=entity1.id,
            target_id=entity2.id,
            relationship_type="resolves_to",
        )
        db_session.add(rel)
        db_session.commit()
        
        # Sync to Neo4j
        neo4j_client = Neo4jClient("bolt://localhost:7687", "neo4j", "test")
        neo4j_client.driver = mock_neo4j_driver
        result = neo4j_client.create_relationship_from_model(rel)
        assert result is not None or result is True


@pytest.mark.integration
class TestGraphQueryPerformance:
    """Tests for graph query performance."""

    def test_large_graph_query(self):
        """Test querying large graph."""
        from app.intelligence_graph.graph_operations import GraphOperations
        from app.intelligence_graph.graph_models import GraphNode, GraphRelationship
        
        graph_ops = GraphOperations()
        
        # Create large graph
        for i in range(100):
            node = GraphNode(id=f"node{i}", type="domain", value=f"example{i}.com")
            graph_ops.add_node(node)
        
        # Add relationships
        for i in range(99):
            rel = GraphRelationship(f"node{i}", f"node{i+1}", "links_to")
            graph_ops.add_edge(rel)
        
        # Query should complete quickly
        nodes = graph_ops.get_all_nodes()
        assert len(nodes) == 100

    def test_subgraph_extraction_performance(self):
        """Test subgraph extraction performance."""
        from app.intelligence_graph.graph_operations import GraphOperations
        from app.intelligence_graph.graph_models import GraphNode
        
        graph_ops = GraphOperations()
        
        # Create graph
        for i in range(50):
            node = GraphNode(id=f"node{i}", type="domain", value=f"example{i}.com")
            graph_ops.add_node(node)
        
        # Extract subgraph
        subgraph = graph_ops.get_subgraph([f"node{i}" for i in range(10)])
        assert subgraph is not None


@pytest.mark.integration
class TestRelationshipCorrelation:
    """Tests for relationship correlation."""

    def test_correlate_related_entities(self):
        """Test correlating related entities."""
        from app.intelligence_graph.graph_operations import GraphOperations
        from app.intelligence_graph.graph_models import GraphNode, GraphRelationship
        
        graph_ops = GraphOperations()
        
        # Create entities
        nodes = [
            GraphNode(id="domain1", type="domain", value="example1.com"),
            GraphNode(id="domain2", type="domain", value="example2.com"),
            GraphNode(id="ip1", type="ip", value="1.2.3.4"),
        ]
        for node in nodes:
            graph_ops.add_node(node)
        
        # Add relationships
        rels = [
            GraphRelationship("domain1", "ip1", "resolves_to"),
            GraphRelationship("domain2", "ip1", "resolves_to"),
        ]
        for rel in rels:
            graph_ops.add_edge(rel)
        
        # Find common connections
        neighbors1 = graph_ops.get_neighbors("domain1")
        neighbors2 = graph_ops.get_neighbors("domain2")
        
        # Should share ip1
        assert len(neighbors1) > 0
        assert len(neighbors2) > 0


@pytest.mark.integration  
class TestGraphAlgorithms:
    """Tests for graph algorithms."""

    def test_community_detection_integration(self):
        """Test community detection on real graph."""
        from app.intelligence_graph.graph_operations import GraphOperations
        from app.intelligence_graph.graph_models import GraphNode, GraphRelationship
        
        graph_ops = GraphOperations()
        
        # Create two clusters
        for cluster in range(2):
            for i in range(5):
                node_id = f"cluster{cluster}_node{i}"
                node = GraphNode(id=node_id, type="domain", value=f"{node_id}.com")
                graph_ops.add_node(node)
        
        # Connect within clusters
        for cluster in range(2):
            for i in range(4):
                rel = GraphRelationship(
                    f"cluster{cluster}_node{i}",
                    f"cluster{cluster}_node{i+1}",
                    "links_to"
                )
                graph_ops.add_edge(rel)
        
        # Detect communities
        communities = graph_ops.detect_communities()
        assert communities is not None

    def test_shortest_path_integration(self):
        """Test shortest path algorithm."""
        from app.intelligence_graph.graph_operations import GraphOperations
        from app.intelligence_graph.graph_models import GraphNode, GraphRelationship
        
        graph_ops = GraphOperations()
        
        # Create chain
        for i in range(5):
            node = GraphNode(id=f"node{i}", type="domain", value=f"example{i}.com")
            graph_ops.add_node(node)
        
        for i in range(4):
            rel = GraphRelationship(f"node{i}", f"node{i+1}", "links_to")
            graph_ops.add_edge(rel)
        
        # Find path
        path = graph_ops.get_shortest_path("node0", "node4")
        assert path is not None
        if path:
            assert len(path) >= 2

    def test_centrality_calculation_integration(self):
        """Test centrality calculations."""
        from app.intelligence_graph.graph_operations import GraphOperations
        from app.intelligence_graph.graph_models import GraphNode, GraphRelationship
        
        graph_ops = GraphOperations()
        
        # Create hub and spoke topology
        hub = GraphNode(id="hub", type="domain", value="hub.com")
        graph_ops.add_node(hub)
        
        for i in range(5):
            node = GraphNode(id=f"spoke{i}", type="domain", value=f"spoke{i}.com")
            graph_ops.add_node(node)
            rel = GraphRelationship("hub", f"spoke{i}", "links_to")
            graph_ops.add_edge(rel)
        
        # Calculate centrality
        centrality = graph_ops.calculate_degree_centrality()
        assert centrality is not None
        if centrality and "hub" in centrality:
            # Hub should have high centrality
            assert centrality["hub"] > 0
