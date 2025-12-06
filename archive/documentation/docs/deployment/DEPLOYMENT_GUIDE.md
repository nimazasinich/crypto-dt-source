# Deployment Guide - Crypto Resource Aggregator

## Quick Deployment to Hugging Face Spaces

### Method 1: Web Interface (Recommended for Beginners)

1. **Create a Hugging Face Account**
   - Go to https://huggingface.co/join
   - Sign up for a free account

2. **Create a New Space**
   - Go to https://huggingface.co/new-space
   - Choose a name (e.g., `crypto-resource-aggregator`)
   - Select SDK: **Docker**
   - Choose visibility: **Public** or **Private**
   - Click "Create Space"

3. **Upload Files**
   Upload the following files to your Space:
   - `app.py` - Main application file
   - `requirements.txt` - Python dependencies
   - `all_apis_merged_2025.json` - Resource configuration
   - `README.md` - Documentation
   - `Dockerfile` - Docker configuration

4. **Wait for Build**
   - The Space will automatically build and deploy
   - This may take 2-5 minutes
   - You'll see the build logs in real-time

5. **Access Your API**
   - Once deployed, your API will be available at:
     `https://[your-username]-[space-name].hf.space`
   - Example: `https://username-crypto-resource-aggregator.hf.space`

### Method 2: Git CLI (Recommended for Advanced Users)

```bash
# Clone your Space repository
git clone https://huggingface.co/spaces/[your-username]/[space-name]
cd [space-name]

# Copy all files to the repository
cp app.py requirements.txt all_apis_merged_2025.json README.md Dockerfile .

# Commit and push
git add .
git commit -m "Initial deployment of Crypto Resource Aggregator"
git push
```

---

## Alternative Deployment Options

### Option 1: Heroku

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Create a new app
heroku create crypto-resource-aggregator

# Create Procfile
echo "web: python app.py" > Procfile

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# Open your app
heroku open
```

### Option 2: Railway

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up

# Get deployment URL
railway domain
```

### Option 3: Render

1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Environment**: Python 3
5. Click "Create Web Service"

### Option 4: Docker (Self-Hosted)

```bash
# Build the Docker image
docker build -t crypto-aggregator .

# Run the container
docker run -d -p 7860:7860 --name crypto-aggregator crypto-aggregator

# Check logs
docker logs crypto-aggregator

# Stop the container
docker stop crypto-aggregator

# Remove the container
docker rm crypto-aggregator
```

### Option 5: Docker Compose (Self-Hosted)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  aggregator:
    build: .
    ports:
      - "7860:7860"
    restart: unless-stopped
    volumes:
      - ./history.db:/app/history.db
    environment:
      - ENVIRONMENT=production
```

Run:
```bash
docker-compose up -d
```

### Option 6: AWS EC2

```bash
# Connect to your EC2 instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Install Python and dependencies
sudo apt update
sudo apt install python3-pip python3-venv -y

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upload files (from local machine)
scp -i your-key.pem app.py requirements.txt all_apis_merged_2025.json ubuntu@your-instance-ip:~/

# Install dependencies
pip install -r requirements.txt

# Run with nohup
nohup python app.py > output.log 2>&1 &

# Or use systemd service (recommended)
sudo nano /etc/systemd/system/crypto-aggregator.service
```

Create systemd service file:
```ini
[Unit]
Description=Crypto Resource Aggregator
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/crypto-aggregator
ExecStart=/home/ubuntu/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable crypto-aggregator
sudo systemctl start crypto-aggregator
sudo systemctl status crypto-aggregator
```

### Option 7: Google Cloud Run

```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Build and deploy
gcloud run deploy crypto-aggregator \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Get URL
gcloud run services describe crypto-aggregator --region us-central1 --format 'value(status.url)'
```

### Option 8: DigitalOcean App Platform

1. Go to https://cloud.digitalocean.com/apps
2. Click "Create App"
3. Connect your GitHub repository
4. Configure:
   - **Run Command**: `python app.py`
   - **Environment**: Python 3.11
   - **HTTP Port**: 7860
5. Click "Deploy"

---

## Environment Variables (Optional)

You can configure the following environment variables:

```bash
# Port (default: 7860)
export PORT=8000

# Log level (default: INFO)
export LOG_LEVEL=DEBUG

# Database path (default: history.db)
export DATABASE_PATH=/path/to/history.db
```

---

## Post-Deployment Testing

### 1. Test Health Endpoint

```bash
curl https://your-deployment-url.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-10T...",
  "resources_loaded": true,
  "database_connected": true
}
```

### 2. Test Resource Listing

```bash
curl https://your-deployment-url.com/resources
```

### 3. Test Query Endpoint

```bash
curl -X POST https://your-deployment-url.com/query \
  -H "Content-Type: application/json" \
  -d '{
    "resource_type": "market_data",
    "resource_name": "coingecko",
    "endpoint": "/simple/price",
    "params": {
      "ids": "bitcoin",
      "vs_currencies": "usd"
    }
  }'
