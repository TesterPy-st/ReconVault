# API Reference

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently in development. All endpoints are accessible without authentication.

## Response Format

All responses follow this format:

**Success Response:**
```json
{
  "data": { ... },
  "message": "Success",
  "status": "success"
}
```

**Error Response:**
```json
{
  "error": "Error message",
  "detail": "Detailed error information",
  "status": "error"
}
```

## Endpoints

### Health Check

#### Check Health
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0-beta",
  "timestamp": "2024-01-03T10:00:00Z"
}
```

---

### Targets

#### List Targets
```
GET /targets
```

**Query Parameters:**
- `limit` (optional): Maximum number of targets (default: 100)
- `offset` (optional): Number of targets to skip (default: 0)
- `type` (optional): Filter by target type

**Example:**
```bash
curl http://localhost:8000/api/v1/targets?limit=10&type=domain
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "example.com",
      "type": "domain",
      "priority": "medium",
      "status": "active",
      "created_at": "2024-01-03T10:00:00Z",
      "updated_at": "2024-01-03T10:00:00Z"
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

#### Get Target
```
GET /targets/{id}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/targets/1
```

#### Create Target
```
POST /targets
```

**Request Body:**
```json
{
  "name": "example.com",
  "type": "domain",
  "priority": "medium",
  "description": "Example target"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/targets \
  -H "Content-Type: application/json" \
  -d '{
    "name": "example.com",
    "type": "domain",
    "priority": "medium"
  }'
```

#### Update Target
```
PUT /targets/{id}
```

**Request Body:**
```json
{
  "name": "new-example.com",
  "priority": "high"
}
```

#### Delete Target
```
DELETE /targets/{id}
```

---

### Entities

#### List Entities
```
GET /entities
```

**Query Parameters:**
- `limit` (optional): Maximum number of entities (default: 100)
- `offset` (optional): Number of entities to skip (default: 0)
- `type` (optional): Filter by entity type
- `target_id` (optional): Filter by target ID

**Example:**
```bash
curl http://localhost:8000/api/v1/entities?limit=20&type=person
```

#### Get Entity
```
GET /entities/{id}
```

#### Search Entities
```
POST /entities/search
```

**Request Body:**
```json
{
  "query": "john doe",
  "types": ["person", "email"],
  "limit": 50
}
```

---

### Graph

#### Get Full Graph
```
GET /graph
```

**Response:**
```json
{
  "nodes": [
    {
      "id": "entity-1",
      "label": "John Doe",
      "type": "person",
      "properties": { ... }
    }
  ],
  "edges": [
    {
      "id": "rel-1",
      "source": "entity-1",
      "target": "entity-2",
      "type": "connected_to",
      "properties": { ... }
    }
  ]
}
```

#### Get Nodes
```
GET /graph/nodes
```

**Query Parameters:**
- `limit` (optional): Maximum number of nodes
- `type` (optional): Filter by node type

#### Get Edges
```
GET /graph/edges
```

#### Analyze Graph
```
POST /graph/analyze
```

**Request Body:**
```json
{
  "analysis_type": "shortest_path",
  "source_node": "entity-1",
  "target_node": "entity-2"
}
```

---

### Collection

#### Start Collection
```
POST /collection/start
```

**Request Body:**
```json
{
  "target_id": 1,
  "collectors": ["web", "dns", "social"],
  "config": {
    "depth": 2,
    "timeout": 300
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/collection/start \
  -H "Content-Type: application/json" \
  -d '{
    "target_id": 1,
    "collectors": ["web", "dns"]
  }'
```

**Response:**
```json
{
  "collection_id": "col-123",
  "status": "started",
  "message": "Collection started successfully"
}
```

#### Get Collection Status
```
GET /collection/{id}/status
```

**Response:**
```json
{
  "collection_id": "col-123",
  "status": "in_progress",
  "progress": 65,
  "entities_collected": 150,
  "active_collectors": ["web"],
  "completed_collectors": ["dns"]
}
```

