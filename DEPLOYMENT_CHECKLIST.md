# ✅ Hugging Face Spaces Deployment Checklist

Use this checklist to track your deployment progress.

## Pre-Deployment

- [x] Docker restart loop fixed in `app.py`
- [x] Source code copying verified in `Dockerfile`
- [x] Port 7860 configured
- [x] Dependencies listed in `requirements_hf.txt`
- [x] README.md has HF Space metadata
- [ ] Choose UI mode (Gradio or FastAPI)

## UI Mode Selection

Choose one:

- [ ] **Gradio UI** (Interactive dashboard - recommended for demos)
  - Run: `.\deploy-to-hf.ps1` and select option 1
  - Or manually edit Dockerfile:
    ```dockerfile
    ENV USE_FASTAPI_HTML=false
    ENV USE_GRADIO=true
    ```

- [ ] **FastAPI + HTML** (REST API - current default)
  - Run: `.\deploy-to-hf.ps1` and select option 2
  - Or keep current Dockerfile settings:
    ```dockerfile
    ENV USE_FASTAPI_HTML=true
    ENV USE_GRADIO=false
    ```

## Create Hugging Face Space

- [ ] Go to https://huggingface.co/new-space
- [ ] Fill in Space details:
  - [ ] Space name: `crypto-intelligence-hub` (or your choice)
  - [ ] License: MIT
  - [ ] SDK: **Docker** (important!)
  - [ ] Hardware: CPU basic (free) or upgrade
- [ ] Click "Create Space"
- [ ] Copy your Space URL: `https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME`

## Deploy Code

- [ ] Clone your new Space:
  ```bash
  git clone https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME
  cd SPACE_NAME
  ```

- [ ] Copy project files:
  ```bash
  # Windows PowerShell
  Copy-Item -Recurse -Force C:\path\to\your\project\* .
  
  # Linux/Mac
  cp -r /path/to/your/project/* .
  ```

- [ ] Verify files copied:
  ```bash
  ls -la
  # Should see: Dockerfile, app.py, requirements_hf.txt, README.md, etc.
  ```

- [ ] Add and commit:
  ```bash
  git add .
  git commit -m "Initial deployment: Crypto Intelligence Hub"
  ```

- [ ] Push to HF Spaces:
  ```bash
  git push
  ```

## Monitor Deployment

- [ ] Go to your Space page
- [ ] Watch the "Building" logs
- [ ] Wait for status to change to "Running" (2-5 minutes)
- [ ] Check for any error messages in logs

## Test Deployed App

### For Gradio Mode:
- [ ] Visit your Space URL
- [ ] Test Dashboard tab
- [ ] Test Resources tab (should show data sources)
- [ ] Test AI Models tab (should show available models)
- [ ] Test Sentiment Analysis tab
- [ ] Try analyzing sample text

### For FastAPI Mode:
- [ ] Visit your Space URL (should show HTML frontend)
- [ ] Visit `/docs` endpoint (Swagger UI)
- [ ] Visit `/redoc` endpoint (ReDoc)
- [ ] Test API endpoints:
  - [ ] GET `/api/health`
  - [ ] GET `/api/resources`
  - [ ] POST `/api/hf/run-sentiment`

## Optional: Configure Secrets

If you need private model access:

- [ ] Get HF token from https://huggingface.co/settings/tokens
- [ ] Go to Space Settings → Repository secrets
- [ ] Add secret:
  - Name: `HF_TOKEN`
  - Value: your token
- [ ] Restart Space (if needed)

## Post-Deployment

- [ ] Update README.md with live demo link
- [ ] Share your Space on social media
- [ ] Monitor Space metrics and logs
- [ ] Collect user feedback
- [ ] Plan improvements

## Troubleshooting

If something goes wrong:

### Build Fails
- [ ] Check build logs for specific errors
- [ ] Verify all files are committed: `git status`
- [ ] Check Dockerfile syntax
- [ ] Verify requirements_hf.txt is complete

### App Doesn't Start
- [ ] Check runtime logs
- [ ] Verify port 7860 is used
- [ ] Check environment variables
- [ ] Verify JSON resource files exist

### Models Don't Load
- [ ] Add HF_TOKEN to secrets
- [ ] Check model names in ai_models.py
- [ ] Consider upgrading to GPU hardware
- [ ] Check model availability on HF Hub

### Performance Issues
- [ ] Upgrade Space hardware (Settings → Hardware)
- [ ] Optimize model loading
- [ ] Add caching
- [ ] Reduce concurrent requests

## Success Criteria

Your deployment is successful when:

- [x] Space status shows "Running"
- [ ] No errors in logs
- [ ] App loads in browser
- [ ] All features work as expected
- [ ] Models load successfully (if using AI features)
- [ ] API endpoints respond (if using FastAPI mode)

## Next Steps After Success

- [ ] Add custom domain (optional, paid feature)
- [ ] Enable analytics
- [ ] Set up monitoring
- [ ] Create documentation
- [ ] Promote your Space
- [ ] Iterate based on feedback

---

## Quick Reference

**Deployment Scripts:**
- Windows: `.\deploy-to-hf.ps1`
- Linux/Mac: `./deploy-to-hf.sh`

**Documentation:**
- Quick Start: `HF_DEPLOYMENT_QUICKSTART.md`
- Full Guide: `HUGGINGFACE_DEPLOYMENT.md`
- Status: `DEPLOYMENT_STATUS.md`

**Support:**
- HF Docs: https://huggingface.co/docs/hub/spaces
- HF Community: https://discuss.huggingface.co/

---

**Estimated Total Time:** 10-15 minutes

**Current Status:** Ready to deploy! 🚀
