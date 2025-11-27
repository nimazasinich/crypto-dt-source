# GitHub and HuggingFace Synchronization System

## 🎯 Overview

This system provides **complete synchronization** between GitHub repositories and HuggingFace Hub, including:

- ✅ GitHub commit tracking and repository synchronization
- ✅ HuggingFace models synchronization
- ✅ HuggingFace datasets synchronization
- ✅ Automatic database updates
- ✅ Comprehensive reporting
- ✅ REST API and CLI interfaces

---

## 📦 Components

### 1. Core Services

- **`github_sync_service.py`**: GitHub API integration and git operations
- **`huggingface_sync_service.py`**: HuggingFace Hub API integration
- **`sync_orchestrator.py`**: Coordinates complete sync workflow
- **`sync_database_updater.py`**: Database management for sync data

### 2. Interfaces

- **`sync_api.py`**: REST API endpoints
- **`sync_cli.py`**: Command-line interface

### 3. Configuration

- **`.env.sync.example`**: Environment variables template

---

## 🚀 Setup

### 1. Install Dependencies

```bash
pip install fastapi uvicorn httpx sqlalchemy pydantic
```

### 2. Configure Environment Variables

```bash
# Copy example file
cp .env.sync.example .env

# Edit with your values
nano .env
```

**Required Variables:**
```bash
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=owner/repository
HF_API_KEY=your_hf_api_key_here  # Optional but recommended
```

### 3. Initialize Database

The database is automatically created on first use. Default location: `sync_database.db`

---

## 💻 Usage

### Using REST API

**Start the server:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Endpoints:**

1. **Run Complete Sync**
```bash
curl -X POST "http://localhost:8000/api/v1/sync/run" \
  -H "Content-Type: application/json" \
  -d '{"branch": "main", "commit_message": "Sync update"}'
```

2. **Get Sync Status**
```bash
curl "http://localhost:8000/api/v1/sync/status"
```

3. **Get GitHub Commits**
```bash
curl "http://localhost:8000/api/v1/sync/github/commits?branch=main&limit=10"
```

4. **Get HuggingFace Models**
```bash
curl "http://localhost:8000/api/v1/sync/hf/models"
```

5. **Get HuggingFace Datasets**
```bash
curl "http://localhost:8000/api/v1/sync/hf/datasets"
```

6. **Get Synced Models from Database**
```bash
curl "http://localhost:8000/api/v1/sync/database/models"
```

7. **Get Sync History**
```bash
curl "http://localhost:8000/api/v1/sync/history?limit=10"
```

8. **Get Latest Report**
```bash
curl "http://localhost:8000/api/v1/sync/reports/latest" -o latest_report.txt
```

### Using CLI

**Complete Sync:**
```bash
python sync_cli.py sync --branch main --message "Update models" --update-db
```

**GitHub Only:**
```bash
python sync_cli.py github --branch main
```

**HuggingFace Only:**
```bash
python sync_cli.py hf --update-db
```

**Get Commits:**
```bash
python sync_cli.py commits --branch main --limit 5
```

**Get Models:**
```bash
python sync_cli.py models
```

**Get History:**
```bash
python sync_cli.py history --limit 10
```

---

## 📊 Workflow

### Complete Sync Workflow

1. **Fetch GitHub Commits**
   - Connects to GitHub API
   - Fetches latest commits
   - Records commit information

2. **Sync HuggingFace Models**
   - Connects to HuggingFace Hub
   - Fetches model information for:
     - `ElKulako/cryptobert`
     - `kk08/CryptoBERT`
     - `ProsusAI/finbert`
     - `cardiffnlp/twitter-roberta-base-sentiment`

3. **Sync HuggingFace Datasets**
   - Fetches dataset information for:
     - `linxy/CryptoCoin`
     - `WinkingFace/CryptoLM-Bitcoin-BTC-USDT`
     - `WinkingFace/CryptoLM-Ethereum-ETH-USDT`
     - `WinkingFace/CryptoLM-Solana-SOL-USDT`
     - `WinkingFace/CryptoLM-Ripple-XRP-USDT`

4. **Git Operations**
   - `git pull origin main`
   - `git add .`
   - `git commit -m "Sync message"`
   - `git push origin main`

5. **Database Update**
   - Updates models table
   - Updates datasets table
   - Records sync history

6. **Report Generation**
   - Creates detailed text report
   - Saves to `/workspace/sync_reports/`
   - Includes all operations and results

---

## 📁 Database Schema

### synced_models
```sql
- id (INTEGER, PRIMARY KEY)
- model_id (STRING, UNIQUE)
- author (STRING)
- pipeline_tag (STRING)
- downloads (INTEGER)
- likes (INTEGER)
- library_name (STRING)
- created_at (DATETIME)
- last_modified (DATETIME)
- last_synced (DATETIME)
- sha (STRING)
- url (TEXT)
- is_active (BOOLEAN)
```

### synced_datasets
```sql
- id (INTEGER, PRIMARY KEY)
- dataset_id (STRING, UNIQUE)
- author (STRING)
- downloads (INTEGER)
- likes (INTEGER)
- created_at (DATETIME)
- last_modified (DATETIME)
- last_synced (DATETIME)
- sha (STRING)
- url (TEXT)
- is_active (BOOLEAN)
```

