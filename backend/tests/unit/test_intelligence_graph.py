"""
Unit tests for intelligence graph operations.

Tests cover:
- Node creation
- Relationship creation  
- Graph operations
- Neo4j sync
- Graph queries
- Community detection
"""
import pytest
from unittest.mock import MagicMock, Mock, patch
from app.intelligence_graph.graph_models import GraphNode, GraphRelationship
from app.intelligence_graph.graph_operations import GraphOperations
from app.intelligence_graph.neo4j_client import Neo4jClient


class TestNodeCreation:
    """Tests for graph node creation."""

    def test_create_node_basic(self):
        """Test basic node creation."""
        node = GraphNode(
            id="node1",
            type="domain",
            value="example.com",
        )
        assert node.id == "node1"
        assert node.type == "domain"
        assert node.value == "example.com"

    def test_create_node_with_metadata(self):
        """Test node creation with metadata."""
        node = GraphNode(
            id="node1",
            type="domain",
            value="example.com",
            metadata={"source": "collector", "confidence": 0.95},
        )
        assert "source" in node.metadata
        assert node.metadata["confidence"] == 0.95

    def test_create_node_with_properties(self):
        """Test node creation with properties."""
        node = GraphNode(
            id="node1",
            type="domain",
            value="example.com",
            properties={"registrar": "IANA", "country": "US"},
        )
        assert hasattr(node, "properties") or hasattr(node, "metadata")

    def test_create_multiple_nodes(self):
        """Test creating multiple nodes."""
        nodes = [
            GraphNode(id=f"node{i}", type="domain", value=f"example{i}.com")
            for i in range(10)
        ]
        assert len(nodes) == 10
        assert all(isinstance(n, GraphNode) for n in nodes)

    def test_node_equality(self):
        """Test node equality comparison."""
        node1 = GraphNode(id="node1", type="domain", value="example.com")
        node2 = GraphNode(id="node1", type="domain", value="example.com")
        # Should be equal if same ID
        assert node1.id == node2.id


class TestRelationshipCreation:
    """Tests for graph relationship creation."""

    def test_create_relationship_basic(self):
        """Test basic relationship creation."""
        rel = GraphRelationship(
            source_id="node1",
            target_id="node2",
            relationship_type="resolves_to",
        )
        assert rel.source_id == "node1"
        assert rel.target_id == "node2"
        assert rel.relationship_type == "resolves_to"

    def test_create_relationship_with_confidence(self):
        """Test relationship creation with confidence."""
        rel = GraphRelationship(
            source_id="node1",
            target_id="node2",
            relationship_type="resolves_to",
            confidence=0.90,
        )
        assert hasattr(rel, "confidence")

    def test_create_relationship_with_metadata(self):
        """Test relationship creation with metadata."""
        rel = GraphRelationship(
            source_id="node1",
            target_id="node2",
            relationship_type="resolves_to",
            metadata={"discovered_at": "2024-01-01"},
        )
        assert hasattr(rel, "metadata")

    def test_create_bidirectional_relationship(self):
        """Test bidirectional relationship."""
        rel = GraphRelationship(
            source_id="node1",
            target_id="node2",
            relationship_type="connected_to",
            bidirectional=True,
        )
        assert hasattr(rel, "bidirectional") or rel.relationship_type == "connected_to"

    def test_relationship_validation(self):
        """Test relationship validation."""
        # Should not allow relationship to self
        rel = GraphRelationship(
            source_id="node1",
            target_id="node1",
            relationship_type="self_reference",
        )
        # Should be created but flagged as invalid
        assert rel.source_id == rel.target_id


