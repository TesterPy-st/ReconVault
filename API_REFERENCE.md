# ReconVault API Reference

## Authentication
ReconVault uses JWT Bearer tokens for authentication.
Include the token in the `Authorization` header: `Authorization: Bearer <your_token>`

---

## Targets
Endpoints for managing reconnaissance targets.

### `GET /api/v1/targets`
Get all targets.

### `POST /api/v1/targets`
Create a new target.

### `GET /api/v1/targets/{id}`
Get target details.

### `PUT /api/v1/targets/{id}`
Update target information.

### `DELETE /api/v1/targets/{id}`
Delete a target and all associated data.

---

## Entities
Endpoints for managing discovered entities.

### `GET /api/v1/entities`
List all entities. Supports filtering by target, type, and risk level.

### `GET /api/v1/entities/{id}`
Get entity details.

### `POST /api/v1/entities`
Create a new entity manually.

### `PUT /api/v1/entities/{id}`
Update entity data.

### `DELETE /api/v1/entities/{id}`
Delete an entity.

---

## Intelligence Graph
Endpoints for graph-based visualization and analysis.

### `GET /api/v1/graph`
Get complete graph data (nodes and relationships) for a target.

### `GET /api/v1/graph/stats`
Get graph statistics (node count, relationship count, density).

### `POST /api/v1/graph/export`
Export graph data in JSON or CSV format.

---

## Collection Pipeline
Endpoints for triggering and monitoring OSINT collection.

### `POST /api/v1/collection/start`
Start a collection task for a target.

### `GET /api/v1/collection/tasks/{id}`
Get status of a collection task.

### `GET /api/v1/collection/tasks/{id}/results`
Get results of a completed collection task.

### `POST /api/v1/collection/tasks/{id}/cancel`
Cancel a running task.

---

## Risk Assessment
Endpoints for risk scoring and analysis.

### `POST /api/v1/risk/analyze`
Calculate risk for a specific entity.

### `POST /api/v1/risk/analyze-batch`
Calculate risk for a list of entities.

### `GET /api/v1/risk/report/{target_id}`
Generate a comprehensive risk report for a target.

### `GET /api/v1/risk/patterns`
Get the library of detected risk patterns.

---

## AI Anomaly Detection
Endpoints for ML-powered anomaly detection.

### `POST /api/v1/anomalies/detect-anomalies`
Analyze an entity for anomalies.

### `POST /api/v1/anomalies/detect-batch`
Batch anomaly detection for multiple entities.

### `GET /api/v1/anomalies/anomalies`
List all detected anomalies.

### `GET /api/v1/anomalies/anomaly/{id}`
Get details and explanation for a specific anomaly.

---

## Ethics & Compliance
Endpoints for compliance monitoring.

### `GET /api/v1/compliance/check`
Verify compliance of a collection target against policies.

### `GET /api/v1/compliance/alerts`
Get recent compliance violations or alerts.

---

## System Health
Endpoints for monitoring system status.

### `GET /health`
Basic health check.

### `GET /health/detailed`
Detailed status of database, Neo4j, Redis, and workers.

---

## WebSocket Events
Real-time updates via WebSockets at `/ws/graph`.

- `task_update`: Progress updates for collection tasks.
- `graph_update`: Notification of new nodes or relationships added to the graph.
- `anomaly_alert`: Real-time notification of detected high-risk anomalies.
- `compliance_alert`: Notification of compliance policy violations.
