# ReconVault Usage Guide

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Running Services](#running-services)
3. [API Endpoints](#api-endpoints)
4. [Frontend Development](#frontend-development)
5. [Backend Development](#backend-development)
6. [Database Management](#database-management)
7. [Common Workflows](#common-workflows)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

## Development Environment Setup

### Prerequisites

Ensure you have the following installed:

- **Docker** 20.10+ and **Docker Compose** 1.29+
- **Node.js** 18+ (for frontend development)
- **Python** 3.11+ (for backend development)
- **Git** for version control

### Clone the Repository

```bash
git clone https://github.com/your-organization/reconvault.git
cd reconvault
```

### Environment Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file with your configuration:
   ```bash
   nano .env
   ```

3. Key configuration options:
   ```env
   # Backend Configuration
   BACKEND_PORT=8000
   BACKEND_HOST=0.0.0.0
   
   # Frontend Configuration  
   FRONTEND_PORT=5173
   FRONTEND_HOST=0.0.0.0
   
   # Database Configuration
   POSTGRES_DB=reconvault
   POSTGRES_USER=reconvault_user
   POSTGRES_PASSWORD=changeme
   NEO4J_AUTH=neo4j/neo4j
   ```

## Running Services

### Full Stack with Docker Compose

```bash
# Start all services
docker-compose up -d

# View service status
docker-compose ps

# Check logs
docker-compose logs

# Check specific service logs
docker-compose logs backend

# Stop all services
docker-compose down
```

### Service Health Monitoring

```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend availability
curl http://localhost:5173

# Check Nginx proxy
curl http://localhost/api/health
```

### Individual Service Management

```bash
# Start specific service
docker-compose up -d backend

# Restart service
docker-compose restart backend

# Scale service (for production)
docker-compose up -d --scale backend=3

# Rebuild service
docker-compose build backend
```

## API Endpoints

### Base URL
- **Development:** `http://localhost:8000`
- **Production:** `https://your-domain.com/api`

### Available Endpoints

#### System Endpoints

| Endpoint | Method | Description | Example |
|----------|--------|-------------|---------|
| `/health` | GET | Health check | `curl http://localhost:8000/health` |
| `/` | GET | Root endpoint | `curl http://localhost:8000/` |
| `/api/` | GET | API information | `curl http://localhost:8000/api/` |

#### Future Endpoints (Phase 2+)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/collect` | POST | Start OSINT collection |
| `/api/graph` | GET | Get intelligence graph data |
| `/api/analyze` | POST | Run analysis on data |
| `/api/risk` | POST | Assess risk score |
| `/api/reverse` | POST | Reverse OSINT lookup |

### API Response Format

All API responses follow this structure:

```json
{
  "status": "success|error",
  "message": "Human-readable message",
  "data": {},
  "timestamp": "ISO timestamp"
}
```

### Error Handling

Common error responses:

```json
{
  "status": "error",
  "message": "Resource not found",
  "error": "NotFoundError",
  "code": 404
}
```

## Frontend Development

### Running Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Frontend Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── components/      # Reusable components
│   ├── pages/           # Page components
│   ├── graph/           # Graph visualization
│   ├── services/        # API services
│   ├── styles/          # CSS and Tailwind
│   ├── App.jsx          # Main app component
│   └── main.jsx         # Entry point
├── package.json         # Dependencies
├── vite.config.js       # Vite configuration
└── tailwind.config.js   # Tailwind config
```

### Key Frontend Technologies

- **React 18+** - Component-based UI
- **Vite** - Fast development server
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Animations
- **react-force-graph** - Graph visualization
- **D3.js** - Advanced data visualization
- **Axios** - API requests

### Frontend Development Tips

1. **Component Creation:**
   ```bash
   # Create new component
   mkdir -p src/components/NewComponent
   touch src/components/NewComponent/index.jsx
   touch src/components/NewComponent/styles.css
   ```

2. **API Integration:**
   ```javascript
   import axios from 'axios';
   
   const fetchData = async () => {
     try {
       const response = await axios.get('/api/endpoint');
       return response.data;
     } catch (error) {
       console.error('API Error:', error);
       throw error;
     }
   };
   ```

3. **Graph Visualization:**
   ```javascript
   import ForceGraph from 'react-force-graph';
   
   const MyGraph = ({ data }) => (
     <ForceGraph
       graphData={data}
       nodeLabel="id"
       linkDirectionalArrowLength={6}
       linkDirectionalArrowRelPos={1}
     />
   );
   ```

## Backend Development

### Running Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Start development server
uvicorn app.main:app --reload

# Run with specific host/port
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Backend Structure

```
backend/
├── app/
│   ├── api/              # API endpoints
│   ├── collectors/       # OSINT collectors
│   ├── normalization/    # Data normalization
│   ├── intelligence_graph/ # Graph operations
│   ├── media_osint/      # Media analysis
│   ├── ai_engine/        # AI processing
│   ├── risk_engine/      # Risk assessment
│   ├── reverse_osint/    # Reverse OSINT
│   ├── automation/       # Workflow automation
│   ├── ethics/           # Ethical compliance
│   ├── models/           # Data models
│   ├── main.py           # FastAPI app
│   └── __init__.py       # Module init
├── requirements.txt      # Dependencies
└── Dockerfile            # Container config
```

### Creating New API Endpoints

1. **Create new router:**
   ```python
   # backend/app/api/new_router.py
   from fastapi import APIRouter
   
   router = APIRouter(prefix="/new", tags=["new"])
   
   @router.get("/endpoint")
   async def new_endpoint():
       return {"message": "New endpoint working"}
   ```

2. **Include router in main app:**
   ```python
   # backend/app/main.py
   from app.api.new_router import router as new_router
   
   app.include_router(new_router)
   ```

3. **Add Pydantic models:**
   ```python
   # backend/app/models/new_models.py
   from pydantic import BaseModel
   
   class NewModel(BaseModel):
       field1: str
       field2: int
       optional_field: str | None = None
   ```

### Backend Development Tips

1. **Environment Variables:**
   ```python
   from dotenv import load_dotenv
   import os
   
   load_dotenv()
   db_url = os.getenv("DATABASE_URL")
   ```

2. **Error Handling:**
   ```python
   from fastapi import HTTPException
   
   @router.get("/items/{item_id}")
   async def read_item(item_id: int):
       if item_id not in database:
           raise HTTPException(status_code=404, detail="Item not found")
       return database[item_id]
   ```

3. **Async Database Operations:**
   ```python
   from sqlalchemy.ext.asyncio import AsyncSession
   
   @router.get("/data/")
   async def get_data(session: AsyncSession = Depends(get_db)):
       result = await session.execute(select(DataModel))
       return result.scalars().all()
   ```

## Database Management

### PostgreSQL

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U reconvault_user -d reconvault

# Common commands
\dt                     # List tables
\d table_name           # Describe table
SELECT * FROM table;    # Query data
```

### Neo4j

```bash
# Access Neo4j browser
# Open http://localhost:7474 in browser
# Username: neo4j, Password: neo4j (from .env)

# Cypher shell
docker-compose exec neo4j cypher-shell -u neo4j -p neo4j

# Common Cypher queries
MATCH (n) RETURN n LIMIT 10;  # Get first 10 nodes
CREATE (n:Person {name: 'Alice'});  # Create node
MATCH (a:Person), (b:Person) 
WHERE a.name = 'Alice' AND b.name = 'Bob'
CREATE (a)-[r:KNOWS]->(b);  # Create relationship
```

### Redis

```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Common commands
PING                    # Test connection
SET key "value"        # Set value
GET key                 # Get value
KEYS *                 # List all keys
DEL key                # Delete key
```

## Common Workflows

### Adding New OSINT Collector

1. **Create collector class:**
   ```python
   # backend/app/collectors/new_collector.py
   from . import BaseCollector
   
   class NewCollector(BaseCollector):
       def __init__(self):
           super().__init__("new_collector")
           self.source = "https://example.com"
       
       def collect(self):
           # Implementation here
           pass
   ```

2. **Add to collectors module:**
   ```python
   # backend/app/collectors/__init__.py
   from .new_collector import NewCollector
   
   __all__ = ["BaseCollector", "NewCollector"]
   ```

3. **Integrate with automation:**
   ```python
   # backend/app/automation/__init__.py
   from app.collectors import NewCollector
   
   class AutomationEngine:
       def __init__(self):
           self.collectors = [NewCollector()]
   ```

### Creating Graph Visualization

1. **Backend API endpoint:**
   ```python
   # backend/app/api/graph.py
   from fastapi import APIRouter
   
   router = APIRouter(prefix="/graph", tags=["graph"])
   
   @router.get("/data")
   async def get_graph_data():
       return {
           "nodes": [{"id": "node1", "name": "Node 1"}],
           "links": [{"source": "node1", "target": "node2"}]
       }
   ```

2. **Frontend component:**
   ```javascript
   // src/components/GraphViewer/index.jsx
   import { useEffect, useState } from 'react';
   import axios from 'axios';
   import ForceGraph from 'react-force-graph';
   
   export default function GraphViewer() {
     const [graphData, setGraphData] = useState({nodes: [], links: []});
     
     useEffect(() => {
       const fetchGraphData = async () => {
         const response = await axios.get('/api/graph/data');
         setGraphData(response.data);
       };
       fetchGraphData();
     }, []);
     
     return (
       <div className="h-screen w-full">
         <ForceGraph
           graphData={graphData}
           nodeLabel="name"
           linkDirectionalArrowLength={6}
         />
       </div>
     );
   }
   ```

## Troubleshooting

### Common Issues and Solutions

#### Docker Issues

**Problem:** `docker-compose up` fails with port conflicts

**Solution:**
```bash
# Find conflicting process
sudo lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different ports in .env
```

**Problem:** Services not starting properly

**Solution:**
```bash
# Check logs
docker-compose logs service_name

# Restart service
docker-compose restart service_name

# Rebuild if needed
docker-compose build service_name
```

#### Backend Issues

**Problem:** Backend not responding

**Solution:**
```bash
# Check if running
curl http://localhost:8000/health

# Check logs
docker-compose logs backend

# Test locally
cd backend
uvicorn app.main:app --reload
```

**Problem:** Dependency conflicts

**Solution:**
```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Frontend Issues

**Problem:** Frontend build fails

**Solution:**
```bash
# Clean and reinstallm -rf node_modules package-lock.json
npm install

# Check Node.js version
node -v  # Should be 18+

# Clear cache
npm cache clean --force
```

**Problem:** Vite HMR not working

**Solution:**
```bash
# Check Vite config
# Ensure proxy settings are correct

# Restart Vite server
npm run dev
```

#### Database Issues

**Problem:** Cannot connect to PostgreSQL

**Solution:**
```bash
# Check container status
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U reconvault_user -d reconvault
```

**Problem:** Neo4j not accessible

**Solution:**
```bash
# Check Neo4j logs
docker-compose logs neo4j

# Reset password if needed
docker-compose exec neo4j cypher-shell -u neo4j -p neo4j
:server change-password
```

### Debugging Tips

1. **Check service dependencies:**
   ```bash
   docker-compose ps --services
   ```

2. **Test individual services:**
   ```bash
   # Test backend directly
   curl http://localhost:8000/health
   
   # Test frontend directly
   curl http://localhost:5173
   ```

3. **Inspect network:**
   ```bash
   docker network inspect reconvault-network
   ```

4. **Check environment variables:**
   ```bash
   docker-compose exec backend env
   ```

## Best Practices

### Development Best Practices

1. **Use environment variables** for all configuration
2. **Follow the existing code style** and patterns
3. **Write comprehensive tests** for new features
4. **Document your code** with clear comments
5. **Keep dependencies updated** but tested
6. **Use feature branches** for development
7. **Write meaningful commit messages**

### Docker Best Practices

1. **Use specific version tags** in Dockerfiles
2. **Keep images small** with multi-stage builds
3. **Use .dockerignore** to exclude unnecessary files
4. **Set proper health checks** for all services
5. **Use named volumes** for persistent data
6. **Clean up regularly** with `docker system prune`

### Security Best Practices

1. **Never commit secrets** to version control
2. **Use strong passwords** for all services
3. **Keep services updated** with latest patches
4. **Implement proper authentication** (future phases)
5. **Use HTTPS** in production
6. **Regularly audit dependencies** for vulnerabilities

### Performance Best Practices

1. **Use async/await** for I/O operations
2. **Implement caching** where appropriate
3. **Optimize database queries**
4. **Use connection pooling** for databases
5. **Minimize frontend bundle size**
6. **Implement lazy loading** for large components

## Conclusion

This usage guide provides comprehensive instructions for:
- Setting up the development environment
- Running and managing services
- Developing frontend and backend components
- Working with databases
- Troubleshooting common issues
- Following best practices

For additional help, refer to the [architecture documentation](architecture.md) and [ethical guidelines](ethics.md), or contact the development team.