# Troubleshooting Guide

Common issues and solutions for ReconVault.

## 🚨 Quick Fixes

Before diving into specific issues, try these general fixes:

1. **Restart services**: `docker-compose restart`
2. **Check logs**: `docker-compose logs [service]`
3. **Verify .env exists**: `cat .env`
4. **Check ports**: Ensure 5173, 8000, 5432, 7687, 6379 are free
5. **Update containers**: `docker-compose pull && docker-compose up -d`

## Frontend Issues

### 404 Error When Accessing Frontend

**Symptoms**: Browser shows "404 Not Found" at http://localhost:5173

**Causes**:
1. Missing `index.html` entry point
2. Vite not running properly
3. Wrong port configuration

**Solutions**:

```bash
# 1. Check if index.html exists
ls frontend/index.html

# 2. Check frontend logs
docker-compose logs frontend

# 3. Restart frontend
docker-compose restart frontend

# 4. Rebuild frontend
docker-compose build frontend --no-cache
docker-compose up -d frontend
```

**Manual fix** (if index.html is missing):
Create `frontend/index.html` with React entry point. See [Quick Start](QUICK_START.md).

### Frontend Won't Build

**Symptoms**: `npm run build` fails with errors

**Common causes**:
1. NPM dependency issues
2. Syntax errors in code
3. Missing dependencies

**Solutions**:

```bash
cd frontend

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Fix vulnerabilities
npm audit fix

# Check for syntax errors
npm run lint

# Try build again
npm run build
```

### White Screen / React Not Loading

**Symptoms**: Blank page, no errors in browser

**Causes**:
1. JavaScript errors preventing render
2. Missing CSS
3. API connection issues

**Solutions**:

1. **Check browser console** (F12) for errors
2. **Verify API connection**:
```bash
curl http://localhost:8000/health
```
3. **Check main.jsx and App.jsx** exist and export correctly
4. **Verify CSS imported**:
```bash
ls frontend/src/styles/main.css
```

### Graph Not Rendering

**Symptoms**: UI loads but graph canvas is empty or broken

**Causes**:
1. No data available
2. react-force-graph import issues
3. WebGL not supported

**Solutions**:

1. **Check graph data**:
```bash
curl http://localhost:8000/api/v1/graph
```

2. **Verify imports in GraphCanvas.jsx**:
```javascript
// CORRECT
import { ForceGraph2D } from 'react-force-graph';

// WRONG
import ForceGraph2D from 'react-force-graph-2d';
```

3. **Check WebGL support** in browser console:
```javascript
!!window.WebGLRenderingContext
```

## Backend Issues

### Backend Won't Start

**Symptoms**: Backend container exits immediately or shows errors

**Common causes**:
1. Database connection failure
2. Missing environment variables
3. Python dependency issues

**Solutions**:

```bash
# Check backend logs
docker-compose logs backend

# Verify environment
cat .env

# Rebuild backend
docker-compose build backend --no-cache

# Check Python dependencies
docker-compose exec backend pip list
```

### Database Connection Errors

**Symptoms**: Backend logs show "cannot connect to database"

**Solutions**:

```bash
# 1. Check PostgreSQL is running
docker-compose ps postgres

# 2. Test connection
docker-compose exec postgres psql -U reconvault -d reconvault

# 3. Verify credentials in .env match
cat .env | grep POSTGRES

# 4. Restart database
docker-compose restart postgres

# 5. Reset database (CAUTION: Deletes data)
docker-compose down -v
docker-compose up -d
```

### Neo4j Connection Issues

**Symptoms**: "Failed to connect to Neo4j" in logs

**Solutions**:

```bash
# 1. Check Neo4j is running
docker-compose ps neo4j

# 2. Access Neo4j browser
open http://localhost:7474

# 3. Verify credentials
# Username: neo4j
# Password: (from .env NEO4J_PASSWORD)

# 4. Check bolt connection
curl http://localhost:7687

# 5. Restart Neo4j
docker-compose restart neo4j
```

### API Returns 500 Errors

**Symptoms**: API calls return "Internal Server Error"

**Solutions**:

1. **Check backend logs**:
```bash
docker-compose logs backend --tail 100
```

2. **Verify database connection**:
```bash
curl http://localhost:8000/health
```

3. **Check specific endpoint**:
```bash
curl -v http://localhost:8000/api/v1/targets
```

4. **Restart backend**:
```bash
docker-compose restart backend
```

## Integration Issues

### CORS Errors

**Symptoms**: Browser console shows "CORS policy" errors

**Causes**: Frontend origin not allowed in backend CORS settings

**Solution**:

Update `.env`:
```bash
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

Restart backend:
```bash
docker-compose restart backend
```

### WebSocket Connection Fails

**Symptoms**: "WebSocket connection failed" in console

**Solutions**:

1. **Check WebSocket endpoint**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onopen = () => console.log('Connected');
```

2. **Verify backend WebSocket support**:
```bash
docker-compose logs backend | grep websocket
```

3. **Check firewall/proxy** not blocking WebSocket

### API Calls Return 404

**Symptoms**: Frontend requests to `/api/v1/*` return 404

**Causes**:
1. Backend not running
2. Wrong API URL
3. Route not registered

**Solutions**:

