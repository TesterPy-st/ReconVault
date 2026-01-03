import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.services.collection_pipeline_service import CollectionPipelineService, TaskStatus
from app.collectors.base_collector import CollectionResult, DataType

@pytest.fixture
async def pipeline_service():
    service = CollectionPipelineService()
    service.entity_service = MagicMock()
    service.graph_service = MagicMock()
    return service

@pytest.mark.asyncio
async def test_full_collection_workflow(pipeline_service):
    target = "example.com"
    with patch.object(pipeline_service.compliance_checker, 'get_ethical_verdict', new_callable=AsyncMock) as mock_verdict:
        mock_verdict.return_value = {"allowed": True}
        with patch.object(pipeline_service, 'route_to_collectors', new_callable=AsyncMock) as mock_route:
            mock_collector = MagicMock()
            mock_collector.name = "WebCollector"
            mock_collector.execute = AsyncMock(return_value=CollectionResult(
                success=True,
                collector_name="WebCollector",
                data=[{"entity_type": DataType.DOMAIN.value, "value": "example.com"}]
            ))
            mock_collector.__aenter__.return_value = mock_collector
            mock_collector.__aexit__.return_value = None
            mock_route.return_value = [mock_collector]
            
            # Need to mock create_entities_from_results and assess_risk to avoid deep integration
            with patch.object(pipeline_service, 'create_entities_from_results', new_callable=AsyncMock) as mock_create:
                mock_create.return_value = {"entities": [], "relationships": []}
                with patch.object(pipeline_service, 'assess_risk', new_callable=AsyncMock):
                    task = await pipeline_service.start_collection_task(target)
                    assert task["status"] == TaskStatus.COMPLETED.value
