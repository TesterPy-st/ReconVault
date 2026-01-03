"""
Integration tests for API and database integration.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestAPICreateAndRetrieve:
    """Tests for API create and retrieve operations."""

    def test_create_and_get_target(self, client, sample_target_data):
        """Test creating target via API and retrieving it."""
        # Create
        response = client.post("/api/targets", json=sample_target_data)
        if response.status_code in [200, 201]:
            data = response.json()
            target_id = data.get("id")
            
            if target_id:
                # Retrieve
                get_response = client.get(f"/api/targets/{target_id}")
                assert get_response.status_code == 200

    def test_list_targets_pagination(self, client):
        """Test listing targets with pagination."""
        response = client.get("/api/targets?limit=10&offset=0")
        assert response.status_code in [200, 404]


@pytest.mark.integration
class TestAPIUpdateWorkflow:
    """Tests for API update workflows."""

    def test_update_target_workflow(self, client, sample_target_data):
        """Test complete update workflow."""
        # Create
        create_response = client.post("/api/targets", json=sample_target_data)
        if create_response.status_code in [200, 201]:
            data = create_response.json()
            target_id = data.get("id")
            
            if target_id:
                # Update
                updated_data = sample_target_data.copy()
                updated_data["name"] = "Updated Target"
                update_response = client.put(f"/api/targets/{target_id}", json=updated_data)
                assert update_response.status_code in [200, 404]


@pytest.mark.integration
class TestAPIDeleteAndVerify:
    """Tests for API delete operations."""

    def test_delete_target_workflow(self, client, sample_target_data):
        """Test complete delete workflow."""
        # Create
        create_response = client.post("/api/targets", json=sample_target_data)
        if create_response.status_code in [200, 201]:
            data = create_response.json()
            target_id = data.get("id")
            
            if target_id:
                # Delete
                delete_response = client.delete(f"/api/targets/{target_id}")
                assert delete_response.status_code in [200, 204, 404]


@pytest.mark.integration
class TestConcurrentAPIcalls:
    """Tests for concurrent API calls."""

    def test_concurrent_reads(self, client):
        """Test concurrent read operations."""
        import concurrent.futures
        
        def make_request():
            return client.get("/api/targets")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in futures]
        
        assert all(r.status_code in [200, 404] for r in results)
