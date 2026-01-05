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

- Docker 20.10+ and Docker Compose 2.0+
- 8GB RAM (16GB recommended)
- 20GB disk space

### Installation

```bash
# Clone and setup
git clone <repository-url>
cd reconvault
cp .env.example .env

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:5173
# API Docs: http://localhost:8000/docs
```

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