```

### 4. Test Status Monitoring

```bash
curl https://your-deployment-url.com/status
```

### 5. Run Full Test Suite

From your local machine:

```bash
# Update BASE_URL in test_aggregator.py
# Change: BASE_URL = "http://localhost:7860"
# To: BASE_URL = "https://your-deployment-url.com"

# Run tests
python test_aggregator.py
```

---

## Performance Optimization

### 1. Enable Caching

Add Redis for caching (optional):

```python
import redis
import json

# Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Cache resource data
def get_cached_data(key, ttl=300):
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    return None

def set_cached_data(key, data, ttl=300):
    redis_client.setex(key, ttl, json.dumps(data))
```

### 2. Use Connection Pooling

Already implemented with `aiohttp.ClientSession`

### 3. Add Rate Limiting

Install:
```bash
pip install slowapi
```

Add to `app.py`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/query")
@limiter.limit("60/minute")
async def query_resource(request: Request, query: ResourceQuery):
    # ... existing code
```

### 4. Add Monitoring

Use Sentry for error tracking:

```bash
pip install sentry-sdk
```

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)
```

---

## Security Best Practices

### 1. API Key Management

Store API keys in environment variables:

```python
import os

API_KEYS = {
    'etherscan': os.getenv('ETHERSCAN_API_KEY', 'default-key'),
    'coinmarketcap': os.getenv('CMC_API_KEY', 'default-key'),
}
```

### 2. Enable HTTPS

Most platforms (Hugging Face, Heroku, etc.) provide HTTPS by default.

For self-hosted, use Let's Encrypt:

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com
```

### 3. Add Authentication (Optional)

```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Security

security = HTTPBearer()

@app.post("/query")
async def query_resource(
    query: ResourceQuery,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    # Verify token
    if credentials.credentials != "your-secret-token":
        raise HTTPException(status_code=401, detail="Invalid token")
    # ... existing code
```

---

## Monitoring & Maintenance

### 1. Monitor Logs

Hugging Face Spaces:
- View logs in the Space settings → "Logs" tab

Docker:
```bash
docker logs -f crypto-aggregator
```

Systemd:
```bash
journalctl -u crypto-aggregator -f
```

### 2. Database Maintenance

Backup database regularly:

```bash
# Local backup
cp history.db history_backup_$(date +%Y%m%d).db

# Remote backup
scp user@server:/path/to/history.db ./backups/
```

Clean old records:

```sql
-- Remove records older than 30 days
DELETE FROM query_history WHERE timestamp < datetime('now', '-30 days');
DELETE FROM resource_status WHERE last_check < datetime('now', '-30 days');
```

### 3. Update Resources

To add new resources, update `all_apis_merged_2025.json` and redeploy.

### 4. Health Checks

Set up automated health checks:

```bash
# Cron job (every 5 minutes)
*/5 * * * * curl https://your-deployment-url.com/health || echo "API is down!"
```

Use UptimeRobot or similar service for monitoring.

---

## Troubleshooting

### Issue: Server won't start

**Solution:**
```bash
# Check if port 7860 is in use
lsof -i :7860

# Kill existing process
kill -9 $(lsof -t -i:7860)

# Or use a different port
PORT=8000 python app.py
```

### Issue: Database locked

**Solution:**
```bash
# Stop all instances
pkill -f app.py

# Remove lock (if exists)
rm history.db-journal

# Restart
python app.py
```

### Issue: High memory usage

**Solution:**
- Add connection limits
- Implement request queuing
- Scale horizontally with multiple instances

### Issue: API rate limits

**Solution:**
- Implement caching
- Add multiple API keys for rotation
- Use fallback resources

---

## Scaling

### Horizontal Scaling

Use a load balancer with multiple instances:

```yaml
# docker-compose-scaled.yml
version: '3.8'

services:
  aggregator:
    build: .
    deploy:
      replicas: 3
    environment:
      - WORKER_ID=${HOSTNAME}

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - aggregator
```

### Vertical Scaling

Increase resources on your hosting platform:
- Hugging Face: Upgrade to paid tier
- AWS: Use larger EC2 instance
- Docker: Adjust container resources

---

## Support

For issues or questions:
1. Check `/health` endpoint
2. Review application logs
3. Test individual resources with `/status`
4. Verify database with SQLite browser

---

## Next Steps

After deployment:

1. **Integrate with your main app** using the provided client examples
2. **Set up monitoring** with health checks and alerts
3. **Configure backups** for the history database
4. **Add custom resources** by updating the JSON file
5. **Implement caching** for frequently accessed data
6. **Enable authentication** if needed for security

---

**Congratulations! Your Crypto Resource Aggregator is now deployed and ready to use!** 🚀
