# ReconVault Architecture

## System Overview

ReconVault is a cyber reconnaissance intelligence system designed to collect, analyze, and correlate Open Source Intelligence (OSINT) data from various public sources. The system uses a graph-based approach to visualize relationships between entities and identify patterns across multiple data streams.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Nginx (Port 80/443)                      │
│                    Reverse Proxy & Load Balancer                 │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
┌─────────────────────────────────┐  ┌─────────────────────────────────┐
│      Frontend (React/Vite)      │  │      Backend (FastAPI)          │
│         Port: 5173              │  │         Port: 8000              │
│  ┌──────────────────────────┐   │  │  ┌──────────────────────────┐  │
│  │  Graph Visualization     │   │  │  │  API Endpoints          │  │
│  │  (react-force-graph)     │   │  │  │  Authentication         │  │
│  │  Dashboard UI           │   │  │  │  Data Normalization     │  │
│  │  Reports & Analytics     │   │  │  │  Intelligence Graph     │  │
│  └──────────────────────────┘   │  │  └──────────────────────────┘  │
└─────────────────────────────────┘  └─────────────────┬───────────────┘
                                                    │
        ┌───────────────────────────────────────────┼─────────────────────┐
        │                                           │                     │
        ▼                                           ▼                     ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐
│   PostgreSQL     │  │     Neo4j        │  │     Redis        │  │  External    │
│   (Port: 5432)   │  │   (Ports:        │  │   (Port: 6379)   │  │  OSINT APIs  │
│                  │  │    7474/7687)    │  │                  │  │              │
│  - User Data     │  │                  │  │  - Caching       │  │  - Social    │
│  - Reports       │  │  - Graph Nodes   │  │  - Task Queue    │  │  - Public    │
│  - Metadata      │  │  - Relationships │  │  - Sessions      │  │  - Commercial│
└──────────────────┘  └──────────────────┘  └──────────────────┘  └──────────────┘
```

## Service Interactions

### Frontend → Backend
- **Protocol**: HTTP/HTTPS, WebSocket
- **Authentication**: JWT tokens
- **Data Format**: JSON
- **Communication Pattern**: REST API with real-time updates via WebSockets

### Backend → Databases
- **PostgreSQL**: Structured data, user accounts, reports, audit logs
  - Connection Pool: SQLAlchemy async
  - ORM: Pydantic models
- **Neo4j**: Graph data, entity relationships, network analysis
  - Driver: neo4j Python driver
  - Query Language: Cypher
- **Redis**: Caching, session management, task queues
  - Client: redis-py
  - Use Cases: Rate limiting, temporary data, pub/sub

### Backend → External Sources
- **Protocol**: HTTPS with rate limiting
- **Data Collection**: Modular collectors
- **Compliance**: robots.txt enforcement, passive OSINT only

## Core Modules

### 1. API Layer (`app/api/`)
- RESTful endpoints
- Request validation (Pydantic)
- Response formatting
- Authentication & authorization

### 2. Data Collectors (`app/collectors/`)
- Modular collector architecture
- Source-specific implementations
- Rate limiting per source
- Error handling and retry logic

### 3. Normalization Engine (`app/normalization/`)
- Data standardization
- Entity extraction
- Deduplication
- Schema mapping

### 4. Intelligence Graph (`app/intelligence_graph/`)
- Graph construction
- Relationship mapping
- Pattern detection
- Path finding algorithms

### 5. Media OSINT (`app/media_osint/`)
- Social media monitoring
- Public forum scraping
- Content analysis
- Account correlation

### 6. AI Engine (`app/ai_engine/`)
- Machine learning models
- Pattern recognition
- Anomaly detection
- Predictive analytics

### 7. Risk Engine (`app/risk_engine/`)
- Threat scoring
- Risk assessment
- Priority ranking
- Alert generation

### 8. Reverse OSINT (`app/reverse_osint/`)
- Cross-referencing
- Identity correlation
- Follower analysis
- Network discovery

### 9. Automation (`app/automation/`)
- Scheduled tasks
- Workflow orchestration
- Notification systems
- Report generation

### 10. Ethics Module (`app/ethics/`)
- robots.txt compliance
- Rate limiting enforcement
- Data retention policies
- Audit logging

## Data Flow

### 1. Data Collection
```
External Sources → Collectors → Raw Data → Validation Queue
```

### 2. Data Processing
```
Raw Data → Normalization → Entity Extraction → Graph Construction
```

### 3. Intelligence Generation
```
Graph Data → AI Analysis → Risk Scoring → Pattern Detection
```

### 4. User Interface
```
Frontend Request → API → Database/Graph → Processing → Response
```

## Technology Choices Rationale

### Backend: FastAPI
- **Performance**: Async support, type hints, automatic validation
- **Developer Experience**: Auto-generated docs, clear error messages
- **Ecosystem**: Seamless integration with modern Python libraries
- **Scalability**: Can handle high concurrency with uvicorn workers

### Frontend: React + Vite
- **Development Speed**: Fast HMR, clear component structure
- **Ecosystem**: Rich library ecosystem (force-graph, D3, Framer Motion)
- **Performance**: Virtual DOM, code splitting, lazy loading
- **Maintainability**: Component-based architecture, hooks system

### Graph Database: Neo4j
- **Native Graph Storage**: Optimized for relationships and traversals
- **Query Language**: Cypher for intuitive graph queries
- **Scalability**: Handles complex relationship queries efficiently
- **Visualization**: Excellent support with react-force-graph

### Relational Database: PostgreSQL
- **ACID Compliance**: Reliable transaction handling
- **JSON Support**: Hybrid relational-document approach
- **Maturity**: Battle-tested, extensive tooling
- **Performance**: Excellent for structured queries

### Caching Layer: Redis
- **Speed**: In-memory storage for sub-millisecond access
- **Data Structures**: Rich set of data types (strings, lists, sets)
- **Pub/Sub**: Built-in messaging for real-time updates
- **Scalability**: Master-slave replication, clustering

### Reverse Proxy: Nginx
- **Performance**: High concurrency handling, low memory footprint
- **Load Balancing**: Distributes traffic across backend instances
- **Security**: SSL termination, request filtering, rate limiting
- **Flexibility**: Extensive configuration options

## Security Considerations

### Network Security
- All inter-service communication within Docker network
- Nginx as only exposed entry point
- HTTPS/TLS for production deployment

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- API key management for integrations

### Data Protection
- Encryption at rest (database level)
- Encryption in transit (TLS)
- Secure credential management

### Rate Limiting
- Per-user request limits
- API endpoint throttling
- External source rate limiting

## Scalability Strategy

### Horizontal Scaling
- Stateless backend services
- Load balancer support
- Database read replicas

### Vertical Scaling
- Resource monitoring
- Container resource limits
- Performance optimization

### Caching Strategy
- Multi-level caching (Redis, browser)
- Cache invalidation policies
- CDN for static assets

## Monitoring & Observability

### Logging
- Structured logging (JSON format)
- Centralized log aggregation
- Log levels by severity

### Metrics
- Request/response times
- Error rates
- Resource utilization
- Database query performance

### Health Checks
- Service availability monitoring
- Dependency health checks
- Automated recovery

## Future Enhancements

### Phase 2
- Advanced AI/ML models
- Real-time streaming data
- Multi-tenant support
- Advanced visualization modes

### Phase 3
- Mobile applications
- API marketplace
- Custom integrations
- Enterprise SSO support
