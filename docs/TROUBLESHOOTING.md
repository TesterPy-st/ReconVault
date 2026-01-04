# Troubleshooting

## Common Issues & Solutions

### Installation & Setup

#### Docker Compose Fails to Start

**Problem:**
```
ERROR: Couldn't connect to Docker daemon
```

**Solutions:**
1. Start Docker Desktop (Windows/Mac) or Docker service (Linux)
2. Check Docker is running: `docker ps`
3. Check Docker Compose version: `docker-compose --version` (minimum 2.0)
4. Restart Docker service:
   ```bash
   sudo systemctl restart docker  # Linux
   ```

#### Port Already in Use

**Problem:**
```
ERROR: for frontend  Bind for 0.0.0.0:5173 failed: port is already allocated
```

**Solutions:**
1. Find process using the port:
   ```bash
   lsof -i :5173  # Mac/Linux
   netstat -tuln | grep 5173  # Linux
   ```
2. Kill the process or change port in `docker-compose.yml`

#### Insufficient Memory

**Problem:**
Container crashes with OOM (Out of Memory) errors.

**Solutions:**
1. Increase Docker memory allocation (Docker Desktop → Settings → Resources)
2. Minimum: 8GB, Recommended: 16GB
3. Reduce concurrent workers in `.env`:
   ```bash
   CELERY_WORKER_CONCURRENCY=2  # Reduce from default
   ```

### Database Issues

#### PostgreSQL Connection Failed

**Problem:**
```
connection to server at "localhost", port 5432 failed
```

**Solutions:**
1. Check PostgreSQL container is running:
   ```bash
   docker-compose ps postgres
   ```
2. Check logs:
   ```bash
   docker-compose logs postgres
   ```
3. Restart PostgreSQL:
   ```bash
   docker-compose restart postgres
   ```
4. Wait for database to be ready (can take 30-60 seconds):
   ```bash
   docker-compose exec postgres pg_isready
   ```

#### Neo4j Connection Failed

**Problem:**
```
Failed to establish connection to Neo4j
```

**Solutions:**
1. Check Neo4j container:
   ```bash
   docker-compose ps neo4j
   docker-compose logs neo4j
   ```
2. Verify Neo4j is ready:
   ```bash
   curl http://localhost:7474
   ```
3. Reset Neo4j data (last resort):
   ```bash
   docker-compose down -v
   docker-compose up -d neo4j
   ```
4. Check `.env` credentials:
   ```bash
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_password
   ```

#### Redis Connection Failed

**Problem:**
```
Error connecting to Redis
```

**Solutions:**
1. Check Redis container:
   ```bash
   docker-compose ps redis
   docker-compose logs redis
   ```
2. Test connection:
   ```bash
   docker-compose exec redis redis-cli ping
   # Should return: PONG
   ```
3. Restart Redis:
   ```bash
   docker-compose restart redis
   ```

### Backend Issues

#### Backend API Not Responding

**Problem:**
```
curl: (7) Failed to connect to localhost port 8000
```

**Solutions:**
1. Check backend container:
   ```bash
   docker-compose ps backend
   docker-compose logs backend
   ```
2. Check health endpoint:
   ```bash
   curl http://localhost:8000/health
   ```
3. Restart backend:
   ```bash
   docker-compose restart backend
   ```
4. Check database connections in logs

#### Import Errors in Backend

**Problem:**
```
ModuleNotFoundError: No module named 'some_module'
```

**Solutions:**
1. Rebuild backend container:
   ```bash
   docker-compose up -d --build backend
   ```
2. Check `requirements.txt` includes all dependencies
3. For local development, reinstall:
   ```bash
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt
   ```

#### Database Migration Errors

**Problem:**
```
alembic.util.exc.CommandError: Target database is not up to date
```

**Solutions:**
1. Run migrations:
   ```bash
   docker-compose exec backend alembic upgrade head
   ```
2. Check migration status:
   ```bash
   docker-compose exec backend alembic current
   ```
3. Reset database (WARNING: deletes data):
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

### Frontend Issues

#### Frontend Won't Load

**Problem:**
Blank page or connection refused at http://localhost:5173

**Solutions:**
1. Check frontend container:
   ```bash
   docker-compose ps frontend
   docker-compose logs frontend
   ```
2. Restart frontend:
   ```bash
   docker-compose restart frontend
   ```
3. Clear browser cache and try incognito mode
4. Check CORS settings in `.env`:
   ```bash
   CORS_ORIGINS=http://localhost:5173
   ```

#### Build Errors in Frontend

**Problem:**
npm install or npm run build fails

