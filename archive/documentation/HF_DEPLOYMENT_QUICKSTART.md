# 🚀 Quick Start: Deploy to Hugging Face Spaces

## ⚡ 5-Minute Deployment

### Step 1: Choose UI Mode (30 seconds)

**Windows:**
```powershell
.\deploy-to-hf.ps1
```

**Linux/Mac:**
```bash
chmod +x deploy-to-hf.sh
./deploy-to-hf.sh
```

Or manually edit `Dockerfile` lines 28-29:

**For Gradio UI (Recommended):**
```dockerfile
ENV USE_FASTAPI_HTML=false
ENV USE_GRADIO=true
```

**For FastAPI + HTML:**
```dockerfile
ENV USE_FASTAPI_HTML=true
ENV USE_GRADIO=false
```

### Step 2: Create Space (1 minute)

1. Go to: https://huggingface.co/new-space
2. Fill in:
   - **Name**: `crypto-intelligence-hub`
   - **SDK**: Docker
   - **Hardware**: CPU basic (free)
3. Click "Create Space"

### Step 3: Deploy (3 minutes)

```bash
# Clone your new space
git clone https://huggingface.co/spaces/YOUR_USERNAME/crypto-intelligence-hub
cd crypto-intelligence-hub

# Copy all files from your project
cp -r /path/to/your/project/* .

# Push to HF
git add .
git commit -m "Initial deployment"
git push
```

### Step 4: Wait & Test (2-5 minutes)

- Watch build logs on your Space page
- Wait for "Running" status
- Visit: `https://huggingface.co/spaces/YOUR_USERNAME/crypto-intelligence-hub`

## ✅ What's Already Fixed

- ✅ Docker image copies source code
- ✅ App fallback logic fixed (no more restart loops)
- ✅ Port 7860 configured correctly
- ✅ All dependencies in requirements_hf.txt
- ✅ README.md has HF Space metadata

## 🎯 What You Get

### Gradio Mode
- 📊 Interactive dashboard
- 📚 Resources browser
- 🤖 AI models viewer
- 💭 Sentiment analysis tool
- 🔌 API integration panel

### FastAPI Mode
- 🌐 REST API endpoints
- 📄 HTML frontend (index.html)
- 📖 Auto-generated docs (/docs)
- 🔍 API explorer (/redoc)

## 🔧 Optional: Add HF Token

For private models access:

1. Get token: https://huggingface.co/settings/tokens
2. Go to Space Settings → Repository secrets
3. Add: `HF_TOKEN` = your token

## 📊 Current Configuration

- **Port**: 7860 (HF Spaces standard)
- **Python**: 3.11
- **Default Mode**: FastAPI + HTML (change with script above)
- **Resources**: All JSON files included
- **Models**: Hugging Face Transformers

## 🐛 If Something Goes Wrong

### Build fails?
- Check Space logs
- Verify all files are pushed: `git status`

### App restarts?
- Already fixed! ✅
- Check logs for other errors

### Models not loading?
- Add HF_TOKEN to secrets
- Upgrade to GPU hardware

## 📞 Need Help?

- Full guide: `HUGGINGFACE_DEPLOYMENT.md`
- HF Docs: https://huggingface.co/docs/hub/spaces
- HF Community: https://discuss.huggingface.co/

---

**Ready to deploy? Run the script and follow the steps! 🚀**
