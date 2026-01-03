import pytest
from unittest.mock import MagicMock, patch
from app.intelligence_graph.graph_operations import GraphOperations
from app.intelligence_graph.graph_models import NodeType, RelationshipType

@pytest.fixture
def mock_neo4j_client():
    with patch('app.intelligence_graph.graph_operations.get_neo4j_client') as mock_get:
        client = MagicMock()
        mock_get.return_value = client
        yield client

def test_node_creation(mock_neo4j_client):
    ops = GraphOperations()
    properties = {"name": "Test Target"}
    mock_neo4j_client.create_node.return_value = {"id": 1, **properties}
    result = ops.create_node(NodeType.TARGET, properties)
    assert result is not None
    assert result["name"] == "Test Target"

def test_relationship_creation(mock_neo4j_client):
    ops = GraphOperations()
    mock_neo4j_client.create_relationship.return_value = {"id": 1, "type": RelationshipType.RELATED_TO}
    result = ops.create_relationship(1, 2, RelationshipType.RELATED_TO, {"weight": 1.0})
    assert result is not None
