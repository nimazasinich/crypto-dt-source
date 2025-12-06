# HuggingFace Token Setup Guide

## Overview

The application can optionally upload collected cryptocurrency data to HuggingFace Datasets. This requires a valid HuggingFace access token.

## Why Do I Need a HuggingFace Token?

HuggingFace tokens enable:
- **Data Persistence**: Upload collected data to HuggingFace Datasets for long-term storage
- **Data Sharing**: Share your datasets publicly or privately with others
- **Cloud Backup**: Automatic backup of all collected cryptocurrency data
- **API Access**: Access your data from anywhere via HuggingFace's API

## Current Issue

If you're seeing errors like:
```
User Access Token "Really-amin" is expired
401 Client Error: Unauthorized
```

This means your HuggingFace token is invalid or has expired.

## How to Fix

### Step 1: Get a New HuggingFace Token

1. **Visit HuggingFace Settings**:
   - Go to https://huggingface.co/settings/tokens
   - Log in to your HuggingFace account (or create one if needed)

2. **Create a New Access Token**:
   - Click "New token" button
   - **Name**: Give it a descriptive name (e.g., `crypto-data-hub-worker`)
   - **Type**: Select "Write" (required for uploading datasets)
   - **Permissions**: Make sure it has permission to create and write to datasets
   - Click "Generate token"

3. **Copy the Token**:
   - **IMPORTANT**: Copy the token immediately - you won't be able to see it again!
   - The token will look like: `hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Step 2: Update Your Environment Variable

#### Option A: Using Docker/Docker Compose

1. **Edit `.env` file**:
   ```bash
   # Open .env file in your project root
   nano .env
   ```

2. **Update HF_TOKEN**:
   ```bash
   # Replace the old token with your new one
   HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

3. **Restart the application**:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

#### Option B: Using Direct Environment Variable

```bash
# Set the environment variable
export HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Restart your application
python main.py
```

#### Option C: Using Systemd Service

If running as a systemd service:

1. **Edit service file**:
   ```bash
   sudo nano /etc/systemd/system/crypto-data-hub.service
   ```

2. **Add environment variable**:
   ```ini
   [Service]
   Environment="HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
   ```

3. **Reload and restart**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart crypto-data-hub
   ```

### Step 3: Verify the Token Works

After updating the token and restarting:

1. **Check the startup logs**:
   ```bash
   # Docker
   docker-compose logs -f
   
   # Or direct logs
   tail -f logs/app.log
   ```

2. **Look for success messages**:
   ```
   ✅ HuggingFace Dataset Uploader initialized
   ✅ HuggingFace Dataset upload ENABLED
   ✅ Successfully uploaded market data to HuggingFace Datasets
   ```

3. **Verify on HuggingFace Hub**:
   - Visit https://huggingface.co/YOUR_USERNAME
   - Check for newly created datasets:
     - `crypto-market-data`
     - `crypto-ohlc-data`
     - `crypto-news-data`
     - `crypto-sentiment-data`
     - `crypto-onchain-data`
     - `crypto-whale-data`
     - `crypto-explorer-data`

## Optional: Disable HuggingFace Upload

If you don't want to use HuggingFace Datasets:

1. **Remove or comment out the HF_TOKEN**:
   ```bash
   # .env file
   # HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

2. **Restart the application**

The workers will continue to collect and store data locally in the SQLite database, but won't upload to HuggingFace.

You'll see this message:
```
ℹ️  HuggingFace Dataset upload DISABLED (no HF_TOKEN)
```

## Troubleshooting

### Token Still Not Working

**Check token permissions**:
- Token must have "Write" permission
- Token must not be expired
- Account must be verified

**Regenerate the token**:
1. Delete the old token on HuggingFace
2. Create a new token with "Write" permission
3. Update your `.env` file
4. Restart the application

### Datasets Not Appearing

**Check HuggingFace username**:
- The uploader tries to detect your username automatically
- If detection fails, it defaults to namespace `crypto-data-hub`
- You can override by setting `HF_USERNAME` environment variable:
  ```bash
  HF_USERNAME=your-hf-username
  HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  ```

**Check dataset creation permissions**:
- Make sure you can create datasets on HuggingFace
- Check if you've hit any rate limits or quotas

### 451 Errors from Binance

If you're seeing:
```
HTTP error '451 ' (Unavailable For Legal Reasons)
```

This is a **separate issue** from HuggingFace tokens. Binance API is geo-blocked in your region. Solutions:

1. **Use a VPN** to access Binance from an allowed region
2. **Alternative data sources**: The app also uses CoinGecko which doesn't have geo-restrictions
3. **Wait for alternative exchange integrations**: Future updates may add more exchange options

The market data worker will continue working with CoinGecko even if Binance is blocked.

## Security Best Practices

1. **Never commit tokens to git**:
   - `.env` file should be in `.gitignore`
   - Never share your token publicly

2. **Use token with minimal permissions**:
   - Only "Write" permission for datasets
   - Don't use tokens with model or inference permissions unless needed

3. **Rotate tokens regularly**:
   - Create new tokens every few months
   - Delete old unused tokens

4. **Monitor token usage**:
   - Check HuggingFace settings for active tokens
   - Revoke any suspicious tokens immediately

## Support

If you continue having issues:

1. **Check HuggingFace Status**: https://status.huggingface.co/
2. **HuggingFace Documentation**: https://huggingface.co/docs/hub/security-tokens
3. **Application Logs**: Check full error messages in logs
4. **Create an Issue**: Report persistent problems on the project repository

## Summary

| Issue | Solution |
|-------|----------|
| Expired token | Create new token at https://huggingface.co/settings/tokens |
| 401 Unauthorized | Update HF_TOKEN in .env and restart |
| Datasets not created | Verify token has "Write" permission |
| Don't want HF upload | Remove/comment HF_TOKEN from .env |
| Binance 451 errors | Use VPN or rely on CoinGecko (separate issue) |

---

**Last Updated**: December 6, 2025
