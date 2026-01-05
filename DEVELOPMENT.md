# Development Guide

## Setup

### Prerequisites
- Python 3.11+ and Node.js 18+
- Docker 20.10+ and Docker Compose 2.0+
- Git

### Quick Setup (Docker)
```bash
# Clone repository
git clone https://github.com/TesterPy-st/ReconVault.git
cd reconvault

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start all services
docker-compose up -d --build

# Check services
docker-compose ps
```

### Local Development Setup

**Backend:**
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## Project Structure

```
ReconVault/
├── backend/app/          # FastAPI application
│   ├── api/routes/       # API endpoints
│   ├── services/         # Business logic
│   ├── collectors/       # OSINT collectors
│   ├── models/           # Database models
│   ├── ai_engine/        # ML models
│   └── risk_engine/      # Risk analysis
├── frontend/src/         # React application
│   ├── components/       # React components
│   ├── services/         # API clients
│   └── hooks/            # Custom React hooks
└── docs/                 # Documentation
```

## Development Commands

### Backend Commands
```bash
cd backend

# Run tests
pytest                          # All tests
pytest --cov=app               # With coverage
pytest tests/test_collectors/  # Specific module

# Code quality
black app/                     # Format code
flake8 app/                    # Lint code
isort app/                     # Sort imports

# Run server
uvicorn app.main:app --reload
```

### Frontend Commands
```bash
cd frontend

# Run tests
npm test                       # Unit tests
npm test -- --coverage         # With coverage

# Code quality
npm run lint                   # Lint code
npm run format                 # Format code

# Development
npm run dev                    # Start dev server
npm run build                  # Production build
```

### Docker Commands
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs backend
docker-compose logs frontend

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# Enter container
docker-compose exec backend bash
docker-compose exec frontend sh
```

## Code Standards

### Backend (Python)
- Follow PEP 8 conventions
- Use type hints for all function signatures
- Docstrings in Google style
- Maximum line length: 88 characters (Black formatter)
- Use async/await for I/O operations
- Proper error handling with HTTP status codes

**Example:**
```python
from fastapi import HTTPException, status
from typing import List, Optional

async def get_targets(
    limit: int = 100,
    offset: int = 0
) -> List[Target]:
    """Get targets with pagination.

    Args:
        limit: Maximum number of targets to return
        offset: Number of targets to skip

    Returns:
        List of target objects

    Raises:
        HTTPException: If database query fails
    """
    try:
        targets = await db.query(Target).limit(limit).offset(offset).all()
        return targets
    except Exception as e:
        logger.error(f"Failed to fetch targets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch targets"
        )
```

### Frontend (React)
- Use functional components with hooks
- PropTypes for all component props
- ESLint + Prettier for formatting
- useCallback for event handlers
- useMemo for expensive calculations
- Proper cleanup in useEffect

**Example:**
```jsx
import React, { useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';

const MyComponent = ({ data, onUpdate }) => {
  const [state, setState] = useState(null);

  useEffect(() => {
    // Effect logic
    return () => {
      // Cleanup
    };
  }, [dependencies]);

  const handleClick = useCallback(() => {
    onUpdate(data);
  }, [onUpdate, data]);

  return <div onClick={handleClick}>{/* content */}</div>;
};

MyComponent.propTypes = {
  data: PropTypes.object.isRequired,
  onUpdate: PropTypes.func.isRequired,
};

export default MyComponent;
```

## Testing

### Backend Tests
- Unit tests for all services and collectors
- Integration tests for API endpoints
- Database connection tests
- Coverage target: 80%

### Frontend Tests
- Component unit tests
- Integration tests for API calls
- E2E tests with Playwright
- Coverage target: 70%

### Running Tests
```bash
# Backend
cd backend
pytest --cov=app

# Frontend
cd frontend
npm test -- --coverage
```

## Submitting Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. Make your changes and test:
   ```bash
   # Backend
   pytest
   black app/
   flake8 app/

   # Frontend
   npm test
   npm run lint
   ```

3. Commit with clear messages:
   ```bash
   git add .
   git commit -m "feat(targets): add bulk import feature"
   ```

4. Push and create PR:
   ```bash
   git push origin feature/amazing-feature
   # Create PR on GitHub
   ```

## Common Issues

### Virtual Environment
**Never edit files inside `backend/venv/` directory.** If corrupted:
```bash
rm -rf backend/venv
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Database Connection
If database connection fails:
```bash
# Check containers
docker-compose ps

# Restart database
docker-compose restart postgres neo4j redis

# Check logs
docker-compose logs postgres
```

### Frontend Build Errors
```bash
# Clear cache
rm -rf node_modules/.vite
npm run dev
```

## Additional Resources
- [Architecture](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)
