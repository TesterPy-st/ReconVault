# ReconVault Usage Guide

## Table of Contents
1. [Development Environment Setup](#development-environment-setup)
2. [Running All Services](#running-all-services)
3. [API Endpoint Structure](#api-endpoint-structure)
4. [Common Troubleshooting](#common-troubleshooting)
5. [Development Workflow](#development-workflow)

---

## Development Environment Setup

### Prerequisites

Before starting, ensure you have the following installed:
- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Git**: For version control
- **Make**: Optional, for convenient commands

### Quick Start

1. **Clone the Repository**
```bash
git clone <repository-url>
cd ReconVault
```

2. **Configure Environment Variables**
```bash
cp .env.example .env
# Edit .env with your preferred configuration
```

3. **Start All Services**
```bash
docker-compose up -d
```

4. **Wait for Services to Initialize**
```bash
# Watch logs to see when services are ready
docker-compose logs -f
```

5. **Verify Services**
```bash
docker-compose ps
# All services should show "healthy" status
```

### Manual Setup (Without Docker)

If you prefer to run services individually:

#### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export $(cat ../../.env | xargs)

# Run backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set environment variables
export VITE_API_URL=http://localhost:8000

# Start development server
npm run dev
```

#### Database Setup

**PostgreSQL:**
```bash
# Using Docker
docker run -d \
  --name reconvault-postgres \
  -e POSTGRES_DB=reconvault \
  -e POSTGRES_USER=reconvault_user \
  -e POSTGRES_PASSWORD=changeme \
  -p 5432:5432 \
  postgres:15-alpine
```

**Neo4j:**
```bash
# Using Docker
docker run -d \
  --name reconvault-neo4j \
  -e NEO4J_AUTH=neo4j/neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  neo4j:5.12-community
```

**Redis:**
```bash
# Using Docker
docker run -d \
  --name reconvault-redis \
  -p 6379:6379 \
  redis:7-alpine
```

---

## Running All Services

### Docker Compose Commands

#### Start All Services
```bash
# Start all services in detached mode
docker-compose up -d

# Start with build
docker-compose up -d --build
```

#### Stop Services
```bash
# Stop all services
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove with volumes
docker-compose down -v
```

#### View Logs
```bash
# View all logs
docker-compose logs

# Follow logs (real-time)
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
docker-compose logs -f neo4j
docker-compose logs -f redis
```

#### Restart Services
```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
```

#### Service Status
```bash
# Check status of all services
docker-compose ps

# Check resource usage
docker stats
```

### Accessing Services

#### Backend API
- **Local**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/health

#### Frontend
- **Local**: http://localhost:5173
- **Via Nginx**: http://localhost

#### Databases

**PostgreSQL:**
- **Host**: localhost
- **Port**: 5432
- **Database**: reconvault
- **User**: reconvault_user
- **Password**: changeme

Connection string:
```
postgresql://reconvault_user:changeme@localhost:5432/reconvault
```

**Neo4j:**
- **Browser UI**: http://localhost:7474
- **Bolt Protocol**: bolt://localhost:7687
- **User**: neo4j
- **Password**: neo4j

Connection string:
```
bolt://neo4j:neo4j@localhost:7687
```

**Redis:**
- **Host**: localhost
- **Port**: 6379
- **Password**: redispass

---

## API Endpoint Structure

### Base URL
```
http://localhost:8000
```

### Endpoints Overview

#### Health & System
```
GET /health              - Health check
GET /                    - API information
GET /api/docs            - Interactive API documentation (Swagger)
GET /api/redoc           - Alternative API documentation (ReDoc)
```

#### Authentication (Future)
```
POST /api/auth/login     - User login
POST /api/auth/logout    - User logout
POST /api/auth/refresh   - Refresh JWT token
```

#### Intelligence Collection (Future)
```
POST /api/collect/start         - Start OSINT collection
GET  /api/collect/status/{id}   - Get collection status
POST /api/collect/stop/{id}     - Stop collection
```

#### Graph Analysis (Future)
```
GET  /api/graph/nodes           - Get graph nodes
GET  /api/graph/edges           - Get graph edges
POST /api/graph/query           - Execute graph query
GET  /api/graph/shortest-path    - Find shortest path
```

#### Reports (Future)
```
GET  /api/reports               - List reports
GET  /api/reports/{id}          - Get specific report
POST /api/reports/generate      - Generate new report
```

#### Users (Future)
```
GET    /api/users               - List users
GET    /api/users/{id}          - Get user details
POST   /api/users               - Create user
PUT    /api/users/{id}          - Update user
DELETE /api/users/{id}          - Delete user
```

### Example API Calls

#### Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "reconvault-backend",
  "version": "0.1.0",
  "message": "ReconVault API is operational"
}
```

#### API Root
```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "name": "ReconVault API",
  "description": "Cyber Reconnaissance Intelligence System",
  "version": "0.1.0",
  "endpoints": {
    "health": "/health",
    "docs": "/api/docs",
    "redoc": "/api/redoc"
  }
}
```

#### Through Nginx
```bash
curl http://localhost/api/health
```

---

## Common Troubleshooting

### Services Won't Start

#### Port Conflicts
**Problem**: Service fails to start due to port already in use.

**Solution**:
```bash
# Check what's using the port
lsof -i :8000
lsof -i :5173
lsof -i :5432
lsof -i :7474
lsof -i :7687
lsof -i :6379

# Kill the process using the port
kill -9 <PID>

# Or change ports in .env file
```

#### Docker Issues
**Problem**: Docker containers won't start or crash immediately.

**Solution**:
```bash
# Check Docker is running
docker ps

# Check Docker disk space
docker system df

# Clean up unused resources
docker system prune -a

# Rebuild containers
docker-compose down -v
docker-compose up -d --build
```

### Database Connection Issues

#### PostgreSQL Connection Refused
**Problem**: Cannot connect to PostgreSQL database.

**Solution**:
```bash
# Check PostgreSQL container is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Verify credentials in .env match
# POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

# Restart PostgreSQL
docker-compose restart postgres
```

#### Neo4j Connection Failed
**Problem**: Cannot connect to Neo4j graph database.

**Solution**:
```bash
# Check Neo4j container status
docker-compose ps neo4j

# Check Neo4j logs
docker-compose logs neo4j

# Access Neo4j browser
# http://localhost:7474

# Verify password in .env
# NEO4J_PASSWORD=neo4j

# Restart Neo4j
docker-compose restart neo4j
```

### Frontend Issues

#### Cannot Access Frontend
**Problem**: Frontend not loading on localhost:5173.

**Solution**:
```bash
# Check frontend container status
docker-compose ps frontend

# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose up -d --build frontend

# Check Vite configuration
# frontend/vite.config.js
```

#### API Connection Errors
**Problem**: Frontend cannot connect to backend API.

**Solution**:
```bash
# Check environment variables
cat .env | grep VITE_API_URL

# Verify backend is running
curl http://localhost:8000/health

# Check CORS configuration
# Backend: app/main.py - CORS middleware

# Restart frontend after .env changes
docker-compose restart frontend
```

### Performance Issues

#### Slow Response Times
**Problem**: API responses are slow.

**Solution**:
```bash
# Check system resources
docker stats

# Check database performance
docker-compose logs postgres | grep -i slow
docker-compose logs neo4j | grep -i slow

# Increase resources in docker-compose.yml
# Add: deploy.resources.limits

# Clear Redis cache
docker-compose exec redis redis-cli FLUSHALL
```

#### High Memory Usage
**Problem**: Services consuming too much memory.

**Solution**:
```bash
# Check memory usage
docker stats --no-stream

# Restart services to clear memory
docker-compose restart

# Adjust memory limits in docker-compose.yml
```

### Logs and Debugging

#### Enable Debug Mode
```bash
# Edit .env
LOG_LEVEL=DEBUG

# Restart services
docker-compose restart backend
docker-compose logs -f backend
```

#### View Container Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend

# Last 100 lines
docker-compose logs --tail=100 backend

# Follow logs
docker-compose logs -f backend
```

#### Enter Container Shell
```bash
# Backend
docker-compose exec backend sh

# Frontend
docker-compose exec frontend sh

# PostgreSQL
docker-compose exec postgres psql -U reconvault_user -d reconvault

# Neo4j
docker-compose exec neo4j cypher-shell -u neo4j -p neo4j

# Redis
docker-compose exec redis redis-cli
```

---

## Development Workflow

### Making Changes

#### Backend Changes
1. Edit code in `backend/app/`
2. Backend auto-reloads with `--reload` flag
3. Check logs: `docker-compose logs -f backend`
4. Test endpoints: `curl http://localhost:8000/health`

#### Frontend Changes
1. Edit code in `frontend/src/`
2. Vite HMR automatically reloads
3. Check browser console for errors
4. Test UI: http://localhost:5173

#### Database Schema Changes
1. Create migration file
2. Run migration: `docker-compose exec backend python -m alembic upgrade head`
3. Verify: `docker-compose exec postgres psql -U reconvault_user -d reconvault -d \d`

### Testing

#### Backend Tests
```bash
# Run all tests
docker-compose exec backend pytest

# Run specific test file
docker-compose exec backend pytest tests/test_main.py

# Run with coverage
docker-compose exec backend pytest --cov=app
```

#### Frontend Tests
```bash
# Run tests
docker-compose exec frontend npm test

# Run tests in watch mode
docker-compose exec frontend npm test -- --watch
```

### Git Workflow

```bash
# Check status
git status

# Add changes
git add .

# Commit changes
git commit -m "Description of changes"

# Push to remote
git push origin feat/branch-name
```

### Pre-commit Hooks
Install pre-commit hooks for code quality:
```bash
pip install pre-commit
pre-commit install
```

---

## Advanced Usage

### Running Services Individually

#### Backend Only
```bash
docker-compose up -d backend postgres neo4j redis
```

#### Frontend Only
```bash
docker-compose up -d frontend
```

#### Databases Only
```bash
docker-compose up -d postgres neo4j redis
```

### Custom Configuration

#### Change Ports
Edit `.env`:
```
BACKEND_PORT=9000
FRONTEND_PORT=3000
POSTGRES_PORT=5433
```

#### Resource Limits
Edit `docker-compose.yml`:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### Scaling Services

```bash
# Scale backend to 3 instances
docker-compose up -d --scale backend=3
```

---

## Getting Help

### Documentation
- Architecture: [docs/architecture.md](architecture.md)
- Ethics: [docs/ethics.md](ethics.md)
- README: [README.md](../README.md)

### Support Channels
- GitHub Issues: Report bugs and request features
- Discussion Forums: Ask questions and share knowledge
- Email: support@reconvault.io

### Common Commands Reference

```bash
# Quick start
docker-compose up -d && docker-compose logs -f

# Stop everything
docker-compose down

# Rebuild and restart
docker-compose down && docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Restart service
docker-compose restart <service>

# Execute command in container
docker-compose exec <service> <command>

# Clean up everything
docker-compose down -v && docker system prune -a
```

---

**Last Updated**: January 2024
**Version**: 0.1.0
