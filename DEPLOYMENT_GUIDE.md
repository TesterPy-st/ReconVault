# ReconVault Deployment Guide

This guide provides instructions for deploying ReconVault in different environments.

## Prerequisites
- Docker and Docker Compose
- Minimum 4GB RAM (8GB recommended for Neo4j and AI models)
- External API keys (see [API_KEYS_REFERENCE.md](API_KEYS_REFERENCE.md))

## Local Development
1. Clone the repository.
2. Copy `.env.example` to `.env` and configure your API keys.
3. Start the services:
   ```bash
   docker-compose up -d
   ```
4. Access the frontend at `http://localhost:5173` and the API at `http://localhost:8000`.

## Production Deployment

### 1. Server Preparation
Ensure your server meets the resource requirements. Ubuntu 22.04 LTS is recommended.

### 2. Security Hardening
- **Change Default Passwords**: Update `POSTGRES_PASSWORD`, `NEO4J_PASSWORD`, and `REDIS_PASSWORD` in your `.env` file.
- **Set a Secret Key**: Change the `SECRET_KEY` for JWT signing.
- **Configure Nginx SSL**: Update `nginx/default.conf` to include SSL certificates (e.g., via Let's Encrypt).

### 3. Database Setup
- **PostgreSQL**: The database schema is initialized automatically.
- **Neo4j**: Ensure the plugins (APOC, Graph Data Science) are correctly mounted in the `neo4j` service.

### 4. Deployment with Docker Compose
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```
(Note: You may need to create a `docker-compose.prod.yml` for specific production overrides).

### 5. Scaling
- **Celery Workers**: Scale the number of workers for parallel collection tasks:
  ```bash
  docker-compose up -d --scale worker=3
  ```
- **Redis**: For high availability, consider using a managed Redis service.

## Monitoring
- **Logs**: Monitor service logs using `docker logs -f reconvault-backend`.
- **Health Checks**: The system provides health endpoints at `/health` and `/health/detailed`.

## Troubleshooting
- **Database Connection Issues**: Ensure the containers are in the same network and hostnames match the service names in `docker-compose.yml`.
- **Neo4j Memory Issues**: Adjust `NEO4J_dbms_memory_heap_max__size` in the environment configuration if the container crashes.
- **Tor Connection**: Dark web collection requires Tor to be running on the host or in a separate container accessible to the worker.
