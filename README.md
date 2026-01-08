# ReconVault - Cyber Intelligence Platform

## What is ReconVault?

ReconVault is a modern, modular cyber reconnaissance and OSINT platform built for security researchers and analysts. It enables comprehensive intelligence collection, normalization, and visualization through an interactive graph-based interface with AI-powered analytics.

## Key Features

- **Modular OSINT collectors** - Web, social media, domains, IPs, emails, dark web, media, and geospatial data
- **Intelligence graph visualization** - Interactive 3D visualization with real-time relationship mapping
- **AI-powered analytics** - Machine learning models for anomaly detection and risk scoring
- **Ethical compliance** - Built-in robots.txt enforcement, rate limiting, and PII detection
- **Real-time updates** - WebSocket-driven live progress tracking and discovery notifications
- **Risk assessment** - Automated exposure analysis with multi-factor risk scoring
- **Export & reporting** - Multiple formats (JSON, CSV, GraphML) with custom reports

### Prerequisites

**For Docker Deployment:**
- Docker 20.10+ and Docker Compose 2.0+
- 8GB RAM (16GB recommended)
- 20GB disk space

**For Local Development:**
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ (optional for local dev)
- Neo4j 5+ (optional for local dev)
- Redis 7+ (optional for local dev)

### Installation

**Option 1: Docker Deployment (Recommended)**

```bash
# Clone and setup
git clone https://github.com/TesterPy-st/ReconVault.git
cd reconvault
cp .env.example .env

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:5173
# API Docs: http://localhost:8000/docs
```

**Option 2: Local Development Setup**

```bash
# Clone repository
git clone https://github.com/TesterPy-st/ReconVault.git
cd ReconVault

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Backend environment setup
# A .env file is already created in backend/.env
# Edit backend/.env to configure database connections if needed
# Note: Database connections are optional for basic functionality

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend setup (new terminal)
cd ../frontend
npm install

# Frontend environment setup
# A .env file is already created in frontend/.env
# It points to http://localhost:8000 for the backend API

# Start frontend
npm run dev

# Access the application
# Frontend: http://localhost:5173
# API Docs: http://localhost:8000/docs
```

### Environment Configuration

**Backend Configuration (`backend/.env`):**
- Basic configuration is already set up in `backend/.env`
- Database connections (PostgreSQL, Neo4j, Redis) can be left as defaults for local dev
- External API keys are optional - collectors will gracefully skip unavailable services

**Optional External APIs:**
All external API integrations are optional. The system will function without them, but certain collectors will have limited functionality:

- **HIBP_API_KEY** - Have I Been Pwned API for breach checking
  - Get free API key from: https://haveibeenpwned.com/API/Key
  - Used by: Email collector for breach detection
  
- **SHODAN_API_KEY** - Shodan API for IP/network reconnaissance  
  - Get API key from: https://account.shodan.io/
  - Used by: IP collector for enhanced device/service discovery

- **VIRUSTOTAL_API_KEY** - VirusTotal API for threat intelligence
  - Get free API key from: https://www.virustotal.com/
  - Used by: Domain and IP collectors for reputation checking

To enable these features, uncomment the respective lines in `backend/.env` and add your API keys.

## Project Status

**Version:** 1.0.0-beta
**Overall Completion:** 97%
**Status:** Production Ready (Minor enhancements pending)

All major features implemented and tested. Ready for deployment with minor polish items remaining.

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design and components
- [API Reference](docs/API.md) - API endpoints and examples

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for development setup, coding standards, and workflows.

### Tech Stack

**Backend:**
- FastAPI (Python 3.11)
- SQLAlchemy, Neo4j, Redis
- Celery for async tasks
- scikit-learn, XGBoost, LightGBM

**Frontend:**
- React 18 + Vite
- Tailwind CSS
- D3.js + react-force-graph
- WebSocket real-time updates

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Follow code standards (PEP 8, ESLint)
4. Write tests for new features
5. Submit a Pull Request

## Team

- **Simanchala Bisoyi** – Lead Architect & Backend Developer
- **Subham Mohanty** – Frontend Specialist & UI/UX Designer
- **Abhinav Kumar** – DevOps & Infrastructure Engineer

## License

MIT License - see [LICENSE](LICENSE) file for details.
---

Built with ❤️ by the ReconVault Team
