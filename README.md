# ReconVault

<div align="center">

![ReconVault](frontend/public/reconvault.svg)

**Cyber Reconnaissance Intelligence System**

*A graph-based OSINT pipeline for advanced threat intelligence and network analysis*

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-green.svg)](https://github.com/reconvault/reconvault)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)

</div>

---

## 🎯 Vision

ReconVault is a comprehensive cyber reconnaissance intelligence system designed to collect, analyze, and correlate Open Source Intelligence (OSINT) data from various public sources. Our system uses a graph-based approach to visualize relationships between entities and identify patterns across multiple data streams.

### Core Capabilities

- **🔍 Multi-Source OSINT Collection**: Gather intelligence from social media, public databases, and web sources
- **🕸️ Graph-Based Analysis**: Visualize complex relationships and network patterns
- **🤖 AI-Powered Insights**: Machine learning models for pattern recognition and anomaly detection
- **🛡️ Risk Assessment**: Automated threat scoring and priority ranking
- **📊 Interactive Dashboard**: Real-time visualization of intelligence data
- **⚡ Real-Time Processing**: Stream processing for live intelligence updates

---

## ✨ Features

### Phase 1: Foundation ✅
- [x] Project infrastructure and Docker setup
- [x] FastAPI backend with health checks
- [x] React + Vite frontend with Tailwind CSS
- [x] PostgreSQL, Neo4j, and Redis integration
- [x] Nginx reverse proxy configuration
- [x] Environment configuration system

### Phase 2: Core Intelligence (Upcoming)
- [ ] OSINT data collectors
- [ ] Data normalization engine
- [ ] Intelligence graph construction
- [ ] Basic risk scoring
- [ ] Report generation

### Phase 3: Advanced Features (Planned)
- [ ] AI/ML integration
- [ ] Real-time streaming
- [ ] Advanced visualization modes
- [ ] Multi-tenant support
- [ ] API marketplace

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.104+
- **Runtime**: Python 3.11+
- **Database**: PostgreSQL 15 (relational data)
- **Graph DB**: Neo4j 5.12 (relationships)
- **Cache**: Redis 7 (caching & queues)
- **Async**: Uvicorn with asyncio support

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite 5
- **Styling**: Tailwind CSS with dark cyber theme
- **Graph Visualization**: react-force-graph
- **Animations**: Framer Motion
- **HTTP Client**: Axios

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Nginx
- **Network**: Bridge network with service discovery

---

## 🚀 Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/reconvault/reconvault.git
cd reconvault

# Configure environment
cp .env.example .env

# Start all services
docker-compose up -d

# Wait for services to initialize (approx. 30 seconds)
docker-compose ps
```

### Access Services

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Neo4j Browser**: http://localhost:7474
- **Nginx Proxy**: http://localhost

### Verify Installation

```bash
# Check service health
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "service": "reconvault-backend",
#   "version": "0.1.0",
#   "message": "ReconVault API is operational"
# }
```

---

## 📚 Documentation

- [Architecture Overview](docs/architecture.md) - System design and technology choices
- [Ethics & Compliance](docs/ethics.md) - Our commitment to ethical OSINT
- [Usage Guide](docs/usage.md) - Development environment and troubleshooting

---

## 👥 Developers

### Core Team

| Name | Role | GitHub |
|------|------|--------|
| Simanchala Bisoyi | Lead Developer | [@simanchala](https://github.com/simanchala) |
| Subham Mohanty | Backend Engineer | [@subham](https://github.com/subham) |
| Abhinav Kumar | Frontend Engineer | [@abhinav](https://github.com/abhinav) |

---

## 🏗️ Project Structure

```
ReconVault/
├── frontend/              # React + Vite application
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── graph/         # Graph visualization
│   │   ├── services/      # API services
│   │   └── styles/        # Global styles
│   ├── public/            # Static assets
│   └── package.json
│
├── backend/               # FastAPI application
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── collectors/    # OSINT collectors
│   │   ├── normalization/ # Data normalization
│   │   ├── intelligence_graph/ # Graph logic
│   │   ├── media_osint/   # Social media OSINT
│   │   ├── ai_engine/     # Machine learning
│   │   ├── risk_engine/   # Risk assessment
│   │   ├── reverse_osint/ # Cross-referencing
│   │   ├── automation/    # Workflows
│   │   ├── ethics/        # Compliance module
│   │   ├── models/        # Data models
│   │   └── main.py        # Application entry
│   └── requirements.txt
│
├── database/              # Database configurations
│   ├── postgres/          # PostgreSQL setup
│   └── neo4j/             # Neo4j setup
│
├── nginx/                 # Nginx configuration
│   └── default.conf
│
├── docs/                  # Documentation
│   ├── architecture.md
│   ├── ethics.md
│   └── usage.md
│
├── docker-compose.yml     # Docker orchestration
├── .env.example           # Environment template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

---

## 🐳 Docker Deployment

### Services

| Service | Port | Description |
|---------|------|-------------|
| backend | 8000 | FastAPI application |
| frontend | 5173 | Vite dev server |
| postgres | 5432 | PostgreSQL database |
| neo4j | 7474, 7687 | Neo4j browser & bolt |
| redis | 6379 | Redis cache |
| nginx | 80, 443 | Reverse proxy |

### Docker Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild services
docker-compose up -d --build

# Check service status
docker-compose ps
```

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow existing code style and conventions
- Write meaningful commit messages
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚖️ Ethics & Compliance

ReconVault is committed to ethical cybersecurity practices:

- ✅ **Passive OSINT Only**: No active scanning or exploitation
- ✅ **robots.txt Compliance**: Respect web standards
- ✅ **Rate Limiting**: Prevent server overload
- ✅ **Privacy Protection**: Data minimization and secure storage

See [docs/ethics.md](docs/ethics.md) for our complete ethics policy.

---

## 🔐 Security

- 🔒 All data encrypted at rest
- 🔒 TLS encryption for all communications
- 🔒 Role-based access control (RBAC)
- 🔒 Comprehensive audit logging
- 🔒 Regular security audits

---

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/reconvault/reconvault/issues)
- **Discussions**: [GitHub Discussions](https://github.com/reconvault/reconvault/discussions)
- **Email**: support@reconvault.io

---

## 🗺️ Roadmap

### Q1 2024: Phase 1 ✅
- [x] Infrastructure setup
- [x] Basic API framework
- [x] Frontend scaffold
- [x] Database connections

### Q2 2024: Phase 2
- [ ] OSINT collectors
- [ ] Data normalization
- [ ] Graph construction
- [ ] Risk scoring engine

### Q3 2024: Phase 3
- [ ] AI/ML integration
- [ ] Advanced visualizations
- [ ] Real-time streaming
- [ ] Multi-tenant support

### Q4 2024: Production
- [ ] Security hardening
- [ ] Performance optimization
- [ ] Cloud deployment
- [ ] Mobile applications

---

<div align="center">

**Built with ❤️ for the cybersecurity community**

Made by Simanchala Bisoyi, Subham Mohanty, and Abhinav Kumar

[⬆ Back to Top](#reconvault)

</div>
