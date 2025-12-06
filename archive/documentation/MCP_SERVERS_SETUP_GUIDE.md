# MCP Servers Setup Guide - FREE Servers Only

This guide explains how to configure Model Context Protocol (MCP) servers in Cursor IDE for zero-cost token optimization.

**Last Updated:** 2025  
**Status:** ✅ All servers are completely FREE (no ongoing costs)

---

## Overview

MCP servers allow Cursor to interact with external tools and services, reducing the need to paste large code blocks and context into chat. This dramatically reduces token usage.

---

## Installation Methods

### Method 1: Via Cursor Settings (Recommended)

1. Open Cursor Settings (Ctrl+,)
2. Search for "MCP" or "Model Context Protocol"
3. Click "Edit in settings.json"
4. Add server configurations (see below)

### Method 2: Direct Configuration File

Cursor typically stores MCP configuration in:
- **Windows:** `%APPDATA%\Cursor\User\globalStorage\cursor.mcp\mcp.json`
- **macOS:** `~/Library/Application Support/Cursor/User/globalStorage/cursor.mcp/mcp.json`
- **Linux:** `~/.config/Cursor/User/globalStorage/cursor.mcp/mcp.json`

---

## Essential FREE Servers

### 1. Filesystem MCP (Local File Operations)

**Purpose:** Read/write files without pasting content into chat

**Configuration:**
```json
{
  "filesystem": {
    "command": "npx",
    "args": [
      "-y",
      "@modelcontextprotocol/server-filesystem",
      "C:\\Users\\Dreammaker\\Downloads\\final_updated_crypto_dthub_project\\crypto-dt-source-main"
    ]
  }
}
```

**Usage:**
- Agent can read files directly
- No need to paste file contents
- Saves thousands of tokens per file

**Status:** ✅ Ready to use (no API keys needed)

---

### 2. Memory MCP (Knowledge Base)

**Purpose:** Store and retrieve persistent knowledge across sessions

**Configuration:**
```json
{
  "memory": {
    "command": "npx",
    "args": [
      "-y",
      "@modelcontextprotocol/server-memory"
    ]
  }
}
```

**Usage:**
- Agent remembers project-specific information
- Reduces repetitive explanations
- Knowledge persists across sessions

**Status:** ✅ Ready to use (no API keys needed)

---

### 3. SQLite MCP (Local Database)

**Purpose:** Query local SQLite databases without pasting data

**Configuration:**
```json
{
  "sqlite": {
    "command": "npx",
    "args": [
      "-y",
      "@modelcontextprotocol/server-sqlite",
      "--db-path",
      "./data.db"
    ]
  }
}
```

**Usage:**
- Query project databases directly
- Generate reports without data dumps
- Efficient data analysis

**Status:** ✅ Ready to use (no API keys needed)

---

## Free Tier Servers (No Credit Card Required)

### 4. Brave Search MCP (Web Search - FREE)

**Purpose:** Web search without using context tokens for URLs

**Setup:**
1. Get free API key: https://brave.com/search/api/
2. No credit card required
3. 2000 free queries per month

**Configuration:**
```json
{
  "brave-search": {
    "command": "npx",
    "args": [
      "-y",
      "@modelcontextprotocol/server-brave-search"
    ],
    "env": {
      "BRAVE_API_KEY": "YOUR_KEY_HERE"
    }
  }
}
```

**Status:** ⏳ Requires free API key (no credit card)

---

### 5. Composio MCP (100+ Apps - Free Tier)

**Purpose:** Connect to Gmail, Slack, Notion, Google Drive, etc.

**Setup:**
1. Sign up: https://app.composio.dev
2. Get free API key (500 calls/month)
3. OAuth built-in for secure connections

**Configuration:**
```json
{
  "composio": {
    "command": "npx",
    "args": [
      "-y",
      "@composio/mcp",
      "setup",
      "https://mcp.composio.dev/YOUR_KEY",
      "--client",
      "cursor"
    ]
  }
}
```

**Status:** ⏳ Requires free account (500 API calls/month)

---

### 6. Firecrawl MCP (Web Scraping - Free Tier)

**Purpose:** Scrape web pages without pasting HTML

**Setup:**
1. Sign up: https://firecrawl.dev
2. Get free API key
3. 500 free scrapes/month

**Configuration:**
```json
{
  "firecrawl": {
    "command": "npx",
    "args": [
      "-y",
      "@firecrawl/mcp-server"
    ],
    "env": {
      "FIRECRAWL_API_KEY": "YOUR_KEY_HERE"
    }
  }
}
```

