# Quick Start Guide

## Prerequisites

Before installing ReconVault, ensure you have:

- **Docker** 20.10+ and **Docker Compose** 2.0+
- **8GB RAM** minimum (16GB recommended)
- **20GB** available disk space
- **Python 3.11+** (for local development only)
- **Node.js 18+** (for frontend development only)

## Installation

### Option 1: Docker Installation (Recommended)

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd reconvault
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   # See API Keys Reference below
   ```

3. **Start All Services**
   ```bash
   docker compose up -d --build
   ```

4. **Verify Installation**
   ```bash
   # Check all services are running
   docker compose ps

   # Test backend health
   curl http://localhost:8000/health
   ```

### Option 2: Local Development Setup

**Backend:**
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-test.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

**Databases (via Docker):**
```bash
docker compose up -d postgres neo4j redis
```

## Accessing the Application

Once started, access these URLs:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend UI** | http://localhost:5173 | Main application interface |
| **API Docs** | http://localhost:8000/docs | Swagger UI documentation |
| **API Alt Docs** | http://localhost:8000/redoc | ReDoc documentation |
| **Health Check** | http://localhost:8000/health | Backend health status |
| **Neo4j Browser** | http://localhost:7474 | Graph database browser |

## First Steps

### 1. Create a Target

**Via Frontend:**
- Navigate to the "Targets" section
- Click "Add New Target"
- Enter target details (e.g., domain, IP, email)
- Click "Save"

**Via API:**
```bash
curl -X POST http://localhost:8000/api/v1/targets \
  -H "Content-Type: application/json" \
  -d '{
    "name": "example.com",
    "type": "domain",
    "priority": "medium"
  }'
```

### 2. Start Intelligence Collection

**Via Frontend:**
- Select a target from the list
- Choose collectors (Web, Social, DNS, etc.)
- Click "Start Collection"
- Monitor progress in real-time

**Via API:**
```bash
curl -X POST http://localhost:8000/api/v1/collection/start \
  -H "Content-Type: application/json" \
  -d '{
    "target_id": 1,
    "collectors": ["web", "dns", "social"]
  }'
```

### 3. View Intelligence Graph

- Navigate to "Graph" section
- Explore discovered entities and relationships
- Use controls to zoom, pan, and filter
- Click nodes to view detailed information

### 4. Analyze Risk Scores

- Navigate to "Risk Analysis" section
- View entity risk scores
- Review anomaly detection results
- Explore risk factors and patterns

### 5. Export Data

**Via Frontend:**
- Click "Export" button
- Select format (JSON, CSV, GraphML)
- Choose what to export
- Download the file

**Via API:**
```bash
curl -X POST http://localhost:8000/api/v1/export \
  -H "Content-Type: application/json" \
  -d '{
    "format": "json",
    "target_id": 1
  }' \
  -o export.json
```

## API Keys Configuration

Some collectors require external API keys. Add these to your `.env` file:

```bash
# Email Verification
EMAILHUNTER_API_KEY=your_key_here
HUNTER_API_KEY=your_key_here

# Social Media (optional)
TWITTER_API_KEY=your_key_here
TWITTER_API_SECRET=your_key_here
LINKEDIN_API_KEY=your_key_here

# Geolocation
IPINFO_API_KEY=your_key_here
IPGEOLOCATION_API_KEY=your_key_here
```

**Note:** The system works without API keys, but functionality will be limited.

## Basic Usage

### Creating Targets

Supported target types:
- **Domain** - Websites and web properties
- **IP Address** - Network infrastructure
- **Email** - Email addresses and accounts
- **Username** - Social media usernames
- **Organization** - Companies and organizations

### Selecting Collectors

Available collectors:
- **Web** - Website scraping and analysis
- **Social** - Social media profile gathering
- **Domain** - WHOIS, DNS, SSL information
- **Email** - Email validation and breach detection
- **IP** - Geolocation and reputation
- **Darkweb** - Tor hidden services (requires Tor)
- **Media** - EXIF data extraction
- **Geo** - Geospatial intelligence

### Viewing Results

- **Graph View** - Visual representation of entities and relationships
- **List View** - Tabular data with filtering and sorting
- **Timeline** - Chronological view of discoveries
- **Dashboard** - Summary statistics and key metrics

## Stopping the System

```bash
# Stop all services
docker compose down

# Stop and remove volumes (deletes data)
docker compose down -v

# View logs
docker compose logs backend
docker compose logs frontend
```

## Troubleshooting

### Services Won't Start

```bash
# Check port conflicts
netstat -tuln | grep -E '8000|5173|7474|5432|6379'

# Check disk space
df -h

# View service logs
docker compose logs [service-name]
```

### Database Connection Issues

```bash
# Restart databases
docker compose restart postgres neo4j redis

# Check database is ready
docker compose exec postgres pg_isready
docker compose exec neo4j cypher-shell "RETURN 1"
```

### Frontend Build Errors

```bash
# Clear cache and rebuild
cd frontend
rm -rf node_modules/.vite
npm install
npm run dev
```

### Performance Issues

- Increase Docker memory allocation (recommended 8GB+)
- Reduce collection concurrency in `.env`
- Use fewer collectors for initial tests

## Next Steps

- Read the [Architecture Guide](ARCHITECTURE.md) for system overview
- Check the [API Reference](API.md) for endpoint documentation
- See [Development Guide](../DEVELOPMENT.md) for local development setup
- Visit [Troubleshooting](TROUBLESHOOTING.md) for common issues

## Getting Help

- [Documentation Index](INDEX.md) - All documentation
- [GitHub Issues](../../issues) - Report bugs
- [GitHub Discussions](../../discussions) - Ask questions
