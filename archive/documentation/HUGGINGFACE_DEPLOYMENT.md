# 🚀 Hugging Face Spaces Deployment Guide

## Quick Deployment Steps

### 1. Prepare Your Repository

Your repository is already configured with:
- ✅ `README.md` with HF Space metadata
- ✅ `Dockerfile` with proper configuration
- ✅ `requirements_hf.txt` with all dependencies
- ✅ `app.py` with fixed fallback logic

### 2. Choose Your UI Mode

Edit the `Dockerfile` environment variables (lines 28-29):

**Option A: Gradio UI (Recommended for HF Spaces)**
```dockerfile
ENV USE_FASTAPI_HTML=false
ENV USE_GRADIO=true
```

**Option B: FastAPI + HTML (Current Default)**
```dockerfile
ENV USE_FASTAPI_HTML=true
ENV USE_GRADIO=false
```

### 3. Create a New Space on Hugging Face

1. Go to https://huggingface.co/new-space
2. Fill in the details:
   - **Space name**: `crypto-intelligence-hub` (or your choice)
   - **License**: MIT
   - **Select SDK**: Docker
   - **Space hardware**: CPU basic (free) or upgrade for better performance
3. Click "Create Space"

### 4. Push Your Code to the Space

**Method 1: Git Push (Recommended)**

```bash
# Clone your new space
git clone https://huggingface.co/spaces/YOUR_USERNAME/crypto-intelligence-hub
cd crypto-intelligence-hub

# Copy your files (from your project directory)
cp -r /path/to/your/project/* .

# Add and commit
git add .
git commit -m "Initial deployment"

# Push to HF Spaces
git push
```

**Method 2: Upload via Web Interface**

1. Go to your Space's "Files" tab
2. Click "Add file" → "Upload files"
3. Upload all project files
4. Commit the changes

### 5. Configure Environment Variables (Optional)

If you need Hugging Face API access for private models:

1. Go to your Space's "Settings" tab
2. Scroll to "Repository secrets"
3. Add:
   - **Name**: `HF_TOKEN`
   - **Value**: Your Hugging Face token (from https://huggingface.co/settings/tokens)

### 6. Monitor Deployment

1. Go to your Space's main page
2. Watch the "Building" logs
3. Wait for "Running" status (usually 2-5 minutes)
4. Your app will be available at: `https://huggingface.co/spaces/YOUR_USERNAME/crypto-intelligence-hub`

## 🔧 Configuration Options

### Port Configuration

Hugging Face Spaces expects apps to run on port **7860** (already configured in Dockerfile).

### Memory and CPU

- **Free tier**: 16GB RAM, 2 CPU cores
- **Upgrade options**: Available in Space settings for better performance

### Persistent Storage

HF Spaces provides ephemeral storage. For persistent data:
- Use HF Datasets for data storage
- Use external databases (PostgreSQL, MongoDB, etc.)
- Use cloud storage (S3, GCS, etc.)

## 🐛 Troubleshooting

### Build Fails

**Check logs for:**
- Missing dependencies in `requirements_hf.txt`
- Dockerfile syntax errors
- File permission issues

**Common fixes:**
```bash
# Ensure all files are committed
git status
git add .
git commit -m "Fix: Add missing files"
git push
```

### Container Restarts

**Fixed in this version!** The app now:
- ✅ Only uses `fastapi_app` when available
- ✅ Exits cleanly with error message if no UI mode is available
- ✅ No more restart loops

### App Not Loading

1. Check Space logs for errors
2. Verify port 7860 is exposed and used
3. Ensure `CMD ["python", "app.py"]` is in Dockerfile
4. Check that required JSON files exist in `api-resources/`

### Models Not Loading

If Hugging Face models fail to load:
1. Add `HF_TOKEN` to Space secrets
2. Increase Space hardware (CPU → GPU)
3. Check model availability and permissions

## 📊 Performance Optimization

### For Gradio Mode

```python
# In app.py, adjust Gradio launch settings:
app.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=False,
    show_error=True,
    max_threads=10  # Adjust based on hardware
)
```

### For FastAPI Mode

```python
# In app.py, adjust uvicorn settings:
uvicorn.run(
    fastapi_app,
    host="0.0.0.0",
    port=7860,
    log_level="info",
    workers=1  # Single worker for free tier
)
```

## 🔄 Updating Your Space

```bash
# Make changes locally
git add .
git commit -m "Update: Description of changes"
git push

# HF Spaces will automatically rebuild
```

## 📝 Recommended README.md Updates

Your current README.md is good! Consider adding:

```markdown
## 🌐 Live Demo

Try it now: [https://huggingface.co/spaces/YOUR_USERNAME/crypto-intelligence-hub](https://huggingface.co/spaces/YOUR_USERNAME/crypto-intelligence-hub)
```

## ✅ Pre-Deployment Checklist

- [x] Dockerfile copies source code (`COPY . .`)
- [x] app.py has fixed fallback logic
- [x] requirements_hf.txt includes all dependencies
- [x] README.md has HF Space metadata
- [x] Port 7860 is exposed and used
- [x] Environment variables are set correctly
- [ ] Choose UI mode (Gradio or FastAPI)
- [ ] Test locally with Docker (optional)
- [ ] Create HF Space
- [ ] Push code to HF Space
- [ ] Monitor build logs
- [ ] Test deployed app

## 🎯 Next Steps After Deployment

1. **Test all features**: Dashboard, Resources, Models, Sentiment Analysis
2. **Monitor performance**: Check Space metrics
3. **Share your Space**: Add to your profile, share on social media
4. **Iterate**: Update based on user feedback

## 📞 Support

- **HF Spaces Docs**: https://huggingface.co/docs/hub/spaces
- **HF Community**: https://discuss.huggingface.co/
- **Docker Docs**: https://docs.docker.com/

---

**Your app is ready to deploy! 🚀**
