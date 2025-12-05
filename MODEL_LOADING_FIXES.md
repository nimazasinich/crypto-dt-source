# Model Loading Fixes and Improvements

## Summary

Comprehensive fixes and improvements to model loading system with detailed diagnostics and enhanced error tracking.

---

## Key Improvements

### 1. Enhanced Model Initialization (`ai_models.py`)

**Changes:**
- Added `force_reload` parameter to `initialize_models()` to allow re-initialization
- Added `max_models` parameter to control how many models to load
- Comprehensive logging at each step of initialization
- Better error tracking with detailed error messages
- Shows which models loaded successfully vs failed

**New Features:**
```python
# Force reload all models
initialize_models(force_reload=True)

# Load up to 10 models
initialize_models(max_models=10)

# Force reload and load up to 20 models
initialize_models(force_reload=True, max_models=20)
```

**Logging Output:**
- Logs when starting initialization
- Logs each model attempt with success/failure
- Logs category-level progress
- Logs final summary with counts

---

### 2. Enhanced `/api/models/summary` Endpoint (`api_endpoints.py`)

**New Information:**
- Accurate counts: `total_models`, `loaded_models`, `failed_models`, `not_loaded_models`
- Detailed model status per category
- Failure reasons for failed models
- Health registry information
- Diagnostics section with environment info

**Response Structure:**
```json
{
  "ok": true,
  "summary": {
    "total_models": 45,
    "loaded_models": 4,
    "failed_models": 2,
    "not_loaded_models": 39,
    "hf_mode": "public",
    "transformers_available": true,
    "hf_token_available": false
  },
  "categories": { ... },
  "loaded_model_keys": [...],
  "failed_model_keys": [...],
  "diagnostics": {
    "hf_mode": "public",
    "transformers_available": true,
    "hf_token_set": false,
    "registry_initialized": true,
    "registry_status": "ok"
  }
}
```

---

### 3. New `/api/models/diagnostics` Endpoint

**Purpose:** Get detailed diagnostics about why models aren't loading

**Returns:**
- Environment status (HF_MODE, transformers, token)
- Registry status (initialized, loaded, failed counts)
- List of issues detected
- Recommendations for fixing issues
- Sample failed model errors
- Health registry summary

**Example Response:**
```json
{
  "ok": true,
  "environment": {
    "hf_mode": "public",
    "transformers_available": true,
    "hf_token_set": false
  },
  "registry_status": {
    "initialized": true,
    "total_specs": 45,
    "pipelines_loaded": 0,
    "pipelines_failed": 5
  },
  "issues": [
    "No models loaded, 5 models failed"
  ],
  "recommendations": [
    "Check failed_models list for specific error messages",
    "Verify model IDs exist on Hugging Face Hub",
    "Check network connectivity to huggingface.co"
  ],
  "failed_samples": [
    {
      "key": "crypto_sent_0",
      "model_id": "some-model-id",
      "error": "Repository not found..."
    }
  ]
}
```

---

### 4. New `/api/models/initialize-batch` Endpoint

**Purpose:** Initialize multiple models with progress tracking

**Request Body:**
```json
{
  "max_models": 10,
  "force_reload": false,
  "category": "crypto"  // optional
}
```

**Response:**
```json
{
  "ok": true,
  "initialization_result": {
    "status": "ok",
    "models_loaded": 4,
    "models_failed": 2,
    ...
  },
  "registry_status": { ... },
  "message": "Initialized 4 model(s)"
}
```

---

### 5. Enhanced Server Startup Logging (`api_server_extended.py`)

**Changes:**
- More detailed logging during model initialization
- Shows loaded/failed/total counts
- Logs initialization result details
- Better error messages if initialization fails

**Example Output:**
```
✓ AI Models initialized: status=ok, loaded=4/45, failed=2
Model initialization result: {'status': 'ok', 'models_loaded': 4, ...}
```

---

### 6. Enhanced Re-initialization Endpoints

**Updated Endpoints:**
- `/api/models/reinit-all` - Now supports force reload with detailed status
- `/api/models/reinitialize` - Enhanced with registry status

**Both endpoints now:**
- Force reload models
- Return detailed initialization results
- Include registry status
- Provide better error messages

---

## How to Use

### 1. Check Model Status

```bash
# Get summary
curl http://localhost:7860/api/models/summary

# Get detailed diagnostics
curl http://localhost:7860/api/models/diagnostics
```

### 2. Force Model Initialization

```bash
# Re-initialize all models
curl -X POST http://localhost:7860/api/models/reinit-all

# Initialize with limit
curl -X POST http://localhost:7860/api/models/initialize-batch \
  -H "Content-Type: application/json" \
  -d '{"max_models": 10, "force_reload": true}'
```

### 3. Check Server Logs

Look for these log messages:
- `Starting model initialization...`
- `[category] Attempting to load model: ...`
- `[category] ✅ Successfully loaded model: ...`
- `[category] ⚠️ Model ... not available: ...`
- `Model initialization summary: ...`

---

## Troubleshooting

### Issue: Models show `loaded: 0` in summary

**Check:**
1. Call `/api/models/diagnostics` to see issues
2. Check server logs for initialization errors
3. Verify `HF_MODE` is set correctly
4. Verify `transformers` library is installed
5. Check if `HF_TOKEN` is needed for specific models

### Issue: Models fail to load

**Check:**
1. Review `failed_samples` in diagnostics endpoint
2. Check network connectivity to huggingface.co
3. Verify model IDs exist on Hugging Face Hub
4. Check if models require authentication (HF_TOKEN)

### Issue: Initialization not happening

**Check:**
1. Verify `initialize_models()` is called during startup (check logs)
2. Check if `_initialized` flag is preventing re-initialization
3. Use `/api/models/reinit-all` to force initialization

---

## Diagnostic Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/models/summary` | GET | Get models summary with counts and status |
| `/api/models/diagnostics` | GET | Get detailed diagnostics and recommendations |
| `/api/models/initialize-batch` | POST | Initialize models with parameters |
| `/api/models/reinit-all` | POST | Force re-initialize all models |
| `/api/models/reinitialize` | POST | Force re-initialize (alias) |

---

## Files Modified

1. **`ai_models.py`**
   - Enhanced `initialize_models()` method
   - Added comprehensive logging
   - Improved error tracking

2. **`api_endpoints.py`**
   - Enhanced `/api/models/summary` endpoint
   - Added `/api/models/diagnostics` endpoint
   - Added `/api/models/initialize-batch` endpoint
   - Improved error handling

3. **`api_server_extended.py`**
   - Enhanced startup logging
   - Improved re-initialization endpoints
   - Better error messages

---

## Next Steps

1. **Test the endpoints** to verify models are loading correctly
2. **Check diagnostics** to identify any remaining issues
3. **Review logs** for detailed initialization progress
4. **Use batch initialization** to load specific models if needed

---

**Status**: ✅ All improvements implemented and ready for testing