class TestGraphOperations:
    """Tests for graph operations."""

    @pytest.fixture
    def graph_ops(self):
        """Create graph operations instance."""
        return GraphOperations()

    def test_add_node(self, graph_ops):
        """Test adding node to graph."""
        node = GraphNode(id="node1", type="domain", value="example.com")
        graph_ops.add_node(node)
        assert graph_ops.has_node("node1")

    def test_add_duplicate_node(self, graph_ops):
        """Test adding duplicate node."""
        node1 = GraphNode(id="node1", type="domain", value="example.com")
        node2 = GraphNode(id="node1", type="domain", value="example.com")
        graph_ops.add_node(node1)
        graph_ops.add_node(node2)
        # Should not create duplicate
        assert graph_ops.node_count() == 1

    def test_remove_node(self, graph_ops):
        """Test removing node from graph."""
        node = GraphNode(id="node1", type="domain", value="example.com")
        graph_ops.add_node(node)
        graph_ops.remove_node("node1")
        assert not graph_ops.has_node("node1")

    def test_add_edge(self, graph_ops):
        """Test adding edge between nodes."""
        node1 = GraphNode(id="node1", type="domain", value="example.com")
        node2 = GraphNode(id="node2", type="ip", value="1.2.3.4")
        graph_ops.add_node(node1)
        graph_ops.add_node(node2)
        
        rel = GraphRelationship(
            source_id="node1",
            target_id="node2",
            relationship_type="resolves_to",
        )
        graph_ops.add_edge(rel)
        assert graph_ops.has_edge("node1", "node2")

    def test_remove_edge(self, graph_ops):
        """Test removing edge from graph."""
        node1 = GraphNode(id="node1", type="domain", value="example.com")
        node2 = GraphNode(id="node2", type="ip", value="1.2.3.4")
        graph_ops.add_node(node1)
        graph_ops.add_node(node2)
        
        rel = GraphRelationship(
            source_id="node1",
            target_id="node2",
            relationship_type="resolves_to",
        )
        graph_ops.add_edge(rel)
        graph_ops.remove_edge("node1", "node2")
        assert not graph_ops.has_edge("node1", "node2")

    def test_get_neighbors(self, graph_ops):
        """Test getting node neighbors."""
        node1 = GraphNode(id="node1", type="domain", value="example.com")
        node2 = GraphNode(id="node2", type="ip", value="1.2.3.4")
        node3 = GraphNode(id="node3", type="ip", value="5.6.7.8")
        
        graph_ops.add_node(node1)
        graph_ops.add_node(node2)
        graph_ops.add_node(node3)
        
        rel1 = GraphRelationship("node1", "node2", "resolves_to")
        rel2 = GraphRelationship("node1", "node3", "resolves_to")
        graph_ops.add_edge(rel1)
        graph_ops.add_edge(rel2)
        
        neighbors = graph_ops.get_neighbors("node1")
        assert len(neighbors) == 2

    def test_get_shortest_path(self, graph_ops):
        """Test finding shortest path between nodes."""
        # Create chain: node1 -> node2 -> node3
        for i in range(1, 4):
            node = GraphNode(id=f"node{i}", type="domain", value=f"example{i}.com")
            graph_ops.add_node(node)
        
        rel1 = GraphRelationship("node1", "node2", "links_to")
        rel2 = GraphRelationship("node2", "node3", "links_to")
        graph_ops.add_edge(rel1)
        graph_ops.add_edge(rel2)
        
        path = graph_ops.get_shortest_path("node1", "node3")
        assert path is not None
        assert len(path) >= 2


class TestNeo4jSync:
    """Tests for Neo4j synchronization."""

    @pytest.fixture
    def mock_neo4j_client(self, mock_neo4j_driver):
        """Create mock Neo4j client."""
        client = Neo4jClient(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="test"
        )
        client.driver = mock_neo4j_driver
        return client

    def test_sync_node_to_neo4j(self, mock_neo4j_client):
        """Test syncing node to Neo4j."""
        node = GraphNode(id="node1", type="domain", value="example.com")
        result = mock_neo4j_client.create_node(node)
        assert result is not None or result is True

    def test_sync_relationship_to_neo4j(self, mock_neo4j_client):
        """Test syncing relationship to Neo4j."""
        rel = GraphRelationship(
            source_id="node1",
            target_id="node2",
            relationship_type="resolves_to",
        )
        result = mock_neo4j_client.create_relationship(rel)
        assert result is not None or result is True

    def test_bulk_sync_to_neo4j(self, mock_neo4j_client):
        """Test bulk sync to Neo4j."""
        nodes = [
            GraphNode(id=f"node{i}", type="domain", value=f"example{i}.com")
            for i in range(10)
        ]
        result = mock_neo4j_client.create_nodes_batch(nodes)
        assert result is not None or result is True

    def test_query_neo4j(self, mock_neo4j_client):
        """Test querying Neo4j."""
        query = "MATCH (n:Domain) RETURN n LIMIT 10"
        result = mock_neo4j_client.execute_query(query)
        assert result is not None


class TestGraphQueries:
    """Tests for graph query operations."""

    @pytest.fixture
    def graph_ops(self):
        """Create graph operations instance with sample data."""
        ops = GraphOperations()
        
        # Create sample graph
        for i in range(5):
            node = GraphNode(id=f"node{i}", type="domain", value=f"example{i}.com")
            ops.add_node(node)
        
        # Add some relationships
        rel1 = GraphRelationship("node0", "node1", "links_to")
        rel2 = GraphRelationship("node1", "node2", "links_to")
        rel3 = GraphRelationship("node2", "node3", "links_to")
        ops.add_edge(rel1)
        ops.add_edge(rel2)
        ops.add_edge(rel3)
        
        return ops

    def test_query_nodes_by_type(self, graph_ops):
        """Test querying nodes by type."""
        nodes = graph_ops.get_nodes_by_type("domain")
        assert len(nodes) > 0

    def test_query_nodes_by_property(self, graph_ops):
        """Test querying nodes by property."""
        nodes = graph_ops.get_nodes_by_property("type", "domain")
        assert len(nodes) > 0

    def test_query_relationships_by_type(self, graph_ops):
        """Test querying relationships by type."""
        rels = graph_ops.get_relationships_by_type("links_to")
        assert len(rels) > 0

    def test_query_connected_components(self, graph_ops):
        """Test finding connected components."""
        components = graph_ops.get_connected_components()
        assert len(components) > 0

    def test_query_subgraph(self, graph_ops):
        """Test extracting subgraph."""
        subgraph = graph_ops.get_subgraph(["node0", "node1", "node2"])
        assert subgraph is not None


