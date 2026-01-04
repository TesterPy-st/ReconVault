# System Architecture

## Overview

ReconVault is a microservices-based cyber intelligence platform with a modular architecture designed for scalability, reliability, and extensibility. The system uses a service-oriented architecture with clear separation of concerns.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                              │
│                    React 18 + Vite                            │
│                  Tailwind CSS + D3.js                         │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/WebSocket
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                       Nginx Reverse Proxy                    │
│                         (Port 80/443)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬────────────┐
        ▼            ▼            ▼            ▼
┌──────────────┐ ┌──────────┐ ┌────────┐ ┌──────────┐
│   Backend    │ │  Neo4j   │ │ PostgreSQL │ │  Redis   │
│  FastAPI     │ │  Graph   │ │  Relational│ │   Cache  │
│   Port 8000  │ │  Port    │ │   Port    │ │  Port    │
│              │ │  7474    │ │   5432    │ │  6379    │
└──────┬───────┘ └──────────┘ └────────┘ └──────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Celery Workers                            │
│              Asynchronous Task Processing                      │
│         Collection, Analysis, Risk Scoring                    │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Frontend Layer

**Technology:** React 18, Vite, Tailwind CSS, D3.js

**Responsibilities:**
- User interface and interaction
- Graph visualization and navigation
- Real-time data display via WebSockets
- Form submissions and user inputs

**Key Components:**
- `GraphCanvas` - Interactive 3D force-directed graph
- `LeftSidebar` - Target management and collection controls
- `RightSidebar` - Entity inspector and relationship viewer
- `ComplianceDashboard` - Ethics and compliance monitoring
- `ExportPanel` - Data export and reporting

### 2. Backend API Layer

**Technology:** FastAPI (Python 3.11), SQLAlchemy, Pydantic

**Responsibilities:**
- RESTful API endpoints
- Request validation and authentication
- Business logic orchestration
- WebSocket server for real-time updates

**Key Services:**
- `target_service` - Target CRUD operations
- `collection_pipeline_service` - Collection orchestration
- `graph_service` - Graph queries and updates
- `risk_analysis_service` - Risk scoring and analysis
- `websocket_service` - Real-time message broadcasting

### 3. Data Storage Layer

**PostgreSQL (Relational Data)**
- Target metadata
- Entity records
- User accounts and permissions
- Audit logs
- Collection history

**Neo4j (Graph Data)**
- Entity nodes and relationships
- Intelligence graph
- Pattern matching queries
- Graph analytics

**Redis (Cache & Queue)**
- Celery task queue
- API response caching
- Session storage
- Rate limiting

### 4. Intelligence Collection Layer

**OSINT Collectors:**
- **Web Collector** - Website scraping and metadata extraction
- **Social Collector** - Social media profile aggregation
- **Domain Collector** - WHOIS, DNS, SSL certificate data
- **Email Collector** - Validation, breach detection, correlation
- **IP Collector** - Geolocation, reputation, ASN information
- **Darkweb Collector** - Tor hidden services, paste sites
- **Media Collector** - EXIF data extraction, image analysis
- **Geo Collector** - Geospatial intelligence, location enrichment

**Compliance:**
- Robots.txt enforcement
- Rate limiting per domain
- PII detection and flagging
- Audit logging

### 5. Analysis Layer

**AI/ML Engine:**
- **Anomaly Detection** - Isolation Forest, One-Class SVM, Autoencoder
- **Risk Scoring** - XGBoost, LightGBM, Random Forest
- **Pattern Recognition** - Entity correlation, relationship analysis

**Risk Engine:**
- Exposure modeling
- Vulnerability assessment
- Threat intelligence correlation
- Risk aggregation and prioritization

## Data Flow

### Collection Workflow

```
User Request
    ↓
Frontend (Target Form)
    ↓
API POST /api/v1/targets
    ↓
Target Service → PostgreSQL
    ↓
User Starts Collection
    ↓
API POST /api/v1/collection/start
    ↓
Collection Pipeline Service
    ↓
Celery Task Queue (Redis)
    ↓
Celery Workers Execute Collectors
    ↓
Collectors Fetch Data (Web, API, etc.)
    ↓
Normalizer (Data Standardization)
    ↓
Graph Builder (Neo4j)
    ↓
Entity Store (PostgreSQL)
    ↓
WebSocket Update → Frontend
    ↓
Real-time Graph Update
```

### Analysis Workflow

```
New Entities Detected
    ↓
Risk Analysis Service
    ↓
Feature Extraction
    ↓
ML Model Inference (XGBoost/Isolation Forest)
    ↓
Risk Score Calculation
    ↓
Anomaly Detection
    ↓
Store Results (PostgreSQL + Neo4j)
    ↓
WebSocket Alert → Frontend
    ↓
Update Dashboard
```

## Technology Stack

### Backend
- **Framework:** FastAPI 0.104+
- **ORM:** SQLAlchemy 2.0+
- **Async:** asyncio + uvloop
- **Task Queue:** Celery + Redis
- **Databases:** PostgreSQL 15+, Neo4j 5+
- **ML/AI:** scikit-learn, XGBoost, LightGBM
- **Validation:** Pydantic v2

### Frontend
- **Framework:** React 18
- **Build:** Vite 5+
- **Styling:** Tailwind CSS 3+
- **Graph:** D3.js, react-force-graph
- **Animation:** Framer Motion
- **State:** React Context, Custom Hooks

### Infrastructure
- **Containerization:** Docker, Docker Compose
- **Proxy:** Nginx
- **CI/CD:** GitHub Actions
- **Monitoring:** Structured logging, health checks

## Security Architecture

### Authentication & Authorization
- JWT-based authentication (in development)
- Role-based access control (RBAC)
- API key management
- Session management via Redis

### Data Security
- Encryption at rest (PostgreSQL, Neo4j)
- TLS/SSL for all connections
- Environment-based secrets management
- Audit logging for all operations

### API Security
- CORS configuration
- Rate limiting per endpoint
- Input validation with Pydantic
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection (React default)

## Scalability Considerations

### Horizontal Scaling
- Stateless API services (multiple instances)
- Celery worker pool scaling
- Redis cluster for caching
- PostgreSQL read replicas
- Neo4j causal clustering

### Performance Optimization
- Redis caching for frequent queries
- Database query optimization
- Async I/O for collectors
- Graph query optimization
- Frontend code splitting and lazy loading

## Monitoring & Observability

### Health Checks
- `/health/live` - Service running
- `/health/ready` - Dependencies ready
- `/health/startup` - Initialization complete

### Logging
- Structured JSON logging
- Request/response logging
- Error tracking
- Performance metrics

### Metrics
- API response times
- Collection success rates
- Error rates by service
- Database query performance
- Memory and CPU usage
