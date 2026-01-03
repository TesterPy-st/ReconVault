# ReconVault - Cyber Reconnaissance Intelligence System

## 🎯 Overview
ReconVault is an advanced, modular cyber reconnaissance and OSINT (Open Source Intelligence) platform. Built with FastAPI and React, it enables security researchers and analysts to collect, normalize, and visualize intelligence data through an interactive graph-based interface. The system integrates multiple intelligence sources, applies AI-powered anomaly detection, and ensures ethical compliance throughout the collection process.

## ✨ Features
- **Modular OSINT Collectors**: Specialized collectors for Web, Social Media, Domains, IPs, Emails, and Dark Web.
- **Intelligence Graph**: Visualization and relationship mapping using Neo4j and D3.js.
- **AI Anomaly Detection**: ML-powered detection of behavioral, relationship, and infrastructure anomalies.
- **Risk Assessment Engine**: Automated risk scoring and exposure analysis for all discovered entities.
- **Ethical Compliance**: Built-in monitoring for robots.txt, rate limits, and PII detection.
- **Real-time Updates**: Live progress and discovery notifications via WebSockets.
- **Comprehensive Audit**: Full logging of all collection activities and system changes.

## 📊 Project Status
- **Overall Completion**: 93%
- **Completed Tasks**: 13/14
- **Last Updated**: 2024-01-03

| Component | Status | Completion |
|-----------|--------|------------|
| Backend API | Stable | 95% |
| Frontend UI | Stable | 90% |
| Collectors | Functional | 95% |
| Risk Engine | Functional | 85% |
| AI Engine | Functional | 80% |
| Infrastructure | Complete | 100% |

## 🏗️ Architecture
- **Backend**: FastAPI (Python 3.11), SQLAlchemy, Celery.
- **Frontend**: React 18, Vite, Tailwind CSS, Framer Motion.
- **Databases**: PostgreSQL (Relational), Neo4j (Graph), Redis (Cache/Task Queue).
- **Infrastrucutre**: Docker, Docker Compose, Nginx.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- 8GB RAM recommended
- Python 3.11+ (for local development)

### Installation
1. Clone the repository.
2. Setup environment variables:
   ```bash
   cp .env.example .env
   ```
3. Configure your API keys in `.env` (see [API Keys Reference](API_KEYS_REFERENCE.md)).
4. Build and start the system:
   ```bash
   docker-compose up -d --build
   ```

### Accessing the System
- **Frontend**: `http://localhost:5173`
- **API Documentation**: `http://localhost:8000/docs`
- **System Health**: `http://localhost:8000/health`

## 📚 Documentation
- [API Reference](API_REFERENCE.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [API Keys Setup](API_KEYS_REFERENCE.md)
- [Code Quality Report](CODE_QUALITY_REPORT.md)
- [Testing Guide](TESTING.md)
- [Performance Benchmarks](PERFORMANCE.md)

## 🐛 Known Issues
See [BUGS_FOUND.md](BUGS_FOUND.md) for a detailed list of active bugs and their status.
- **BUG-001**: Rate limiter memory growth issue.
- **BUG-002**: Neo4j connection pool exhaustion under extreme load.
- **BUG-006**: Race condition in concurrent collection tasks.

## 📋 Remaining Tasks
See [REMAINING_TASKS.md](REMAINING_TASKS.md) for the roadmap of incomplete features.
- [ ] Implement WebSocket broadcasts for real-time anomaly alerts.
- [ ] Add historical risk scoring and trend analysis.
- [ ] Optimize frontend graph rendering for >1000 nodes.

## 🔐 Security
- **API Key Management**: All keys are managed via environment variables and should never be committed to the repository.
- **CORS Configuration**: Restrict `CORS_ORIGINS` in production settings.
- **Rate Limiting**: Configurable rate limits are applied to all API endpoints.

## 🤝 Contributing
Please read the [Contributing Guidelines](CONTRIBUTING.md) before submitting pull requests.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team
- **Simanchala Bisoyi** – Lead Architect & Backend Developer
- **Subham Mohanty** – Frontend Specialist & UI/UX Designer
- **Abhinav Kumar** – DevOps & Infrastructure Engineer

---
Built with ❤️ by the ReconVault Team.
