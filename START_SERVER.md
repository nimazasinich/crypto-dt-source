# 🚀 Starting the FastAPI Server

This guide explains how to run the Crypto Intelligence Hub FastAPI server using uvicorn on port 7860.

## Quick Start

### Method 1: Using Python directly (Recommended)
```bash
python main.py
```

### Method 2: Using the run script
```bash
python run_server.py
```

### Method 3: Using uvicorn directly
```bash
uvicorn main:app --host 0.0.0.0 --port 7860
```

## Configuration

### Port Configuration
The server runs on **port 7860** by default (Hugging Face Spaces standard).

You can change the port using environment variables:
```bash
# Windows
set PORT=8000
python main.py

# Linux/Mac
export PORT=8000
python main.py
```

Or for Hugging Face Spaces:
```bash
export HF_PORT=7860
python main.py
```

### Host Configuration
Default host is `0.0.0.0` (listens on all interfaces).

Change it with:
```bash
export HOST=127.0.0.1  # Only localhost
python main.py
```

### Development Mode (Auto-reload)
Enable auto-reload for development:
```bash
export DEBUG=true
python main.py
```

## Access Points

Once the server is running, you can access:

- **Main Dashboard**: http://localhost:7860/
- **API Documentation**: http://localhost:7860/docs
- **System Monitor**: http://localhost:7860/system-monitor
- **OpenAPI Schema**: http://localhost:7860/openapi.json

## Production Deployment

### Hugging Face Spaces
The server is configured to work with Hugging Face Spaces automatically:
- Port 7860 is the default
- Host 0.0.0.0 allows external access
- All optimizations are enabled

### Using Gunicorn (Alternative)
For production with multiple workers:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:7860
```

## Troubleshooting

### Port Already in Use
If port 7860 is already in use:
```bash
# Find what's using the port
# Windows
netstat -ano | findstr :7860

# Linux/Mac
lsof -i :7860

# Then use a different port
export PORT=8000
python main.py
```

### Module Not Found Errors
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Database Connection Issues
The server will continue to run even if database connections fail. Check logs for specific errors.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `7860` | Server port |
| `HF_PORT` | `7860` | Hugging Face Spaces port (fallback) |
| `HOST` | `0.0.0.0` | Server host |
| `DEBUG` | `false` | Enable auto-reload |

## Logs

The server logs to console with INFO level by default. You'll see:
- Server startup messages
- Router loading status
- Request logs (if access_log=True)
- Error messages

## Stopping the Server

Press `Ctrl+C` to gracefully stop the server.

## Next Steps

1. ✅ Server is running on port 7860
2. 📊 Open the dashboard at http://localhost:7860/
3. 📚 Check API docs at http://localhost:7860/docs
4. 🔍 Monitor system at http://localhost:7860/system-monitor

