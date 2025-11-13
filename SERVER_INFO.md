# Server Entry Points

## Primary Production Server

**Use this for production deployments:**

```bash
python app.py
```

OR use the convenient launcher:

```bash
python start_server.py
```

**File:** `app.py`
- Production-ready FastAPI application
- Comprehensive monitoring and WebSocket support
- All features enabled (160+ API sources)
- Full database persistence
- Automated scheduling
- Rate limiting
- Health checks
- HuggingFace integration

## Server Access Points

Once started, access the application at:

- **Main Dashboard:** http://localhost:7860/
- **API Documentation:** http://localhost:7860/docs
- **Health Check:** http://localhost:7860/health

## Deprecated Server Files

The following server files are **deprecated** and kept only for backward compatibility:

- `simple_server.py` - Simple test server (use app.py instead)
- `enhanced_server.py` - Old enhanced version (use app.py instead)
- `real_server.py` - Old real data server (use app.py instead)
- `production_server.py` - Old production server (use app.py instead)

**Do not use these files for new deployments.**

## Docker Deployment

For Docker deployment, the Dockerfile already uses `app.py`:

```bash
docker build -t crypto-monitor .
docker run -p 7860:7860 crypto-monitor
```

## Development

For development with auto-reload:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 7860
```

## Configuration

1. Copy `.env.example` to `.env`
2. Add your API keys (optional, many sources work without keys)
3. Start the server

```bash
cp .env.example .env
python app.py
```
