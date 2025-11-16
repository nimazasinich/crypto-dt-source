# Docker Deployment Guide

This guide explains how to run the Crypto Data Aggregator using Docker and Docker Compose.

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 2GB RAM available
- At least 5GB disk space

## 🏗️ Architecture

The application consists of two main services:

1. **crypto-api** (Port 8000) - FastAPI backend server
   - Lightweight API server
   - No Gradio, Plotly, or Transformers
   - Minimal dependencies

2. **crypto-dashboard** (Port 7860) - Gradio web dashboard
   - Full web UI with charts
   - Includes Plotly for visualizations
   - Optional AI features with Transformers
   - Depends on crypto-api

## 🚀 Quick Start

### Option 1: Run Both Services (Recommended)

```bash
# Start both API and Dashboard
docker-compose up -d

# View logs
docker-compose logs -f

# Access services
# - Dashboard: http://localhost:7860
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Option 2: Run API Server Only

```bash
# Start only the API server (lightweight)
docker-compose up -d crypto-api

# Access API at http://localhost:8000
```

### Option 3: Run Dashboard Only

```bash
# Start only the dashboard (requires API)
docker-compose up -d crypto-dashboard

# Access Dashboard at http://localhost:7860
```

## 📦 Docker Images

### Dockerfile (API Server)
- Base: `python:3.10-slim`
- Size: ~300MB
- Dependencies: Core requirements only
- Optional: Can install Gradio deps with build arg

**Build manually:**
```bash
# API only
docker build -t crypto-monitor-api .

# API with Gradio support
docker build -t crypto-monitor-api --build-arg INSTALL_GRADIO=true .
```

### Dockerfile.gradio (Dashboard)
- Base: `python:3.10-slim`
- Size: ~2-3GB (includes ML libraries)
- Dependencies: Full requirements + gradio + plotly + transformers

**Build manually:**
```bash
docker build -f Dockerfile.gradio -t crypto-monitor-dashboard .
```

## ⚙️ Configuration

### Environment Variables

#### API Server (`crypto-api`)
```yaml
HOST: 0.0.0.0                    # Server host
PORT: 8000                       # Server port
LOG_LEVEL: INFO                  # Logging level (DEBUG, INFO, WARNING, ERROR)
ENABLE_AUTO_DISCOVERY: false     # Auto-discover API providers
```

#### Dashboard (`crypto-dashboard`)
```yaml
PYTHONUNBUFFERED: 1              # Python output buffering
LOG_LEVEL: INFO                  # Logging level
GRADIO_SERVER_NAME: 0.0.0.0      # Gradio server host
GRADIO_SERVER_PORT: 7860         # Gradio server port
GRADIO_SHARE: false              # Create public Gradio link
```

### Volumes

Both services mount the same volumes for data persistence:

```yaml
volumes:
  - ./logs:/app/logs        # Application logs
  - ./data:/app/data        # Database and cached data
```

## 🔧 Common Commands

### Start Services
```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d crypto-api
docker-compose up -d crypto-dashboard
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop specific service
docker-compose stop crypto-api
docker-compose stop crypto-dashboard
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f crypto-api
docker-compose logs -f crypto-dashboard

# Last 100 lines
docker-compose logs --tail=100
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart crypto-api
docker-compose restart crypto-dashboard
```

### Rebuild Images
```bash
# Rebuild all images
docker-compose build

# Rebuild specific service
docker-compose build crypto-api
docker-compose build crypto-dashboard

# Rebuild without cache
docker-compose build --no-cache
```

### Enter Container Shell
```bash
# API container
docker exec -it crypto-monitor-api bash

# Dashboard container
docker exec -it crypto-monitor-dashboard bash
```

## 🏥 Health Checks

Both services include health checks:

**API Server:**
- Endpoint: `http://localhost:8000/health`
- Interval: 30s
- Timeout: 10s
- Start period: 10s

**Dashboard:**
- Endpoint: `http://localhost:7860`
- Interval: 30s
- Timeout: 10s
- Start period: 40s (longer due to ML library loading)

Check health status:
```bash
docker-compose ps
```

## 📊 Optional Services

The docker-compose file includes optional observability services:

### Enable All Optional Services
```bash
docker-compose --profile observability up -d
```

### Available Optional Services

1. **Redis** (Port 6379) - Caching
2. **PostgreSQL** (Port 5432) - Database
3. **Prometheus** (Port 9090) - Metrics
4. **Grafana** (Port 3000) - Dashboards

## 🔍 Troubleshooting

### Dashboard Won't Start

**Issue:** Container exits immediately

**Check logs:**
```bash
docker-compose logs crypto-dashboard
```

**Common causes:**
1. Missing dependencies (gradio, plotly)
   - Solution: Rebuild image `docker-compose build crypto-dashboard`

2. Port already in use
   - Solution: Change port in docker-compose.yml

3. Out of memory
   - Solution: Increase Docker memory limit (Settings > Resources)

### API Server Errors

**Issue:** AttributeError: module 'utils' has no attribute 'setup_logging'

**Solution:** This is fixed in the latest code. Rebuild:
```bash
docker-compose build --no-cache crypto-api
docker-compose up -d crypto-api
```

### Dependency Verification

Check which dependencies are installed:
```bash
# In API container
docker exec -it crypto-monitor-api pip list | grep -E "(gradio|plotly|transformers)"

# In Dashboard container
docker exec -it crypto-monitor-dashboard pip list | grep -E "(gradio|plotly|transformers)"
```

Expected output for Dashboard:
```
gradio         4.12.0
plotly         5.18.0
transformers   4.36.0 (or similar)
torch          2.x.x (optional)
```

### Check Application Status

```bash
# Check if services are running
docker-compose ps

# Check resource usage
docker stats

# Check container health
docker inspect crypto-monitor-api | grep Health
docker inspect crypto-monitor-dashboard | grep Health
```

## 🔐 Security Notes

1. **Change default passwords** in docker-compose.yml:
   - PostgreSQL: `POSTGRES_PASSWORD`
   - Grafana: `GF_SECURITY_ADMIN_PASSWORD`

2. **Use secrets** for production:
   ```yaml
   secrets:
     db_password:
       file: ./secrets/db_password.txt
   ```

3. **Limit exposed ports** - Only expose necessary ports in production

4. **Use reverse proxy** (nginx) for SSL/TLS termination

## 📝 Production Deployment

For production deployment:

1. **Use specific image tags** instead of `latest`
2. **Configure resource limits**:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2'
         memory: 2G
       reservations:
         cpus: '1'
         memory: 1G
   ```

3. **Set up monitoring** with Prometheus + Grafana
4. **Configure log rotation**
5. **Use external database** (PostgreSQL instead of SQLite)
6. **Set up backups** for data volumes

## 🆘 Getting Help

If you encounter issues:

1. Check logs: `docker-compose logs -f`
2. Verify dependencies: See "Dependency Verification" above
3. Rebuild images: `docker-compose build --no-cache`
4. Check health: `docker-compose ps`
5. Review: `DEPENDENCY_FIX_SUMMARY.md` for dependency issues

## 📚 Related Documentation

- `DEPENDENCY_FIX_SUMMARY.md` - Dependency installation and troubleshooting
- `README.md` - Main application documentation
- `requirements.txt` - Core API dependencies
- `requirements_gradio.txt` - Dashboard dependencies with Plotly & Transformers
