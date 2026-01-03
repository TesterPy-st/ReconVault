# ReconVault - Cyber Reconnaissance Intelligence System

## Vision Statement
ReconVault is a next-generation cyber reconnaissance intelligence system designed to provide comprehensive OSINT (Open Source Intelligence) capabilities with a focus on ethical, passive data collection and analysis. Our system combines modular OSINT pipelines with advanced graph-based visualization to help security professionals understand complex digital landscapes.

## Feature Overview

### Phase 1: Foundation & Infrastructure
- ✅ FastAPI backend with modular architecture
- ✅ React + Vite frontend with graph visualization
- ✅ Docker containerization for all services
- ✅ PostgreSQL and Neo4j database integration
- ✅ Redis for caching and real-time processing
- ✅ Nginx reverse proxy configuration
- ✅ Comprehensive development environment setup

### Future Phases
- OSINT collectors for various data sources
- Intelligence graph construction and analysis
- AI-powered threat detection and pattern recognition
- Automated risk assessment engine
- Reverse OSINT capabilities
- Ethical compliance monitoring

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Databases**: PostgreSQL, Neo4j
- **Caching**: Redis
- **Containerization**: Docker & Docker Compose

### Frontend
- **Framework**: React 18+
- **Build Tool**: Vite
- **Styling**: Tailwind CSS with dark cyber theme
- **Visualization**: react-force-graph, D3.js
- **Animation**: Framer Motion

### Infrastructure
- **Reverse Proxy**: Nginx
- **Environment Management**: Docker Compose
- **Configuration**: .env files

## Quick Start Guide

### Prerequisites
- Docker 20.10+
- Docker Compose 1.29+
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/your-repo/reconvault.git
cd reconvault
```

2. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env file with your configuration
```

3. **Start all services:**
```bash
docker-compose up -d
```

4. **Wait for services to initialize (about 30 seconds):**
```bash
docker-compose ps
```

5. **Access the application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Nginx proxy: http://localhost

### Development Setup

For active development, you may want to run services separately:

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Docker Deployment Guide

### Building and Running
```bash
docker-compose build
docker-compose up -d
```

### Service Management
```bash
# View logs
docker-compose logs

# View logs for specific service
docker-compose logs backend

# Restart services
docker-compose restart

# Stop services
docker-compose down
```

### Service Ports
- **Frontend**: 5173 (Vite dev server)
- **Backend**: 8000 (FastAPI)
- **PostgreSQL**: 5432
- **Neo4j**: 7474 (browser), 7687 (bolt)
- **Redis**: 6379
- **Nginx**: 80 (HTTP), 443 (HTTPS)

## Developers

### Core Team
- **Simanchala Bisoyi** - Lead Architect & Backend Developer
- **Subham Mohanty** - Frontend Specialist & UI/UX Designer
- **Abhinav Kumar** - DevOps & Infrastructure Engineer

### Contributing Guidelines

We welcome contributions to ReconVault! Please follow these guidelines:

1. **Fork the repository** and create your branch from `main`
2. **Follow the existing code style** and architecture patterns
3. **Write comprehensive tests** for new features
4. **Update documentation** for any changes
5. **Submit a pull request** with clear description of changes

### Code Style
- Python: Follow PEP 8 guidelines
- JavaScript: Use ESLint with standard config
- Commit messages: Use conventional commits format
- Documentation: Markdown with clear structure

## Testing

ReconVault includes a comprehensive test suite covering unit tests, integration tests, and end-to-end tests.

### Running Tests

#### Backend Tests
```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test suite
pytest tests/unit/
pytest tests/integration/
```

#### Frontend Tests
```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run E2E tests
npm run test:e2e
```

#### Load Tests
```bash
cd backend/tests/load
locust -f load_test.py --host=http://localhost:8000
```

### Test Coverage

- **Backend:** ≥70% coverage (200+ tests)
- **Frontend:** ≥60% coverage (75+ tests)
- **E2E:** 12+ workflow tests
- **Total:** 340+ tests

See [TESTING.md](TESTING.md) for detailed testing documentation.

### CI/CD Pipeline

The project uses GitHub Actions for continuous integration:

1. **Lint & Format Check** - Code quality verification
2. **Build** - Docker images and application builds
3. **Unit Tests** - Component-level testing
4. **Integration Tests** - Full-stack testing
5. **Security Scan** - Vulnerability detection
6. **Deploy** - Automated deployment (on main branch)

See `.github/workflows/ci.yml` for pipeline configuration.

## Architecture Overview

ReconVault follows a modular microservices architecture:

```
┌─────────────────────────────────────────────────┐
│                 Client Applications               │
└─────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────┐
│                    Nginx Reverse Proxy           │
└─────────────────────────────────────────────────┘
                            │
       ┌───────────────────────────────────────────┴───────────────────────────────────────────┐
       ▼                                                                                   ▼
┌─────────────────┐                                                             ┌─────────────────┐
│   Frontend      │                                                             │    Backend      │
│   (React + Vite)│                                                             │   (FastAPI)     │
└─────────────────┘                                                             └─────────────────┘
       │                                                                                   │
       ▼                                                                                   ▼
┌─────────────────────────────────────────────────┐                           ┌─────────────────────────────────────────────────┐
│                 Graph Visualization               │                           │                 API Endpoints                  │
└─────────────────────────────────────────────────┘                           └─────────────────────────────────────────────────┘
                            │                                                                                   │
                            ▼                                                                                   ▼
┌─────────────────────────────────────────────────┐                           ┌─────────────────────────────────────────────────┐
│                 Intelligence Graph                │                           │                 OSINT Collectors              │
└─────────────────────────────────────────────────┘                           └─────────────────────────────────────────────────┘
                            │                                                                                   │
                            ▼                                                                                   ▼
┌─────────────────────────────────────────────────┐                           ┌─────────────────────────────────────────────────┐
│                 Data Storage Layer                │                           │                 Processing Pipeline            │
│                 (PostgreSQL, Neo4j)              │                           │                 (Normalization, AI, Risk)      │
└─────────────────────────────────────────────────┘                           └─────────────────────────────────────────────────┘
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or feature requests, please open an issue on GitHub or contact the development team.