### sync_history
```sql
- id (INTEGER, PRIMARY KEY)
- sync_timestamp (DATETIME)
- success (BOOLEAN)
- duration_seconds (INTEGER)
- models_synced (INTEGER)
- datasets_synced (INTEGER)
- github_commits_fetched (INTEGER)
- errors_count (INTEGER)
- report_path (TEXT)
```

---

## 📝 Reports

Reports are generated automatically after each sync and stored in `/workspace/sync_reports/`.

**Report Format:**
```
================================================================================
SYNCHRONIZATION REPORT
================================================================================

Report Generated: 2025-11-27 12:00:00 UTC
Status: ✅ SUCCESS
Duration: 45.23 seconds

--------------------------------------------------------------------------------
SUMMARY
--------------------------------------------------------------------------------
GitHub Commits Fetched: 5
HF Models Synced: 4/4
HF Datasets Synced: 5/5
Git Operations: 5
Total Errors: 0
Total Warnings: 0

--------------------------------------------------------------------------------
GITHUB COMMITS
--------------------------------------------------------------------------------
... [commit details]

--------------------------------------------------------------------------------
HUGGINGFACE MODELS
--------------------------------------------------------------------------------
... [model details]

--------------------------------------------------------------------------------
HUGGINGFACE DATASETS
--------------------------------------------------------------------------------
... [dataset details]

--------------------------------------------------------------------------------
GIT OPERATIONS
--------------------------------------------------------------------------------
... [operation details]

================================================================================
END OF REPORT
================================================================================
```

---

## 🔧 Advanced Configuration

### Custom Models and Datasets

Edit `backend/services/huggingface_sync_service.py`:

```python
self.models_to_sync = [
    "your-username/your-model",
    "another-model",
]

self.datasets_to_sync = [
    "your-username/your-dataset",
    "another-dataset",
]
```

### Custom Database

Set `DATABASE_URL` in `.env`:

```bash
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/sync_db

# MySQL
DATABASE_URL=mysql://user:password@localhost:3306/sync_db
```

### Automated Sync

**Using Cron:**
```cron
# Run sync every hour
0 * * * * cd /workspace && python sync_cli.py sync --update-db
```

**Using Systemd Timer:**
```ini
# /etc/systemd/system/crypto-sync.timer
[Unit]
Description=Crypto Sync Timer

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
```

---

## 🧪 Testing

Run tests:
```bash
pytest test_sync.py -v
```

Test individual components:
```bash
# Test GitHub sync
python sync_cli.py commits --limit 1

# Test HuggingFace sync
python sync_cli.py models

# Test complete workflow
python sync_cli.py sync --branch main --update-db
```

---

## 📈 Monitoring

### Check Sync Status

**Via API:**
```bash
curl "http://localhost:8000/api/v1/sync/status"
```

**Via CLI:**
```bash
python sync_cli.py history --limit 5
```

### View Reports

**Latest report:**
```bash
curl "http://localhost:8000/api/v1/sync/reports/latest" -o report.txt
cat report.txt
```

**All reports:**
```bash
ls -lh /workspace/sync_reports/
```

---

## 🔒 Security

### API Keys

- Store API keys in `.env` file
- Never commit `.env` to version control
- Use read-only tokens when possible
- Rotate keys regularly

### GitHub Token Scopes

Required scopes:
- `repo` - Full control of private repositories
- `workflow` - Update GitHub Action workflows (optional)

### HuggingFace Token

- Optional but recommended
- Provides higher rate limits
- Required for private models/datasets

---

## 🚨 Troubleshooting

### "Git pull failed"

**Solution:**
```bash
cd /workspace
git status
git pull origin main --rebase
```

### "HuggingFace API error"

**Solution:**
- Check HF_API_KEY is set
- Verify model/dataset names
- Check HuggingFace status

### "Database locked"

**Solution:**
```bash
# Close other connections
# Or use PostgreSQL instead of SQLite
```

### "Sync already running"

**Solution:**
```bash
# Wait for current sync to complete
# Or restart the server to reset state
```

---

## 📞 Support

- API Documentation: `/docs` endpoint
- Swagger UI: `http://localhost:8000/docs`
- CLI Help: `python sync_cli.py --help`

---

## 🎯 Features Summary

✅ **GitHub Integration**
- Commit tracking
- Pull/push operations
- Branch management

✅ **HuggingFace Integration**
- Model synchronization
- Dataset synchronization
- Metadata tracking

✅ **Database Management**
- SQLite/PostgreSQL/MySQL support
- Model/dataset storage
- Sync history tracking

✅ **Reporting**
- Detailed text reports
- JSON data export
- Historical tracking

✅ **Interfaces**
- REST API endpoints
- Command-line interface
- Background processing

✅ **Production Ready**
- Error handling
- Retry logic
- Comprehensive logging

---

**Implementation Date**: November 27, 2025  
**Version**: 1.0.0  
**Status**: ✅ Complete and Ready
