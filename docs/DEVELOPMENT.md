# ReconVault Development Guide

**Last Updated:** 2024-01-03  
**Version:** 1.0.0

## Table of Contents
1. [Development Environment Setup](#development-environment-setup)
2. [Project Structure](#project-structure)
3. [Backend Development](#backend-development)
4. [Frontend Development](#frontend-development)
5. [Database Management](#database-management)
6. [Testing](#testing)
7. [Code Standards](#code-standards)
8. [Common Development Tasks](#common-development-tasks)
9. [Troubleshooting](#troubleshooting)

---

## Development Environment Setup

### Prerequisites
- **Docker** 20.10+ and **Docker Compose** 2.0+
- **Python** 3.11+ (for local backend development)
- **Node.js** 18+ and **npm** 9+ (for local frontend development)
- **Git** 2.30+
- **8GB RAM minimum** (16GB recommended)
- **20GB free disk space**

### Initial Setup

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd reconvault
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and configure:
   - Database credentials
   - API keys (see [API_KEYS_REFERENCE.md](../API_KEYS_REFERENCE.md))
   - Secret keys
   - Service ports
   - Feature flags

3. **Start Development Environment**
   ```bash
   docker-compose up -d
   ```

4. **Verify Services**
   ```bash
   # Check all containers are running
   docker-compose ps
   
   # Check backend health
   curl http://localhost:8000/health
   
   # Access frontend
   open http://localhost:5173
   ```

---

## Project Structure

```
reconvault/
├── backend/                    # FastAPI backend application
│   ├── app/
│   │   ├── api/               # API route definitions
│   │   │   └── routes/        # Endpoint implementations
│   │   ├── collectors/        # OSINT collector modules
│   │   ├── models/            # SQLAlchemy database models
│   │   ├── services/          # Business logic layer
│   │   ├── ai_engine/         # ML models and inference
│   │   ├── risk_engine/       # Risk assessment logic
│   │   ├── intelligence_graph/ # Neo4j graph operations
│   │   ├── ethics/            # Compliance and ethics checks
│   │   ├── automation/        # Celery task definitions
│   │   ├── utils/             # Utility functions
│   │   ├── config.py          # Application configuration
│   │   ├── database.py        # Database connection setup
│   │   └── main.py            # Application entry point
│   ├── tests/                 # Backend test suite
│   ├── Dockerfile             # Backend container definition
│   ├── requirements.txt       # Python dependencies
│   └── pytest.ini             # Test configuration
│
├── frontend/                   # React frontend application
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── common/        # Reusable UI components
│   │   │   ├── graph/         # Graph visualization
│   │   │   ├── forms/         # Input forms
│   │   │   ├── panels/        # Side panels and controls
│   │   │   └── inspector/     # Entity detail views
│   │   ├── hooks/             # Custom React hooks
│   │   ├── services/          # API and service clients
│   │   ├── styles/            # Global styles and themes
│   │   ├── utils/             # Utility functions
│   │   ├── App.jsx            # Main application component
│   │   └── main.jsx           # Application entry point
│   ├── public/                # Static assets
│   ├── package.json           # Node dependencies
│   ├── vite.config.js         # Vite build configuration
│   └── tailwind.config.js     # Tailwind CSS configuration
│
├── database/                   # Database initialization scripts
│   ├── init.sql               # PostgreSQL schema
│   └── neo4j_init.cypher      # Neo4j graph schema
│
├── nginx/                      # Nginx reverse proxy configuration
│   └── nginx.conf
│
├── docs/                       # Project documentation
│   ├── INDEX.md               # Documentation index
│   ├── architecture.md        # System architecture
│   ├── usage.md               # User guide
│   └── ...
│
├── docker-compose.yml          # Multi-container orchestration
├── .env.example                # Environment variable template
├── .gitignore                  # Git ignore patterns
└── README.md                   # Project overview
```

---

## Backend Development

### Local Development Setup

1. **Create Python Virtual Environment**
   ```bash
   cd backend
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-test.txt  # For testing
   ```

3. **Run Database Migrations**
   ```bash
   # Ensure PostgreSQL is running
   alembic upgrade head
   ```

4. **Start Backend Server**
   ```bash
   # Development mode with auto-reload
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Or use the docker-compose backend service
   docker-compose up backend
   ```

5. **Access API Documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Backend Code Standards

**Python Style Guide:**
- Follow PEP 8 conventions
- Use type hints for all function signatures
- Maximum line length: 88 characters (Black formatter)
- Docstrings: Google style

**Example:**
```python
from typing import Optional, List
from app.models.entity import Entity

async def get_entity_by_id(
    entity_id: str,
    include_relationships: bool = False
) -> Optional[Entity]:
    """
    Retrieve an entity by its unique identifier.
    
    Args:
        entity_id: The unique identifier of the entity
        include_relationships: Whether to include related entities
        
    Returns:
        The entity object if found, None otherwise
        
    Raises:
        DatabaseError: If database connection fails
    """
    # Implementation
    pass
```

**Code Organization:**
- **Models:** Database models in `app/models/`
- **Routes:** API endpoints in `app/api/routes/`
- **Services:** Business logic in `app/services/`
- **Utilities:** Helper functions in `app/utils/`

**Error Handling:**
```python
from fastapi import HTTPException, status

# Always use appropriate HTTP status codes
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Entity not found"
)

# Log errors before raising
logger.error(f"Failed to fetch entity {entity_id}: {str(e)}")
```

**Database Operations:**
```python
from sqlalchemy.orm import Session
from app.database import get_db

async def create_entity(entity_data: dict, db: Session):
    """Use dependency injection for database sessions."""
    try:
        entity = Entity(**entity_data)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create entity: {str(e)}")
        raise
```

### Running Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_collectors.py

# Run specific test
pytest tests/test_collectors.py::test_web_collector_basic

# Run with verbose output
pytest -v -s
```

---

## Frontend Development

### Local Development Setup

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm run dev
   # Application runs on http://localhost:5173
   ```

3. **Build for Production**
   ```bash
   npm run build
   npm run preview  # Preview production build
   ```

### Frontend Code Standards

**React/JavaScript Style Guide:**
- Use functional components with hooks
- PropTypes for component props validation
- ESLint configuration in `.eslintrc.js`
- Prettier for code formatting

**Example Component:**
```jsx
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

/**
 * EntityCard component displays entity information.
 *
 * @param {Object} props - Component props
 * @param {Object} props.entity - The entity object to display
 * @param {Function} props.onSelect - Callback when entity is selected
 */
const EntityCard = ({ entity, onSelect }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    // Cleanup logic
    return () => {
      // Cleanup code
    };
  }, [entity.id]);

  const handleClick = () => {
    setIsExpanded(!isExpanded);
    onSelect(entity);
  };

  return (
    <div className="entity-card" onClick={handleClick}>
      <h3>{entity.name}</h3>
      {isExpanded && <div>{entity.description}</div>}
    </div>
  );
};

EntityCard.propTypes = {
  entity: PropTypes.shape({
    id: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    description: PropTypes.string,
  }).isRequired,
  onSelect: PropTypes.func.isRequired,
};

export default EntityCard;
```

**API Service Pattern:**
```javascript
// services/api.js
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export default apiClient;
```

**Custom Hooks Pattern:**
```javascript
// hooks/useGraph.js
import { useState, useEffect, useCallback } from 'react';
import graphService from '../services/graphService';

export const useGraph = (targetId) => {
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchGraph = useCallback(async () => {
    try {
      setLoading(true);
      const data = await graphService.getGraph(targetId);
      setGraphData(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [targetId]);

  useEffect(() => {
    if (targetId) {
      fetchGraph();
    }
  }, [targetId, fetchGraph]);

  const refreshGraph = useCallback(() => {
    fetchGraph();
  }, [fetchGraph]);

  return { graphData, loading, error, refreshGraph };
};
```

### Running Frontend Tests

```bash
cd frontend

# Run unit tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage

# Run E2E tests
npm run test:e2e
```

---

## Database Management

### PostgreSQL

**Connection String:**
```
postgresql://user:password@localhost:5432/reconvault
```

**Common Operations:**
```bash
# Connect to database
docker exec -it reconvault-postgres psql -U reconvault

# List tables
\dt

# Describe table
\d entities

# Run SQL query
SELECT * FROM targets LIMIT 10;

# Exit
\q
```

**Alembic Migrations:**
```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

### Neo4j

**Connection:**
- Bolt: bolt://localhost:7687
- HTTP: http://localhost:7474
- Username: neo4j
- Password: (from .env file)

**Cypher Queries:**
```cypher
// View all nodes and relationships
MATCH (n) RETURN n LIMIT 25;

// Count entities by type
MATCH (n) RETURN labels(n) AS type, count(n) AS count;

// Find relationships
MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 50;

// Delete all data (CAUTION!)
MATCH (n) DETACH DELETE n;
```

### Redis

**Connection:**
```bash
# Connect to Redis CLI
docker exec -it reconvault-redis redis-cli

# View all keys
KEYS *

# Get key value
GET key_name

# Monitor commands
MONITOR

# Clear all data (CAUTION!)
FLUSHALL
```

---

## Testing

### Backend Testing Strategy

**Test Types:**
1. **Unit Tests:** Individual functions and methods
2. **Integration Tests:** Service interactions and database operations
3. **API Tests:** Endpoint request/response validation
4. **End-to-End Tests:** Complete workflows

**Example Test:**
```python
# tests/test_collectors/test_web_collector.py
import pytest
from app.collectors.web_collector import WebCollector

@pytest.mark.asyncio
async def test_web_collector_basic():
    """Test basic web collection functionality."""
    collector = WebCollector()
    result = await collector.collect("https://example.com")
    
    assert result is not None
    assert result.url == "https://example.com"
    assert result.status_code == 200
    assert len(result.metadata) > 0

@pytest.fixture
def sample_entity():
    """Fixture providing a sample entity for tests."""
    return {
        "name": "Test Entity",
        "type": "domain",
        "value": "example.com"
    }

def test_entity_creation(sample_entity):
    """Test entity model creation."""
    entity = Entity(**sample_entity)
    assert entity.name == "Test Entity"
    assert entity.type == "domain"
```

### Frontend Testing Strategy

**Test Types:**
1. **Component Tests:** React component rendering and interaction
2. **Hook Tests:** Custom hook behavior
3. **Integration Tests:** Component integration
4. **E2E Tests:** Full user workflows

**Example Test:**
```javascript
// src/__tests__/components/EntityCard.test.jsx
import { render, screen, fireEvent } from '@testing-library/react';
import EntityCard from '../../components/EntityCard';

describe('EntityCard', () => {
  const mockEntity = {
    id: '123',
    name: 'Test Entity',
    type: 'domain',
  };

  const mockOnSelect = jest.fn();

  test('renders entity information', () => {
    render(<EntityCard entity={mockEntity} onSelect={mockOnSelect} />);
    
    expect(screen.getByText('Test Entity')).toBeInTheDocument();
  });

  test('calls onSelect when clicked', () => {
    render(<EntityCard entity={mockEntity} onSelect={mockOnSelect} />);
    
    fireEvent.click(screen.getByText('Test Entity'));
    
    expect(mockOnSelect).toHaveBeenCalledWith(mockEntity);
  });
});
```

---

## Code Standards

### Linting and Formatting

**Backend:**
```bash
cd backend

# Format code with Black
black app/

# Sort imports
isort app/

# Check code style
flake8 app/

# Type checking
mypy app/
```

**Frontend:**
```bash
cd frontend

# Check code style
npm run lint

# Fix auto-fixable issues
npm run lint -- --fix

# Format with Prettier
npm run format
```

### Git Workflow

**Branch Naming:**
- `feature/description` - New features
- `bugfix/issue-number` - Bug fixes
- `hotfix/description` - Critical production fixes
- `refactor/description` - Code refactoring
- `docs/description` - Documentation updates

**Commit Message Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Example:**
```
feat(collectors): add media collector with EXIF extraction

- Implement EXIF metadata extraction from images
- Add support for GPS coordinates
- Include camera information parsing

Closes #42
```

---

## Common Development Tasks

### Adding a New Collector

1. **Create Collector File:**
   ```bash
   touch backend/app/collectors/new_collector.py
   ```

2. **Implement Base Class:**
   ```python
   from app.collectors.base_collector import BaseCollector
   from typing import Dict, Any
   
   class NewCollector(BaseCollector):
       """Collector for XYZ data sources."""
       
       async def collect(self, target: str) -> Dict[str, Any]:
           """Collect data from target."""
           # Implementation
           pass
   ```

3. **Register Collector:**
   Update `backend/app/services/collection_pipeline_service.py`

4. **Add Tests:**
   Create `backend/tests/test_collectors/test_new_collector.py`

### Adding a New API Endpoint

1. **Create Route File or Update Existing:**
   ```python
   # backend/app/api/routes/new_endpoint.py
   from fastapi import APIRouter, Depends, HTTPException
   from sqlalchemy.orm import Session
   from app.database import get_db
   
   router = APIRouter(prefix="/api/v1/new", tags=["new"])
   
   @router.get("/{item_id}")
   async def get_item(item_id: str, db: Session = Depends(get_db)):
       """Get item by ID."""
       # Implementation
       pass
   ```

2. **Register Router:**
   Update `backend/app/api/routes/__init__.py`

3. **Update OpenAPI Tags:**
   Add to `backend/app/main.py`

4. **Add Tests:**
   Create `backend/tests/test_api/test_new_endpoint.py`

### Adding a New Frontend Component

1. **Create Component File:**
   ```bash
   touch frontend/src/components/NewComponent.jsx
   ```

2. **Implement Component:**
   ```jsx
   import React from 'react';
   import PropTypes from 'prop-types';
   
   const NewComponent = ({ prop1, prop2 }) => {
     return (
       <div className="new-component">
         {/* Implementation */}
       </div>
     );
   };
   
   NewComponent.propTypes = {
     prop1: PropTypes.string.isRequired,
     prop2: PropTypes.func,
   };
   
   export default NewComponent;
   ```

3. **Add Tests:**
   Create `frontend/src/__tests__/components/NewComponent.test.jsx`

---

## Troubleshooting

### Common Issues

**1. Docker Container Won't Start**
```bash
# Check logs
docker-compose logs backend

# Rebuild container
docker-compose build --no-cache backend
docker-compose up backend
```

**2. Database Connection Errors**
```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Check connection
docker exec reconvault-postgres pg_isready

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

**3. Neo4j Connection Issues**
```bash
# Verify Neo4j is running
docker-compose ps neo4j

# Check logs
docker-compose logs neo4j

# Access browser interface
open http://localhost:7474
```

**4. Frontend Build Errors**
```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
npm run dev
```

**5. Python Import Errors**
```bash
# Ensure virtual environment is activated
source backend/venv/bin/activate

# Reinstall dependencies
pip install -r backend/requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

**6. Port Already in Use**
```bash
# Find process using port
lsof -i :8000  # Or relevant port

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Debug Mode

**Backend Debug Mode:**
```python
# In backend/app/main.py
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add debug statements
logger.debug("Debug information here")
```

**Frontend Debug Mode:**
```javascript
// Enable React DevTools
// Add to frontend/src/main.jsx
if (import.meta.env.DEV) {
  console.log('Running in development mode');
}
```

### Performance Profiling

**Backend:**
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Code to profile

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

**Frontend:**
```javascript
// Use React Profiler
import { Profiler } from 'react';

const onRenderCallback = (id, phase, actualDuration) => {
  console.log(`${id} (${phase}) took ${actualDuration}ms`);
};

<Profiler id="GraphCanvas" onRender={onRenderCallback}>
  <GraphCanvas />
</Profiler>
```

---

## Additional Resources

- [Architecture Documentation](architecture.md)
- [API Reference](../API_REFERENCE.md)
- [Testing Guide](../TESTING.md)
- [Deployment Guide](../DEPLOYMENT_GUIDE.md)
- [Performance Optimization](../PERFORMANCE.md)

---

**Questions or Issues?**  
Contact the development team or create an issue in the project repository.

**Last Updated:** 2024-01-03  
**Maintained By:** ReconVault Development Team
