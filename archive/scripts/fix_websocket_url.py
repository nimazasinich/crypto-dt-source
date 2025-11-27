#!/usr/bin/env python3
"""
Fix WebSocket URL to support both HTTP and HTTPS (HuggingFace Spaces)
"""

# Read dashboard
with open("unified_dashboard.html", "r", encoding="utf-8") as f:
    html_content = f.read()

# Fix WebSocket URL to support both ws:// and wss://
old_ws_url = "this.url = url || `ws://${window.location.host}/ws`;"
new_ws_url = "this.url = url || `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`;"

html_content = html_content.replace(old_ws_url, new_ws_url)

# Write fixed dashboard
with open("unified_dashboard.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ WebSocket URL fixed for HTTPS/WSS support")
