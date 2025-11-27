#!/usr/bin/env python3
"""
Fix unified_dashboard.html - Inline static files and fix all issues
"""

import re

# Read static files
with open("static/css/connection-status.css", "r", encoding="utf-8") as f:
    css_content = f.read()

with open("static/js/websocket-client.js", "r", encoding="utf-8") as f:
    js_content = f.read()

# Read original dashboard
with open("unified_dashboard.html", "r", encoding="utf-8") as f:
    html_content = f.read()

# Remove problematic permissions policy
html_content = re.sub(
    r'<meta\s+http-equiv="Permissions-Policy"[^>]*>', "", html_content, flags=re.IGNORECASE
)

# Replace external CSS link with inline style
css_link_pattern = r'<link rel="stylesheet" href="/static/css/connection-status\.css">'
inline_css = f'<style id="connection-status-css">\n{css_content}\n</style>'
html_content = re.sub(css_link_pattern, inline_css, html_content)

# Replace external JS with inline script
js_script_pattern = r'<script src="/static/js/websocket-client\.js"></script>'
inline_js = f'<script id="websocket-client-js">\n{js_content}\n</script>'
html_content = re.sub(js_script_pattern, inline_js, html_content)

# Fix: Add defer to Chart.js to prevent blocking
html_content = html_content.replace(
    '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>',
    '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js" defer></script>',
)

# Write fixed dashboard
with open("unified_dashboard.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ Dashboard fixed successfully!")
print("  - Inlined CSS from static/css/connection-status.css")
print("  - Inlined JS from static/js/websocket-client.js")
print("  - Removed problematic permissions policy")
print("  - Added defer to Chart.js")