```bash
# 1. Test backend directly
curl http://localhost:8000/api/v1/targets

# 2. Check backend routes
curl http://localhost:8000/docs

# 3. Verify proxy in vite.config.js
cat frontend/vite.config.js

# 4. Check API service URL
grep -r "baseURL" frontend/src/services/
```

## Docker Issues

### Services Won't Start

**Symptoms**: `docker-compose up` fails

**Solutions**:

```bash
# 1. Check Docker is running
docker ps

# 2. Check docker-compose.yml syntax
docker-compose config

# 3. Remove old containers
docker-compose down -v

# 4. Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d

# 5. Check disk space
df -h
```

### Port Already in Use

**Symptoms**: "port is already allocated" error

**Solutions**:

```bash
# Find process using port
lsof -i :5173
lsof -i :8000
lsof -i :5432

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Container Keeps Restarting

**Symptoms**: Container status shows "Restarting"

**Solutions**:

```bash
# Check logs
docker-compose logs <service>

# Check resource limits
docker stats

# Remove and recreate
docker-compose rm -f <service>
docker-compose up -d <service>
```

## Collector Issues

### Dark Web Collector Fails

**Symptoms**: Tor-based collections fail

**Cause**: Tor proxy not configured

**Solution**:

1. **Install and start Tor**:
```bash
# Ubuntu/Debian
sudo apt-get install tor
sudo systemctl start tor

# macOS
brew install tor
brew services start tor
```

2. **Configure in .env**:
```bash
TOR_PROXY=socks5h://localhost:9050
```

### Social Media Collectors Fail

**Symptoms**: Twitter/social collections return errors

**Cause**: Missing API keys

**Solution**:

Add API keys to `.env`:
```bash
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
GITHUB_TOKEN=your_token
```

### Rate Limiting Issues

**Symptoms**: "Rate limit exceeded" errors

**Solutions**:

1. **Increase delays** in collector config
2. **Use multiple API keys** (rotate)
3. **Reduce concurrent collectors**
4. **Check rate limit status**:
```bash
curl http://localhost:8000/api/v1/compliance/rate-limits
```

## Performance Issues

### Slow Graph Rendering

**Symptoms**: Graph takes long to render or is laggy

**Solutions**:

1. **Reduce node count**: Apply filters
2. **Disable physics** temporarily in graph settings
3. **Increase browser resources**
4. **Use performance mode** in graph controls

### High Memory Usage

**Symptoms**: Docker containers using too much RAM

**Solutions**:

```bash
# Check memory usage
docker stats

# Increase Docker memory limit (Docker Desktop settings)
# Or reduce resource usage in docker-compose.yml

# Restart services
docker-compose restart
```

### Slow API Responses

**Symptoms**: API calls take >5 seconds

**Solutions**:

1. **Check database indexes**
2. **Enable Redis caching**
3. **Reduce query complexity**
4. **Scale backend horizontally**

## Development Issues

### Hot Reload Not Working

**Symptoms**: Code changes don't appear in browser

**Solutions**:

```bash
# Frontend
cd frontend
npm run dev  # Restart dev server

# Backend
docker-compose restart backend
# Or run with --reload flag
uvicorn app.main:app --reload
```

### Tests Failing

**Symptoms**: `pytest` or `npm test` show failures

**Solutions**:

```bash
# Backend
cd backend
pytest -v  # Verbose output
pytest --lf  # Run only failed tests
pytest --pdb  # Debug on failure

# Frontend
cd frontend
npm test -- --verbose
npm run test:watch  # Watch mode
```

### Import Errors

**Symptoms**: "ModuleNotFoundError" or "Cannot find module"

**Solutions**:

```bash
# Backend
pip install -r requirements.txt

# Frontend
npm install

# Check import paths
# Backend: from app.services.target_service import ...
# Frontend: import { api } from '@/services/api';
```

## Common Error Messages

### "ExifTool not found"

**Issue**: Old package name in requirements.txt

**Fix**: Use `piexif` instead of `ExifTool`

### "react-force-graph-2d not found"

**Issue**: Wrong import path

**Fix**: Import from `react-force-graph` not submodule

### "Cannot read property of undefined"

**Issue**: Accessing property on null/undefined object

**Fix**: Add null checks:
```javascript
const value = data?.property ?? 'default';
```

### "OperationalError: database is locked"

**Issue**: SQLite concurrent access (if using SQLite)

**Fix**: Use PostgreSQL in production (already configured)

## Still Having Issues?

If none of these solutions work:

1. **Check GitHub Issues**: Someone may have reported the same problem
2. **Enable Debug Mode**: Set `DEBUG=true` in `.env`
3. **Collect Full Logs**: `docker-compose logs > logs.txt`
4. **Open an Issue**: Include logs, steps to reproduce, environment details

### Useful Debug Commands

```bash
# Full system status
docker-compose ps
docker stats --no-stream

# All logs
docker-compose logs --tail 100

# Specific service logs
docker-compose logs backend --follow
docker-compose logs frontend --follow

# Network connectivity
docker network ls
docker network inspect reconvault_default

# Container shell access
docker-compose exec backend bash
docker-compose exec frontend sh

# Database access
docker-compose exec postgres psql -U reconvault
docker-compose exec neo4j cypher-shell -u neo4j
```

---

**Still stuck?** Open an issue on GitHub with:
- Error messages
- Steps to reproduce
- Environment details
- Relevant logs

We'll help you get it working!