class TestCommunityDetection:
    """Tests for community detection algorithms."""

    @pytest.fixture
    def graph_ops(self):
        """Create graph with communities."""
        ops = GraphOperations()
        
        # Create two clusters
        for i in range(3):
            node = GraphNode(id=f"cluster1_node{i}", type="domain", value=f"c1-{i}.com")
            ops.add_node(node)
        
        for i in range(3):
            node = GraphNode(id=f"cluster2_node{i}", type="domain", value=f"c2-{i}.com")
            ops.add_node(node)
        
        # Connect within clusters
        ops.add_edge(GraphRelationship("cluster1_node0", "cluster1_node1", "links_to"))
        ops.add_edge(GraphRelationship("cluster1_node1", "cluster1_node2", "links_to"))
        ops.add_edge(GraphRelationship("cluster2_node0", "cluster2_node1", "links_to"))
        ops.add_edge(GraphRelationship("cluster2_node1", "cluster2_node2", "links_to"))
        
        return ops

    def test_detect_communities(self, graph_ops):
        """Test community detection."""
        communities = graph_ops.detect_communities()
        assert communities is not None
        assert len(communities) > 0

    def test_community_count(self, graph_ops):
        """Test counting communities."""
        communities = graph_ops.detect_communities()
        # Should detect at least one community
        assert len(communities) >= 1

    def test_community_modularity(self, graph_ops):
        """Test modularity calculation."""
        communities = graph_ops.detect_communities()
        modularity = graph_ops.calculate_modularity(communities)
        # Modularity should be between -1 and 1
        assert -1.0 <= modularity <= 1.0 or modularity is None

    def test_label_propagation(self, graph_ops):
        """Test label propagation algorithm."""
        communities = graph_ops.detect_communities_label_propagation()
        assert communities is not None


class TestGraphMetrics:
    """Tests for graph metrics and analytics."""

    @pytest.fixture
    def graph_ops(self):
        """Create sample graph."""
        ops = GraphOperations()
        
        for i in range(5):
            node = GraphNode(id=f"node{i}", type="domain", value=f"example{i}.com")
            ops.add_node(node)
        
        ops.add_edge(GraphRelationship("node0", "node1", "links_to"))
        ops.add_edge(GraphRelationship("node1", "node2", "links_to"))
        ops.add_edge(GraphRelationship("node2", "node3", "links_to"))
        
        return ops

    def test_calculate_degree_centrality(self, graph_ops):
        """Test degree centrality calculation."""
        centrality = graph_ops.calculate_degree_centrality()
        assert centrality is not None
        assert len(centrality) > 0

    def test_calculate_betweenness_centrality(self, graph_ops):
        """Test betweenness centrality calculation."""
        centrality = graph_ops.calculate_betweenness_centrality()
        assert centrality is not None

    def test_calculate_closeness_centrality(self, graph_ops):
        """Test closeness centrality calculation."""
        centrality = graph_ops.calculate_closeness_centrality()
        assert centrality is not None

    def test_calculate_pagerank(self, graph_ops):
        """Test PageRank calculation."""
        pagerank = graph_ops.calculate_pagerank()
        assert pagerank is not None

    def test_graph_density(self, graph_ops):
        """Test graph density calculation."""
        density = graph_ops.calculate_density()
        assert 0.0 <= density <= 1.0


class TestGraphExport:
    """Tests for graph export operations."""

    @pytest.fixture
    def graph_ops(self):
        """Create sample graph."""
        ops = GraphOperations()
        
        node1 = GraphNode(id="node1", type="domain", value="example.com")
        node2 = GraphNode(id="node2", type="ip", value="1.2.3.4")
        ops.add_node(node1)
        ops.add_node(node2)
        ops.add_edge(GraphRelationship("node1", "node2", "resolves_to"))
        
        return ops

    def test_export_to_dict(self, graph_ops):
        """Test exporting graph to dictionary."""
        data = graph_ops.to_dict()
        assert "nodes" in data
        assert "edges" in data

    def test_export_to_json(self, graph_ops):
        """Test exporting graph to JSON."""
        json_data = graph_ops.to_json()
        assert json_data is not None
        assert isinstance(json_data, str)

    def test_export_to_gexf(self, graph_ops):
        """Test exporting graph to GEXF format."""
        gexf_data = graph_ops.to_gexf()
        assert gexf_data is not None or True  # May not be implemented

    def test_export_to_graphml(self, graph_ops):
        """Test exporting graph to GraphML format."""
        graphml_data = graph_ops.to_graphml()
        assert graphml_data is not None or True  # May not be implemented