#### Get Recent Collections
```
GET /collection/recent
```

#### Cancel Collection
```
POST /collection/{id}/cancel
```

---

### Risk

#### Get Risk Scores
```
GET /risk/scores
```

**Query Parameters:**
- `target_id` (optional): Filter by target
- `min_score` (optional): Minimum risk score

#### Get Entity Risk
```
GET /risk/entities/{id}
```

**Response:**
```json
{
  "entity_id": "entity-1",
  "risk_score": 75,
  "risk_level": "high",
  "factors": [
    {
      "name": "exposed_credentials",
      "weight": 0.3,
      "value": 90
    },
    {
      "name": "suspicious_connections",
      "weight": 0.25,
      "value": 70
    }
  ]
}
```

#### Analyze Risk
```
POST /risk/analyze
```

**Request Body:**
```json
{
  "entity_ids": ["entity-1", "entity-2"],
  "analysis_type": "comprehensive"
}
```

---

### Anomalies

#### List Anomalies
```
GET /anomalies
```

**Query Parameters:**
- `limit` (optional): Maximum number of anomalies
- `type` (optional): Filter by anomaly type
- `severity` (optional): Filter by severity level

**Response:**
```json
{
  "data": [
    {
      "id": "anom-1",
      "type": "behavioral",
      "severity": "high",
      "entity_id": "entity-1",
      "description": "Unusual activity pattern detected",
      "detected_at": "2024-01-03T10:00:00Z"
    }
  ]
}
```

#### Get Anomaly Details
```
GET /anomalies/{id}
```

---

### Compliance

#### Get Compliance Status
```
GET /compliance/status
```

**Response:**
```json
{
  "status": "compliant",
  "robots_txt_enforced": true,
  "rate_limits_active": true,
  "requests_this_hour": 150,
  "requests_limit": 1000,
  "blocked_requests": 5,
  "last_check": "2024-01-03T10:00:00Z"
}
```

#### Get Compliance Violations
```
GET /compliance/violations
```

#### Get Audit Logs
```
GET /compliance/logs
```

**Query Parameters:**
- `limit` (optional): Maximum number of logs
- `action` (optional): Filter by action type
- `from_date` (optional): Filter by date

---

### Export

#### Export Data
```
POST /export
```

**Request Body:**
```json
{
  "format": "json",
  "target_id": 1,
  "include_entities": true,
  "include_relationships": true
}
```

**Supported Formats:**
- `json` - Structured JSON data
- `csv` - Comma-separated values
- `graphml` - GraphML format for graph tools
- `gexf` - GEXF format for Gephi

---

## WebSocket Events

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('Connected to WebSocket');
};
```

### Subscribe to Updates
```javascript
ws.send(JSON.stringify({
  action: 'subscribe',
  channels: ['collection_updates', 'graph_updates']
}));
```

### Message Format
```json
{
  "type": "collection_update",
  "data": {
    "collection_id": "col-123",
    "progress": 75,
    "entities_collected": 150
  },
  "timestamp": "2024-01-03T10:00:00Z"
}
```

### Event Types
- `collection_update` - Collection progress updates
- `graph_update` - New nodes/edges added to graph
- `risk_update` - Risk score changes
- `anomaly_detected` - New anomaly detected
- `compliance_alert` - Compliance issues

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

---

## Rate Limiting

- **Default Limit:** 1000 requests per hour
- **Burst Limit:** 100 requests per minute
- Headers returned:
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset time (Unix timestamp)

---

## Pagination

All list endpoints support pagination:

```bash
GET /targets?limit=50&offset=0
```

**Response Headers:**
- `X-Total-Count`: Total number of items
- `X-Limit`: Items per page
- `X-Offset`: Current offset

---

## Interactive API Documentation

Access the interactive Swagger UI:
```
http://localhost:8000/docs
```

Or ReDoc:
```
http://localhost:8000/redoc
```
