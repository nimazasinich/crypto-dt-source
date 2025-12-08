# Apply Header Enhancements Script
# This script applies the enhanced header to your application

Write-Host "🚀 Applying Header Enhancements..." -ForegroundColor Cyan
Write-Host ""

# Step 1: Backup existing files
Write-Host "📦 Step 1: Creating backups..." -ForegroundColor Yellow
Copy-Item "static/shared/layouts/header.html" "static/shared/layouts/header-backup.html" -ErrorAction SilentlyContinue
Write-Host "✓ Backed up header.html" -ForegroundColor Green

# Step 2: Replace header
Write-Host ""
Write-Host "🔄 Step 2: Replacing header..." -ForegroundColor Yellow
Copy-Item "static/shared/layouts/header-enhanced.html" "static/shared/layouts/header.html" -Force
Write-Host "✓ Header replaced with enhanced version" -ForegroundColor Green

# Step 3: Check if CSS files exist
Write-Host ""
Write-Host "📝 Step 3: Checking CSS files..." -ForegroundColor Yellow
if (Test-Path "static/shared/css/header-enhanced.css") {
    Write-Host "✓ header-enhanced.css found" -ForegroundColor Green
} else {
    Write-Host "✗ header-enhanced.css not found!" -ForegroundColor Red
}

if (Test-Path "static/shared/css/sidebar-enhanced.css") {
    Write-Host "✓ sidebar-enhanced.css found" -ForegroundColor Green
} else {
    Write-Host "✗ sidebar-enhanced.css not found!" -ForegroundColor Red
}

# Step 4: Instructions for adding CSS
Write-Host ""
Write-Host "📋 Step 4: Manual steps required..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Add these lines to your HTML files:" -ForegroundColor Cyan
Write-Host '<link rel="stylesheet" href="/static/shared/css/header-enhanced.css">' -ForegroundColor White
Write-Host '<link rel="stylesheet" href="/static/shared/css/sidebar-enhanced.css">' -ForegroundColor White
Write-Host ""
Write-Host "Files to update:" -ForegroundColor Cyan
Write-Host "  - static/pages/dashboard/index-enhanced.html" -ForegroundColor White
Write-Host "  - static/pages/market/index.html" -ForegroundColor White
Write-Host "  - static/pages/models/index.html" -ForegroundColor White
Write-Host "  - (and other page HTML files)" -ForegroundColor White

# Step 5: Summary
Write-Host ""
Write-Host "✅ Enhancement files are ready!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Add CSS links to your HTML files (see above)" -ForegroundColor White
Write-Host "2. Clear browser cache (Ctrl+Shift+Delete)" -ForegroundColor White
Write-Host "3. Reload your application" -ForegroundColor White
Write-Host "4. Test all pages" -ForegroundColor White
Write-Host ""
Write-Host "📚 Read HEADER_ENHANCEMENT_GUIDE.md for details" -ForegroundColor Yellow
Write-Host ""
Write-Host "To rollback:" -ForegroundColor Cyan
Write-Host "Copy-Item static/shared/layouts/header-backup.html static/shared/layouts/header.html" -ForegroundColor White
Write-Host ""
Write-Host "🎉 Done!" -ForegroundColor Green
