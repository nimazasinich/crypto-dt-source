# Quick Start - GitHub & HuggingFace Synchronization

## 🚀 Get Started in 5 Minutes

This guide will help you set up and run the GitHub and HuggingFace synchronization system.

---

## 1️⃣ Configure Environment

```bash
# Copy example environment file
cp .env.sync.example .env

# Edit with your values
nano .env
```

**Minimum Required:**
```bash
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_REPO=owner/repository
HF_API_KEY=your_huggingface_api_key  # Optional but recommended
```

**Get Your Tokens:**
- **GitHub Token**: https://github.com/settings/tokens (requires `repo` scope)
- **HuggingFace Token**: https://huggingface.co/settings/tokens

---

## 2️⃣ Start the Server

```bash
# Run the API server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     ✅ Unified Service API Server initialized
```

---

## 3️⃣ Run Your First Sync

### Option A: Using REST API

```bash
# Trigger sync (runs in background)
curl -X POST "http://localhost:8000/api/v1/sync/run" \
  -H "Content-Type: application/json" \
  -d '{"branch": "main", "commit_message": "Sync update"}'

# Check status
curl "http://localhost:8000/api/v1/sync/status"

# View latest report
curl "http://localhost:8000/api/v1/sync/reports/latest" -o report.txt
cat report.txt
```

### Option B: Using CLI

```bash
# Complete sync with database update
python sync_cli.py sync --branch main --update-db

# View sync history
python sync_cli.py history --limit 5
```

---

## 4️⃣ View Results

### Check Sync Status

```bash
curl "http://localhost:8000/api/v1/sync/status"
```

Expected response:
```json
{
  "success": true,
  "status": {
    "is_running": false,
    "last_sync": "2025-11-27T12:00:00",
    "last_result": {
      "success": true,
      "duration": 45.23,
      "summary": {
        "github_commits_fetched": 5,
        "hf_models_synced": 4,
        "hf_datasets_synced": 5
      }
    }
  }
}
```

### Get Synced Models

```bash
curl "http://localhost:8000/api/v1/sync/database/models"
```

### Get Synced Datasets

```bash
curl "http://localhost:8000/api/v1/sync/database/datasets"
```

---

## 5️⃣ View Documentation

Open your browser:
- **Swagger UI**: http://localhost:8000/docs
- **Root Info**: http://localhost:8000/

---

## 📊 What Gets Synchronized?

### GitHub
- ✅ Latest commits from your repository
- ✅ Pull changes from remote
- ✅ Push local changes back

### HuggingFace Models
- ✅ `ElKulako/cryptobert`
- ✅ `kk08/CryptoBERT`
- ✅ `ProsusAI/finbert`
- ✅ `cardiffnlp/twitter-roberta-base-sentiment`

### HuggingFace Datasets
- ✅ `linxy/CryptoCoin`
- ✅ `WinkingFace/CryptoLM-Bitcoin-BTC-USDT`
- ✅ `WinkingFace/CryptoLM-Ethereum-ETH-USDT`
- ✅ `WinkingFace/CryptoLM-Solana-SOL-USDT`
- ✅ `WinkingFace/CryptoLM-Ripple-XRP-USDT`

---

## 🔧 Common Commands

### API Commands

```bash
# Get GitHub commits
curl "http://localhost:8000/api/v1/sync/github/commits?branch=main&limit=10"

# Get HuggingFace models info
curl "http://localhost:8000/api/v1/sync/hf/models"

# Get HuggingFace datasets info
curl "http://localhost:8000/api/v1/sync/hf/datasets"

# Get sync history
curl "http://localhost:8000/api/v1/sync/history?limit=10"

# List all reports
curl "http://localhost:8000/api/v1/sync/reports"
```

### CLI Commands

```bash
# Complete sync
python sync_cli.py sync --branch main --message "Update" --update-db

# GitHub only
python sync_cli.py github --branch main

# HuggingFace only
python sync_cli.py hf --update-db

# View GitHub commits
python sync_cli.py commits --branch main --limit 10

# View HuggingFace models
python sync_cli.py models

# View sync history
python sync_cli.py history --limit 10
```

---

## 📝 Example Workflow

### Daily Sync Routine

```bash
# 1. Run complete sync
curl -X POST "http://localhost:8000/api/v1/sync/run" \
  -H "Content-Type: application/json" \
  -d '{"branch": "main", "commit_message": "Daily sync"}'

# 2. Wait a moment for background task
sleep 10

# 3. Check status
curl "http://localhost:8000/api/v1/sync/status"

# 4. Download report
curl "http://localhost:8000/api/v1/sync/reports/latest" -o daily_report.txt

# 5. View synced models
curl "http://localhost:8000/api/v1/sync/database/models"
```

### Automated Sync (Cron)

```bash
# Add to crontab for hourly sync
crontab -e

# Add this line:
0 * * * * cd /workspace && python sync_cli.py sync --update-db > /tmp/sync.log 2>&1
```

---

## 🔍 Troubleshooting

### "GitHub API error"

**Problem**: GitHub token not set or invalid

**Solution**:
```bash
# Check token is set
echo $GITHUB_TOKEN

# If not, add to .env
echo "GITHUB_TOKEN=your_token_here" >> .env
```

### "Git pull failed"

**Problem**: Local changes conflict with remote

**Solution**:
```bash
cd /workspace
git status
git stash  # Save local changes
git pull origin main
git stash pop  # Restore local changes
```

### "HuggingFace API rate limit"

**Problem**: Too many requests without API key

**Solution**:
```bash
# Add HF API key to .env
echo "HF_API_KEY=your_hf_token" >> .env

# Restart server
```

### "Sync already running"

**Problem**: Previous sync still in progress

**Solution**:
```bash
# Check status
curl "http://localhost:8000/api/v1/sync/status"

# Wait for it to complete, or restart server
```

---

## 📚 More Information

- **Complete Documentation**: `SYNC_DOCUMENTATION.md`
- **Implementation Details**: `SYNC_IMPLEMENTATION_SUMMARY.md`
- **Configuration Guide**: `.env.sync.example`
- **Swagger UI**: http://localhost:8000/docs

---

## ✅ Checklist

Before running your first sync, make sure:

- [ ] Environment variables configured (`.env` file)
- [ ] GitHub token with `repo` scope
- [ ] HuggingFace API key (optional but recommended)
- [ ] Git repository initialized in `/workspace`
- [ ] Server running (`uvicorn main:app`)

---

## 🎉 You're Ready!

Your synchronization system is now set up and ready to:
- ✅ Sync GitHub repository
- ✅ Sync HuggingFace models
- ✅ Sync HuggingFace datasets
- ✅ Generate detailed reports
- ✅ Track sync history

Run your first sync now:
```bash
python sync_cli.py sync --update-db
```

**Happy syncing! 🚀**