**Status:** ⏳ Requires free API key (500 scrapes/month)

---

## Open Source FREE Servers

### 7. HackerNews MCP (Tech News)

**Purpose:** Fetch HackerNews articles and comments

**Configuration:**
```json
{
  "hackernews": {
    "command": "npx",
    "args": [
      "-y",
      "hackernews-mcp-server"
    ]
  }
}
```

**Status:** ✅ Ready to use (completely free, no API keys)

---

### 8. YouTube Transcript MCP

**Purpose:** Get transcripts from YouTube videos

**Configuration:**
```json
{
  "youtube": {
    "command": "npx",
    "args": [
      "-y",
      "youtube-transcript-mcp"
    ]
  }
}
```

**Status:** ✅ Ready to use (completely free)

---

### 9. GitHub MCP (Optional)

**Purpose:** Manage GitHub repositories, issues, PRs

**Setup:**
1. Create Personal Access Token: https://github.com/settings/tokens
2. Select scopes: `repo`, `read:org`, `read:user`
3. No credit card needed (free tier)

**Configuration:**
```json
{
  "github": {
    "command": "npx",
    "args": [
      "-y",
      "@modelcontextprotocol/server-github"
    ],
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_TOKEN_HERE"
    }
  }
}
```

**Status:** ⏳ Requires free GitHub token

---

## Complete Configuration Template

Create or update your MCP configuration file with all free servers:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "C:\\Users\\Dreammaker\\Downloads\\final_updated_crypto_dthub_project\\crypto-dt-source-main"
      ]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "sqlite": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sqlite",
        "--db-path",
        "./data.db"
      ]
    },
    "hackernews": {
      "command": "npx",
      "args": ["-y", "hackernews-mcp-server"]
    },
    "youtube": {
      "command": "npx",
      "args": ["-y", "youtube-transcript-mcp"]
    }
  }
}
```

---

## Testing MCP Servers

### Test Filesystem MCP:
```
@filesystem Read the file: app.py
```

### Test Memory MCP:
```
@memory Remember: This project uses Flask and FastAPI
```

### Test SQLite MCP:
```
@sqlite Query the database: SELECT * FROM users LIMIT 5
```

### Test HackerNews MCP:
```
@hackernews Get top 10 stories
```

---

## Troubleshooting

### Server Not Loading?

1. **Check Node.js:** Ensure Node.js is installed (`node --version`)
2. **Check npx:** Ensure npx works (`npx --version`)
3. **Restart Cursor:** After adding servers, restart Cursor
4. **Check logs:** Look for errors in Cursor's developer console

### Permission Errors?

1. **Filesystem path:** Use absolute paths for filesystem MCP
2. **Database path:** Ensure SQLite file exists or path is correct
3. **Windows paths:** Use double backslashes or forward slashes

### API Key Issues?

1. **Environment variables:** Ensure env vars are set correctly
2. **Key format:** Copy keys exactly (no extra spaces)
3. **Free tier limits:** Check if you've exceeded free tier

---

## Token Savings Estimate

### Without MCP:
- File read: ~5,000 tokens per file
- Database query: ~3,000 tokens per query
- Web search: ~2,000 tokens per result

### With MCP:
- File read: ~500 tokens (using tool)
- Database query: ~300 tokens (using tool)
- Web search: ~200 tokens (using tool)

**Savings: 80-90% reduction per operation**

---

## Priority Installation Order

1. ✅ **Filesystem MCP** - Highest impact, zero setup
2. ✅ **Memory MCP** - Reduces repetitive context
3. ✅ **SQLite MCP** - If you use databases
4. ✅ **HackerNews MCP** - Easy setup, useful for research
5. ⏳ **Brave Search** - Requires free API key (2 min setup)
6. ⏳ **GitHub MCP** - If you use GitHub actively
7. ⏳ **Composio MCP** - If you use connected apps

---

## Security Notes

- ✅ All listed servers are safe and open source
- ✅ Free tier servers have usage limits (no surprise charges)
- ⚠️ Store API keys securely (use environment variables)
- ⚠️ GitHub token: Use minimum required permissions
- ⚠️ Filesystem MCP: Limit to project directory only

---

## Next Steps

1. Install essential servers (filesystem, memory, SQLite)
2. Test each server after installation
3. Update `token-tracker.md` when servers are verified
4. Install optional servers as needed
5. Monitor token usage improvements

---

**Questions?** Check Cursor's MCP documentation or server-specific README files.

