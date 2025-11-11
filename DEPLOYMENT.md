# 🚀 Deployment Guide - Crypto API Monitoring System

Complete guide for deploying the Crypto API Monitoring System to various platforms.

---

## Table of Contents

1. [Hugging Face Spaces](#hugging-face-spaces)
2. [Docker Deployment](#docker-deployment)
3. [Docker Compose](#docker-compose-production)
4. [Cloud Platforms](#cloud-platforms)
5. [Environment Variables](#environment-variables)
6. [Troubleshooting](#troubleshooting)

---

## 🤗 Hugging Face Spaces

### Prerequisites
- Hugging Face account
- Git installed locally
- API keys for crypto services

### Step-by-Step Deployment

#### 1. Create New Space
```bash
# Login to Hugging Face
huggingface-cli login

# Clone this repository
git clone https://github.com/nimazasinich/crypto-dt-source.git
cd crypto-dt-source

# Create a new Space (or use web interface)
huggingface-cli repo create crypto-monitor --type space --space_sdk docker
```

#### 2. Configure Space Settings
In your Space settings on Hugging Face:
- **SDK**: Docker
- **Port**: 7860
- **Hardware**: CPU Basic (free) or CPU Upgrade (faster)

#### 3. Add Secrets (API Keys)
Go to **Settings → Repository Secrets** and add:

```
ETHERSCAN_KEY_1=your_etherscan_api_key
COINMARKETCAP_KEY_1=your_coinmarketcap_api_key
NEWSAPI_KEY=your_newsapi_key
BSCSCAN_KEY=your_bscscan_key (optional)
CRYPTOCOMPARE_KEY=your_cryptocompare_key (optional)
```

#### 4. Push to Hugging Face
```bash
# Add Hugging Face remote
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/crypto-monitor

# Ensure README has proper metadata
cp README_HUGGINGFACE.md README.md

# Push to HF
git add .
git commit -m "Initial deployment"
git push hf main
```

#### 5. Monitor Deployment
- Space will automatically build and deploy
- Check logs in the Space interface
- Access at: `https://huggingface.co/spaces/YOUR_USERNAME/crypto-monitor`

### Updating the Space
```bash
# Make changes
git add .
git commit -m "Update: description of changes"
git push hf main
```

---

## 🐳 Docker Deployment

### Quick Start

```bash
# 1. Build the image
docker build -t crypto-monitor:latest .

# 2. Run the container
docker run -d \
  --name crypto-monitor \
  -p 7860:7860 \
  -v crypto-data:/app/data \
  -v crypto-logs:/app/logs \
  -e ETHERSCAN_KEY_1=your_key \
  -e COINMARKETCAP_KEY_1=your_key \
  -e NEWSAPI_KEY=your_key \
  crypto-monitor:latest

# 3. Check logs
docker logs -f crypto-monitor

# 4. Access the application
# Open browser: http://localhost:7860
```

### Using Environment File

```bash
# 1. Create .env file
cp .env.example .env
# Edit .env with your API keys

# 2. Run with env file
docker run -d \
  --name crypto-monitor \
  -p 7860:7860 \
  -v $(pwd)/data:/app/data \
  --env-file .env \
  crypto-monitor:latest
```

### Production Build

```bash
# Multi-stage build for smaller image
docker build \
  --target production \
  --tag crypto-monitor:2.0.0 \
  --tag crypto-monitor:latest \
  .

# Push to registry (optional)
docker tag crypto-monitor:latest your-registry/crypto-monitor:latest
docker push your-registry/crypto-monitor:latest
```

---

## 🐳 Docker Compose (Production)

### Basic Setup

```bash
# 1. Prepare environment
cp .env.example .env
# Edit .env with your API keys

# 2. Start services
docker-compose up -d

# 3. Check status
docker-compose ps

# 4. View logs
docker-compose logs -f crypto-monitor

# 5. Access application
# http://localhost:7860
```

### With Nginx Proxy

```bash
# Start with Nginx
docker-compose --profile production up -d

# Access via Nginx
# http://localhost:80
```

### With Monitoring (Prometheus + Grafana)

```bash
# Start with monitoring stack
docker-compose --profile monitoring up -d

# Access services:
# - Main app: http://localhost:7860
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000 (admin/admin)
```

### With Redis Cache

```bash
# Start with Redis caching
docker-compose --profile with-cache up -d
```

### Management Commands

```bash
# Stop services
docker-compose down

# Stop and remove volumes (CAUTION: deletes data)
docker-compose down -v

# Restart a service
docker-compose restart crypto-monitor

# Scale workers (if configured)
docker-compose up -d --scale crypto-monitor=3

# Update and rebuild
docker-compose pull
docker-compose build --no-cache
docker-compose up -d

# View resource usage
docker-compose stats
```

---

## ☁️ Cloud Platforms

### AWS ECS (Elastic Container Service)

```bash
# 1. Install AWS CLI and configure
aws configure

# 2. Create ECR repository
aws ecr create-repository --repository-name crypto-monitor

# 3. Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# 4. Build and push
docker build -t crypto-monitor .
docker tag crypto-monitor:latest \
  YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/crypto-monitor:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/crypto-monitor:latest

# 5. Create ECS task definition
# Use AWS Console or CLI to create task

# 6. Deploy to ECS cluster
# Configure via AWS Console
```

### Google Cloud Run

```bash
# 1. Install gcloud CLI
gcloud init

# 2. Build and deploy
gcloud run deploy crypto-monitor \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 7860 \
  --set-env-vars ETHERSCAN_KEY_1=your_key,COINMARKETCAP_KEY_1=your_key

# 3. Access the URL provided
```

### Azure Container Instances

```bash
# 1. Install Azure CLI
az login

# 2. Create resource group
az group create --name crypto-monitor-rg --location eastus

# 3. Create container registry
az acr create --resource-group crypto-monitor-rg \
  --name cryptomonitoracr --sku Basic

# 4. Build and push
az acr build --registry cryptomonitoracr \
  --image crypto-monitor:latest .

# 5. Deploy container
az container create \
  --resource-group crypto-monitor-rg \
  --name crypto-monitor \
  --image cryptomonitoracr.azurecr.io/crypto-monitor:latest \
  --dns-name-label crypto-monitor \
  --ports 7860 \
  --environment-variables \
    ETHERSCAN_KEY_1=your_key \
    COINMARKETCAP_KEY_1=your_key
```

### DigitalOcean App Platform

```bash
# 1. Install doctl
snap install doctl

# 2. Authenticate
doctl auth init

# 3. Create app via web interface or:
doctl apps create --spec app-spec.yaml

# app-spec.yaml:
---
name: crypto-monitor
services:
- name: web
  github:
    repo: your-username/crypto-dt-source
    branch: main
  dockerfile_path: Dockerfile
  http_port: 7860
  envs:
  - key: ETHERSCAN_KEY_1
    value: your_key
    type: SECRET
```

---

## 🔐 Environment Variables

### Required Variables

```bash
# Blockchain Explorers
ETHERSCAN_KEY_1=your_etherscan_api_key

# Market Data
COINMARKETCAP_KEY_1=your_coinmarketcap_api_key

# News
NEWSAPI_KEY=your_newsapi_key
```

### Optional Variables

```bash
# Additional Explorers
BSCSCAN_KEY=your_bscscan_key
TRONSCAN_KEY=your_tronscan_key

# Enhanced Market Data
CRYPTOCOMPARE_KEY=your_cryptocompare_key

# AI/ML Features
HUGGINGFACE_KEY=your_huggingface_token

# Application Settings
APP_ENV=production
LOG_LEVEL=info
PORT=7860
WORKERS=1

# Database
DATABASE_PATH=data/api_monitor.db

# Features
ENABLE_WEBSOCKETS=true
ENABLE_METRICS=true
```

### How to Get API Keys

1. **Etherscan**: https://etherscan.io/myapikey
   - Free tier: 5 calls/second
   - Required for Ethereum blockchain data

2. **CoinMarketCap**: https://pro.coinmarketcap.com/signup
   - Free tier: 333 calls/day
   - Required for market cap data

3. **NewsAPI**: https://newsapi.org/register
   - Free tier: 100 requests/day
   - Required for crypto news

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Container Won't Start
```bash
# Check logs
docker logs crypto-monitor

# Common causes:
# - Missing required API keys
# - Port 7860 already in use
# - Permission issues with volumes

# Solutions:
lsof -i :7860  # Check what's using the port
sudo chown -R 1000:1000 data/  # Fix permissions
```

#### 2. Database Errors
```bash
# Reset database
docker-compose down -v
docker-compose up -d

# Or manually:
rm -rf data/api_monitor.db
docker-compose restart crypto-monitor
```

#### 3. WebSocket Connection Failed
```bash
# Check if WebSockets are enabled
# Verify nginx configuration if using proxy
# Check browser console for errors

# Test WebSocket directly:
wscat -c ws://localhost:7860/ws/live
```

#### 4. High Memory Usage
```bash
# Reduce workers
docker-compose down
# Edit docker-compose.yml: WORKERS=1
docker-compose up -d

# Set memory limits
docker update --memory 512m crypto-monitor
```

#### 5. API Rate Limits
```bash
# Check rate limit status
curl http://localhost:7860/api/rate-limits

# Wait for reset or add more API keys
# Multiple keys rotate automatically
```

### Health Checks

```bash
# Application health
curl http://localhost:7860/api/health

# System status
curl http://localhost:7860/api/status

# Provider status
curl http://localhost:7860/api/providers

# Docker health
docker inspect --format='{{.State.Health.Status}}' crypto-monitor
```

### Performance Tuning

```bash
# Adjust workers (in .env or docker-compose.yml)
WORKERS=2

# Increase connection pool
MAX_CONNECTIONS=200
POOL_SIZE=20

# Adjust timeouts
REQUEST_TIMEOUT=15
CONNECT_TIMEOUT=10

# Enable caching
ENABLE_CACHING=true
CACHE_TTL=300
```

---

## 📊 Monitoring

### Docker Stats
```bash
docker stats crypto-monitor
```

### Application Metrics
Access Prometheus: http://localhost:9090
Access Grafana: http://localhost:3000

### Logs
```bash
# Real-time logs
docker-compose logs -f crypto-monitor

# Last 100 lines
docker-compose logs --tail=100 crypto-monitor

# Logs for specific service
docker-compose logs nginx

# Save logs to file
docker-compose logs crypto-monitor > app.log 2>&1
```

---

## 🔄 Updates & Maintenance

### Updating the Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose build --no-cache
docker-compose up -d

# Or with minimal downtime:
docker-compose up -d --build
```

### Database Backup

```bash
# Backup database
docker cp crypto-monitor:/app/data/api_monitor.db ./backup_$(date +%Y%m%d).db

# Restore database
docker cp ./backup.db crypto-monitor:/app/data/api_monitor.db
docker-compose restart crypto-monitor
```

### Cleanup

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Full cleanup
docker system prune -a --volumes
```

---

## 📞 Support

- **GitHub Issues**: https://github.com/nimazasinich/crypto-dt-source/issues
- **Documentation**: See README.md
- **Email**: support@example.com

---

**Last Updated**: 2025-11-11
**Version**: 2.0.0
