# ReconVault - Cyber Reconnaissance Intelligence System

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

## 🎯 Overview

ReconVault is an advanced, modular **cyber reconnaissance and OSINT (Open Source Intelligence) platform** designed for security researchers and analysts. Built with a modern tech stack (FastAPI + React), it enables comprehensive intelligence collection, normalization, and visualization through an interactive graph-based interface with AI-powered analytics.

### Key Capabilities
- 🔍 **Modular OSINT Collection** - 8 specialized collectors for web, social media, domains, IPs, emails, dark web, media, and geospatial data
- 🕸️ **Intelligence Graph** - Interactive 3D visualization powered by Neo4j and D3.js with real-time relationship mapping
- 🤖 **AI-Powered Analytics** - Machine learning models for anomaly detection, risk scoring, and behavioral analysis
- ⚖️ **Ethical Compliance** - Built-in robots.txt enforcement, rate limiting, PII detection, and audit logging
- 📡 **Real-Time Updates** - WebSocket-driven live progress tracking and discovery notifications
- 📊 **Risk Assessment** - Automated exposure analysis with multi-model risk scoring
- 🔒 **Security-First** - Comprehensive audit trails, API key management, and CORS configuration

---

## 📊 Project Status

**Current Version:** 1.0.0-beta  
**Overall Completion:** 93%  
**Status:** Active Development  
**Last Updated:** 2024-01-03

### Phase Completion Matrix

| Phase | Status | Tasks | Completion |
|-------|--------|-------|------------|
| **Phase 1:** Core Backend Pipeline | ✅ Complete | 4/4 | 100% |
| **Phase 2:** Frontend Visualization | 🔄 In Progress | 3/4 | 90% |
| **Phase 3:** Advanced Intelligence | 🔄 In Progress | 3/4 | 85% |
| **Phase 4:** Finalization & Deployment | 🔄 In Progress | 1/2 | 70% |

### Component Status

| Component | Implementation | Testing | Documentation | Status |
|-----------|----------------|---------|---------------|--------|
| Backend API | 100% | 90% | 95% | ✅ Stable |
| Frontend UI | 95% | 80% | 85% | ✅ Stable |
| OSINT Collectors | 100% | 85% | 95% | ✅ Functional |
| Risk Engine | 100% | 85% | 100% | ✅ Functional |
| AI/ML Engine | 100% | 80% | 100% | ✅ Functional |
| Intelligence Graph | 100% | 85% | 95% | ✅ Functional |
| WebSocket Updates | 100% | 85% | 90% | ✅ Functional |
| Infrastructure | 100% | 95% | 100% | ✅ Complete |

**Detailed Status:** See [docs/INDEX.md](docs/INDEX.md) for comprehensive phase and task breakdown.

---

## 🏗️ Architecture

### Technology Stack

**Backend:**
- **Framework:** FastAPI (Python 3.11)
- **ORM:** SQLAlchemy
- **Task Queue:** Celery + Redis
- **Databases:** PostgreSQL (relational), Neo4j (graph), Redis (cache)
- **ML/AI:** scikit-learn, XGBoost, LightGBM

**Frontend:**
- **Framework:** React 18 + Vite
- **Styling:** Tailwind CSS
- **Animation:** Framer Motion
- **Graph:** D3.js + react-force-graph
- **State:** React Context + Custom Hooks

**Infrastructure:**
- **Containerization:** Docker + Docker Compose
- **Reverse Proxy:** Nginx
- **CI/CD:** GitHub Actions (planned)

**Architecture Details:** [docs/architecture.md](docs/architecture.md)

---

## 🚀 Quick Start

### Prerequisites
- **Docker** 20.10+ and **Docker Compose** 2.0+
- **8GB RAM** (16GB recommended)
- **20GB disk space**
- **Python 3.11+** (for local development)
- **Node.js 18+** (for frontend development)

### Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd reconvault
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   # See docs/API_KEYS_REFERENCE.md for API key setup
   ```

3. **Start the System**
   ```bash
   docker-compose up -d --build
   ```

4. **Verify Installation**
   ```bash
   # Check all services are running
   docker-compose ps
   
   # Test backend health
   curl http://localhost:8000/health
   ```

### Accessing the Application

- **Frontend UI:** http://localhost:5173
- **API Documentation:** http://localhost:8000/docs (Swagger UI)
- **API Alternative Docs:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health
- **Neo4j Browser:** http://localhost:7474 (username: neo4j)

### First Steps

1. **Create a Target** via the frontend search form or API
2. **Initiate Collection** - Select collectors and start reconnaissance
3. **View Intelligence Graph** - Explore discovered entities and relationships
4. **Analyze Risk** - Review risk scores and anomaly detection results
5. **Export Data** - Generate reports in JSON, CSV, or GraphML formats

**Detailed Usage:** [docs/usage.md](docs/usage.md)

---

## 📚 Documentation

### Core Documentation
- **[Documentation Index](docs/INDEX.md)** - Complete documentation map with task tracking
- **[Architecture Guide](docs/architecture.md)** - System design and component architecture
- **[Development Guide](docs/DEVELOPMENT.md)** - Setup, coding standards, and workflows
- **[Usage Guide](docs/usage.md)** - User manual for reconnaissance operations
- **[API Reference](API_REFERENCE.md)** - REST API endpoint documentation

### Feature Documentation
- **[Risk Engine](docs/RISK_ENGINE.md)** - Risk assessment models and scoring
- **[Anomaly Detection](docs/ANOMALY_DETECTION.md)** - AI-powered anomaly detection
- **[Ethics & Compliance](docs/ethics.md)** - Compliance monitoring and guidelines
- **[Frontend Implementation](docs/FRONTEND_IMPLEMENTATION.md)** - React component architecture
- **[Frontend Phase 2 Features](docs/FRONTEND_PHASE2.md)** - Advanced UI features

### Operational Documentation
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Production deployment procedures
- **[Testing Guide](TESTING.md)** - Testing strategy and integration tests
- **[Performance Benchmarks](PERFORMANCE.md)** - Performance metrics and optimization
- **[API Keys Reference](API_KEYS_REFERENCE.md)** - External API configuration

### Development Documentation
- **[CI/CD Notes](docs/CI_NOTES.md)** - Continuous integration setup
- **[Code Quality Report](CODE_QUALITY_REPORT.md)** - Code quality metrics
- **[Known Bugs](BUGS_FOUND.md)** - Bug tracking and status
- **[Remaining Tasks](REMAINING_TASKS.md)** - Feature roadmap

---

## ✨ Features

### OSINT Collection
- **Web Collector** - Scrape websites, extract metadata, analyze technologies
- **Social Media Collector** - Gather profiles from Twitter, LinkedIn, Facebook, GitHub
- **Domain Collector** - WHOIS data, DNS records, SSL certificate information
- **Email Collector** - Email validation, breach detection, domain correlation
- **IP Collector** - Geolocation, reputation scores, ASN information
- **Dark Web Collector** - Tor hidden services, paste sites (requires Tor proxy)
- **Media Collector** - EXIF data extraction, image metadata analysis
- **Geo Collector** - Geospatial intelligence, location data enrichment

### Intelligence Analysis
- **Graph Visualization** - Interactive 3D force-directed graph with zoom, pan, search
- **Entity Relationships** - Automatic relationship mapping and correlation
- **Risk Scoring** - Multi-factor risk assessment with ML models
- **Anomaly Detection** - Behavioral, relationship, and infrastructure anomaly identification
- **Pattern Recognition** - Identify suspicious patterns across entities

### Compliance & Ethics
- **Robots.txt Enforcement** - Automatic compliance with site crawler policies
- **Rate Limiting** - Configurable rate limits to prevent abuse
- **PII Detection** - Automatic detection and flagging of personal information
- **Audit Logging** - Comprehensive activity logs for all operations
- **Compliance Dashboard** - Real-time compliance monitoring (in development)

### Real-Time Features
- **WebSocket Updates** - Live collection progress and entity discoveries
- **Notifications** - Real-time alerts for anomalies and critical findings
- **Live Graph Updates** - Graph refreshes automatically as data is collected

### Export & Reporting
- **Multiple Formats** - Export to JSON, CSV, GraphML, GEXF
- **Custom Reports** - Generate intelligence reports with filtering
- **Snapshots** - Save and restore graph states
- **Bookmarks** - Mark and organize important entities

---

## 🐛 Known Issues

**High Priority:**
- **BUG-001:** Rate limiter memory growth under sustained load (mitigation in place)
- **BUG-002:** Neo4j connection pool exhaustion at >500 concurrent requests
- **BUG-006:** Race condition in concurrent Celery tasks (rare)

**Medium Priority:**
- WebSocket reconnection occasionally fails to restore subscriptions
- Frontend graph performance degrades with >1000 nodes
- Dark web collector requires manual Tor proxy configuration

**Low Priority:**
- Some collector error messages lack detail
- Theme switcher dark mode needs refinements

**Full Bug List:** [BUGS_FOUND.md](BUGS_FOUND.md)

---

## 📋 Roadmap

### Short Term (January 2024)
- [ ] Complete comprehensive integration testing
- [ ] Fix critical bugs (BUG-001, BUG-002, BUG-006)
- [ ] Implement compliance dashboard UI
- [ ] Add backend export API endpoint
- [ ] Production deployment hardening

### Medium Term (Q1 2024)
- [ ] Historical risk scoring and trend analysis
- [ ] Advanced graph filtering and search
- [ ] Automated anomaly alerts via WebSocket
- [ ] Multi-tenant architecture support
- [ ] Role-based access control (RBAC)

### Long Term (Q2+ 2024)
- [ ] ML model retraining automation
- [ ] Advanced correlation engine
- [ ] Threat intelligence feed integration
- [ ] Mobile monitoring app
- [ ] Plugin system for custom collectors

**Detailed Roadmap:** [REMAINING_TASKS.md](REMAINING_TASKS.md)

---

## 🔐 Security

### Best Practices
- **Environment Variables:** All sensitive configuration in `.env` (never commit!)
- **API Keys:** Managed via environment variables - see [API_KEYS_REFERENCE.md](API_KEYS_REFERENCE.md)
- **CORS:** Configure `CORS_ORIGINS` appropriately for production
- **Rate Limiting:** Applied to all API endpoints - adjust in `.env`
- **Authentication:** JWT-based auth (user management in development)
- **Audit Logs:** All operations logged to database

### Production Considerations
- Use strong, unique passwords for all services
- Enable SSL/TLS for all connections
- Restrict network access via firewall rules
- Regular security updates and patches
- Monitor audit logs for suspicious activity

---

## 🧪 Testing

### Running Tests

**Backend Tests:**
```bash
cd backend
pytest                          # Run all tests
pytest --cov=app               # With coverage
pytest tests/test_collectors/  # Specific module
```

**Frontend Tests:**
```bash
cd frontend
npm test                # Unit tests
npm run test:e2e       # End-to-end tests
npm test -- --coverage # With coverage
```

**Integration Tests:**
```bash
# See TESTING.md for comprehensive integration test procedures
docker-compose -f docker-compose.test.yml up
```

**Testing Documentation:** [TESTING.md](TESTING.md), [INTEGRATION_TESTING_COMPLETE.md](INTEGRATION_TESTING_COMPLETE.md)

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow code standards (see [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md))
4. Write tests for new features
5. Ensure all tests pass
6. Commit with descriptive messages
7. Push to your fork
8. Open a Pull Request

### Code Standards
- **Backend:** PEP 8, type hints, docstrings (Google style)
- **Frontend:** ESLint + Prettier, PropTypes, component documentation
- **Git:** Conventional commit messages
- **Documentation:** Update relevant docs with code changes

**Development Guide:** [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

- **Simanchala Bisoyi** – Lead Architect & Backend Developer
- **Subham Mohanty** – Frontend Specialist & UI/UX Designer
- **Abhinav Kumar** – DevOps & Infrastructure Engineer

---

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/), [React](https://reactjs.org/), and [Neo4j](https://neo4j.com/)
- Graph visualization powered by [D3.js](https://d3js.org/) and [react-force-graph](https://github.com/vasturiano/react-force-graph)
- UI components styled with [Tailwind CSS](https://tailwindcss.com/)
- Animations by [Framer Motion](https://www.framer.com/motion/)

---

## 📞 Support

- **Documentation:** [docs/INDEX.md](docs/INDEX.md)
- **Issues:** [GitHub Issues](../../issues)
- **Discussions:** [GitHub Discussions](../../discussions)

---

<div align="center">

**Built with ❤️ by the ReconVault Team**

⭐ Star this repository if you find it useful!

</div>