**Solutions:**
1. Delete node_modules and reinstall:
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```
2. Clear Vite cache:
   ```bash
   rm -rf node_modules/.vite
   npm run dev
   ```
3. Check Node.js version (minimum 18):
   ```bash
   node --version
   ```

#### WebSocket Connection Fails

**Problem:**
Real-time updates not working

**Solutions:**
1. Check WebSocket URL in browser console
2. Verify backend WebSocket endpoint is accessible:
   ```bash
   curl -i -N -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     http://localhost:8000/ws
   ```
3. Check firewall settings
4. Restart backend to reinitialize WebSocket server

### Collection Issues

#### Collection Stuck or Hangs

**Problem:**
Collection shows "in_progress" but no progress

**Solutions:**
1. Check Celery workers:
   ```bash
   docker-compose ps
   # Look for celery_worker containers
   ```
2. Check Celery logs:
   ```bash
   docker-compose logs backend | grep celery
   ```
3. Restart Celery workers:
   ```bash
   docker-compose restart backend
   ```
4. Cancel collection via API:
   ```bash
   curl -X POST http://localhost:8000/api/v1/collection/{id}/cancel
   ```

#### Rate Limiting Errors

**Problem:**
```
429 Too Many Requests
```

**Solutions:**
1. Wait until rate limit resets (check `X-RateLimit-Reset` header)
2. Adjust rate limit in `.env`:
   ```bash
   RATE_LIMIT_PER_HOUR=2000  # Increase limit
   ```
3. Reduce collection concurrency
4. Use different target or wait longer between requests

#### Collector Fails with Timeout

**Problem:**
```
TimeoutError: Request timeout after 30 seconds
```

**Solutions:**
1. Increase timeout in collector configuration
2. Check network connectivity
3. Target may be blocking requests - verify robots.txt
4. Try running collector in isolation for debugging

### Performance Issues

#### Slow Graph Rendering

**Problem:**
Graph takes >10 seconds to render with many nodes

**Solutions:**
1. Limit number of nodes displayed:
   ```bash
   # Add filter in graph query
   GET /graph?limit=500
   ```
2. Enable graph optimization in frontend
3. Use graph filtering to show only relevant nodes
4. Consider using graph aggregation for large datasets

#### High Memory Usage

**Problem:**
Container uses excessive memory and slows down

**Solutions:**
1. Check memory usage:
   ```bash
   docker stats
   ```
2. Reduce worker concurrency:
   ```bash
   CELERY_WORKER_CONCURRENCY=2  # In .env
   ```
3. Reduce graph cache size
4. Restart containers to clear memory leaks

### API Issues

#### 404 Not Found

**Problem:**
API endpoint returns 404

**Solutions:**
1. Verify correct endpoint path and version:
   ```bash
   # Correct: /api/v1/targets
   # Wrong: /api/targets
   ```
2. Check API docs at http://localhost:8000/docs
3. Check backend logs for routing errors

#### 500 Internal Server Error

**Problem:**
API returns 500 error

**Solutions:**
1. Check backend logs:
   ```bash
   docker-compose logs backend --tail=100
   ```
2. Common causes:
   - Database connection failed
   - Missing environment variables
   - Invalid request data
3. Check `.env` configuration

#### CORS Errors

**Problem:**
Browser console shows CORS errors

**Solutions:**
1. Check CORS configuration in `.env`:
   ```bash
   CORS_ORIGINS=http://localhost:5173,http://localhost:3000
   ```
2. Restart backend after changing `.env`
3. Ensure frontend URL is in CORS origins list

### Development Issues

#### Virtual Environment Issues

**Problem:**
Python imports fail or venv is corrupted

**Solutions:**
1. Never manually edit venv files
2. Recreate venv if needed:
   ```bash
   cd backend
   rm -rf venv
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

#### Tests Failing

**Problem:**
pytest or npm test fails

**Solutions:**
1. Run tests with verbose output:
   ```bash
   cd backend
   pytest -v
   ```
2. Run single test file for debugging:
   ```bash
   pytest tests/test_specific.py -v
   ```
3. Check test database is configured
4. For frontend, ensure all dependencies installed:
   ```bash
   cd frontend
   npm install
   npm test
   ```

### Getting Help

If you can't resolve your issue:

1. **Check Documentation**
   - [Quick Start Guide](QUICK_START.md)
   - [API Reference](API.md)
   - [Development Guide](../DEVELOPMENT.md)

2. **Search Existing Issues**
   - [GitHub Issues](../../issues)
   - Search for similar problems

3. **Ask in Discussions**
   - [GitHub Discussions](../../discussions)
   - Describe your problem clearly
   - Include error messages and logs

4. **Create a New Issue**
   - Include environment details
   - Provide reproduction steps
   - Attach relevant logs
   - Include screenshots if applicable

## FAQ

### Q: How do I reset the entire system?
A:
```bash
docker-compose down -v  # Stop and remove all data
docker-compose up -d   # Start fresh
```

### Q: Can I use external databases?
A: Yes, configure connection strings in `.env`

### Q: How do I update to the latest version?
A:
```bash
git pull origin main
docker-compose down
docker-compose up -d --build
```

### Q: Where are logs stored?
A:
- Docker logs: `docker-compose logs [service]`
- Application logs: Check container filesystem
- Audit logs: Stored in PostgreSQL database

### Q: How do I backup my data?
A:
```bash
# PostgreSQL backup
docker-compose exec postgres pg_dump -U user dbname > backup.sql

# Neo4j backup
docker-compose exec neo4j neo4j-admin backup
```

### Q: What's the difference between /docs and /redoc?
A: Both show API documentation but with different interfaces. /docs (Swagger) is interactive, /redoc is cleaner for reading.
