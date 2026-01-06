# ReconVault Quick Start Guide

Get up and running with ReconVault in minutes.

## Prerequisites

Before you begin, ensure you have:
- **Docker** (v20.10 or higher) and **Docker Compose** (v2.0 or higher)
- **Git** for cloning the repository
- At least **4GB RAM** and **10GB disk space**
- **Optional**: Python 3.11+ and Node.js 18+ for local development

## Installation

### Option 1: Docker (Recommended)

1. **Clone the repository**
```bash
git clone https://github.com/reconvault/reconvault.git
cd reconvault
```

2. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your settings (API keys, database passwords, etc.)
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Verify services are running**
```bash
docker-compose ps
```

All services should show status "Up". The platform will be available at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Option 2: Local Development

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Basic Usage

### 1. Access the Platform

Open your browser and navigate to **http://localhost:5173**

### 2. Create Your First Target

Using the left sidebar search form:
- Enter a target (domain, IP, email, username)
- Select collectors to use
- Click "Start Collection"

### 3. View Intelligence Graph

The main canvas displays your intelligence graph:
- **Nodes** represent entities (domains, IPs, people, etc.)
- **Links** show relationships between entities
- **Colors** indicate entity types
- Use mouse wheel to zoom, drag to pan

### 4. Inspect Entities

Click any node to view:
- Entity details in the right sidebar
- Risk score and indicators
- Collected intelligence data
- Related entities

### 5. Monitor Collections

Check the bottom stats panel for:
- Active collection tasks
- Graph statistics (nodes, edges)
- System health
- Real-time updates

## API Usage

### Health Check
```bash
curl http://localhost:8000/health
```

### Create a Target
```bash
curl -X POST http://localhost:8000/api/v1/targets \
  -H "Content-Type: application/json" \
  -d '{
    "value": "example.com",
    "target_type": "domain",
    "priority": "high"
  }'
```

### Get Graph Data
```bash
curl http://localhost:8000/api/v1/graph
```

### Start Collection
```bash
curl -X POST http://localhost:8000/api/v1/collection/start \
  -H "Content-Type: application/json" \
  -d '{
    "target_id": "123",
    "collectors": ["web", "domain", "social"]
  }'
```

## Configuration

### Environment Variables

Key variables in `.env`:

```bash
# Backend
BACKEND_PORT=8000
DEBUG=true

# Database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=reconvault
POSTGRES_USER=reconvault
POSTGRES_PASSWORD=your_password

# Neo4j
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# CORS
CORS_ORIGINS=["http://localhost:5173"]

# API Keys (optional, for specific collectors)
SHODAN_API_KEY=your_key
VIRUSTOTAL_API_KEY=your_key
```

### Collector Configuration

Configure collectors in the UI or via API. Each collector has specific options:

- **Web Collector**: Scrapes websites, follows links
- **Domain Collector**: DNS records, WHOIS, subdomain enumeration
- **Social Collector**: Social media profiles (requires API keys)
- **Email Collector**: Email validation, breach checks
- **IP Collector**: Geolocation, port scanning, ASN lookup

## Troubleshooting

### Services Not Starting

**Check logs**:
```bash
docker-compose logs backend
docker-compose logs frontend
```

**Common fixes**:
- Ensure ports 5173, 8000, 5432, 7687, 6379 are available
- Check Docker has sufficient resources
- Verify `.env` file exists and is configured

### Frontend Shows 404

**Verify Vite is running**:
```bash
docker-compose logs frontend
# Should show "ready in X ms"
```

**Check index.html exists**:
```bash
ls frontend/index.html
```

### Database Connection Errors

**Check PostgreSQL is running**:
```bash
docker-compose ps postgres
```

**Test connection**:
```bash
docker-compose exec postgres psql -U reconvault -d reconvault
```

### Neo4j Connection Issues

**Verify Neo4j is accessible**:
```bash
curl http://localhost:7474
```

**Check credentials in .env match Neo4j container**

## Next Steps

- Review the [Architecture Guide](ARCHITECTURE.md) to understand the system
- Check the [API Reference](API.md) for all available endpoints
- Read [Development Guide](../DEVELOPMENT.md) for contributing
- See [Troubleshooting](TROUBLESHOOTING.md) for more solutions

## Need Help?

- Check [Troubleshooting Guide](TROUBLESHOOTING.md)
- Review logs: `docker-compose logs [service]`
- Open an issue on GitHub
- Check API docs at http://localhost:8000/docs

---

**Next**: [Architecture Overview](ARCHITECTURE.md)
