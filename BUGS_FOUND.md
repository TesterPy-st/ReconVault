# Bugs Found

## Bug #1
- **Location**: `backend/app/collectors/email_collector.py:348`
- **Severity**: MEDIUM
- **Description**: The `_get_email_provider_info` method iterates over an empty local list `entities` instead of finding and updating the existing EMAIL entity or returning the provider info to be merged.
- **Reproduction**: Run `EmailCollector.collect()` for an email address.
- **Impact**: Email provider information is not correctly added to the metadata of the EMAIL entity.
- **Status**: OPEN

## Bug #2
- **Location**: `backend/app/ethics/compliance.py` (referenced in `BUGS.md`)
- **Severity**: HIGH
- **Description**: Rate limiter accumulates entries indefinitely, causing memory growth over time.
- **Reproduction**: Make 1000+ requests from different hosts and monitor memory usage.
- **Impact**: Potential service crash due to Out-Of-Memory (OOM) error.
- **Status**: IN_PROGRESS

## Bug #3
- **Location**: `backend/app/intelligence_graph/neo4j_client.py` (referenced in `BUGS.md`)
- **Severity**: MEDIUM
- **Description**: Neo4j connections are not properly released under high load, leading to pool exhaustion.
- **Reproduction**: Run load test with 100+ concurrent users performing graph operations.
- **Impact**: System becomes unresponsive to graph queries.
- **Status**: OPEN

## Bug #4
- **Location**: `frontend/src/components/GraphCanvas.jsx` (referenced in `BUGS.md`)
- **Severity**: HIGH
- **Description**: Graph rendering performance degrades significantly with 1000+ nodes.
- **Reproduction**: Load a target with 1000+ entities and attempt to zoom/pan.
- **Impact**: Poor user experience, UI freezes.
- **Status**: IN_PROGRESS

## Bug #5
- **Location**: `frontend/src/services/websocketService.js` (referenced in `BUGS.md`)
- **Severity**: MEDIUM
- **Description**: WebSocket fails to automatically reconnect after connection loss.
- **Reproduction**: Establishing a connection, restart the backend, and observe that it doesn't reconnect.
- **Impact**: Real-time updates stop working until a page refresh.
- **Status**: OPEN

## Bug #6
- **Location**: `backend/app/services/collection_pipeline_service.py` (referenced in `BUGS.md`)
- **Severity**: HIGH
- **Description**: Race condition when concurrent collections are run on the same target, leading to duplicate entities.
- **Reproduction**: Start two collections for the same target simultaneously.
- **Impact**: Data duplication and inconsistency in the intelligence graph.
- **Status**: IN_PROGRESS

## Bug #7
- **Location**: `docker-compose.yml`
- **Severity**: MEDIUM
- **Description**: Insecure default credentials and configuration (Redis has no password, PostgreSQL and Neo4j use default/weak passwords).
- **Reproduction**: Inspect `docker-compose.yml`.
- **Impact**: Security vulnerability in production if not changed.
- **Status**: OPEN
