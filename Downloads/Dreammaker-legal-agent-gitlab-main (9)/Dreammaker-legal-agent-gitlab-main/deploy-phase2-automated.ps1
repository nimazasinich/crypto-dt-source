# Phase 2 Automated Deployment Script (PowerShell)
# Automated version - skips interactive prompts for CI/CD
# Use this for staging deployment with known issues

Write-Host "🚀 Phase 2 Automated Deployment (Staging)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Set error action preference
$ErrorActionPreference = "Continue"

Write-Host "📋 Deployment Configuration:" -ForegroundColor Cyan
Write-Host "   Target: Staging Environment" -ForegroundColor Yellow
Write-Host "   Mode: Automated (non-interactive)" -ForegroundColor Yellow
Write-Host "   Quality Checks: Informational only" -ForegroundColor Yellow
Write-Host ""

# Check TypeScript compilation (informational)
Write-Host "📝 Checking TypeScript compilation..." -ForegroundColor Cyan
npx tsc --noEmit 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ TypeScript compilation successful" -ForegroundColor Green
} else {
    Write-Host "⚠️  TypeScript has errors (proceeding anyway for staging)" -ForegroundColor Yellow
    Write-Host "   Note: Fix these before production deployment" -ForegroundColor Yellow
}

# Run linter (informational)
Write-Host ""
Write-Host "🔍 Running linter..." -ForegroundColor Cyan
npm run lint 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Linter checks passed" -ForegroundColor Green
} else {
    Write-Host "⚠️  Linter found issues (proceeding anyway for staging)" -ForegroundColor Yellow
}

# Attempt to build
Write-Host ""
Write-Host "🔨 Building project..." -ForegroundColor Cyan
npm run build 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Build successful" -ForegroundColor Green
    $buildSuccess = $true
} else {
    Write-Host "⚠️  Build failed (will skip for staging branch creation)" -ForegroundColor Yellow
    $buildSuccess = $false
}

# Git operations
Write-Host ""
Write-Host "📦 Preparing Git Commit..." -ForegroundColor Cyan

# Add Phase 2 files
Write-Host "   Adding Phase 2 files..." -ForegroundColor Gray
git add `
    src/views/MarketAnalysisHub.tsx `
    src/services/CacheManager.ts `
    src/App.tsx `
    src/components/Navigation/EnhancedSidebar.tsx `
    src/components/ui/Toast.tsx `
    src/views/trading-hub/tabs/FuturesTab.tsx `
    src/views/trading-hub/UnifiedTradingHubView.tsx `
    PHASE_2_*.md `
    deploy-phase2.ps1 `
    deploy-phase2.sh `
    deploy-phase2-automated.ps1 2>&1 | Out-Null

Write-Host "✅ Files staged for commit" -ForegroundColor Green

# Create commit
$commitMsg = "WIP: Phase 2 Market Analysis Hub and Trading Hub - Staging | Features: Market Analysis Hub, Trading Hub Quick Actions, Tab Presets, Global Filters, CacheManager | Known Issues: TypeScript errors, Component prop mismatches | Status: STAGING ONLY - NOT PRODUCTION READY | Next: Fix TS errors, Complete testing, Get approval"

Write-Host ""
Write-Host "   Creating commit..." -ForegroundColor Gray
git commit -m $commitMsg 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Git commit created" -ForegroundColor Green
} else {
    Write-Host "⚠️  Git commit skipped (no changes or already committed)" -ForegroundColor Yellow
}

# Create staging branch
Write-Host ""
Write-Host "🌿 Creating staging branch..." -ForegroundColor Cyan

# Check if branch already exists
$branchExists = git branch --list staging/phase2-market-analysis
if ($branchExists) {
    Write-Host "   Branch already exists, switching to it..." -ForegroundColor Gray
    git checkout staging/phase2-market-analysis 2>&1 | Out-Null
} else {
    Write-Host "   Creating new branch..." -ForegroundColor Gray
    git checkout -b staging/phase2-market-analysis 2>&1 | Out-Null
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Staging branch ready: staging/phase2-market-analysis" -ForegroundColor Green
} else {
    Write-Host "⚠️  Branch operation had issues" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "📊 Deployment Summary" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "Branch: staging/phase2-market-analysis" -ForegroundColor White
Write-Host "Status: $(if ($buildSuccess) { "✅ Ready for staging" } else { "⚠️  Has build errors" })" -ForegroundColor $(if ($buildSuccess) { "Green" } else { "Yellow" })
Write-Host "Target: Staging environment only" -ForegroundColor White
Write-Host ""

Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Push to staging:" -ForegroundColor White
Write-Host "   git push origin staging/phase2-market-analysis" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Fix TypeScript errors before production:" -ForegroundColor White
Write-Host "   npx tsc --noEmit | more" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Test in staging environment" -ForegroundColor White
Write-Host "   - Monitor for issues" -ForegroundColor Gray
Write-Host "   - Verify Phase 2 features" -ForegroundColor Gray
Write-Host "   - Document test results" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Production deployment:" -ForegroundColor White
Write-Host "   - Fix all TypeScript errors" -ForegroundColor Gray
Write-Host "   - Get stakeholder approval" -ForegroundColor Gray
Write-Host "   - Run .\deploy-phase2.ps1 (full version)" -ForegroundColor Gray
Write-Host ""

Write-Host "⚠️  Important Notes:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   • This is a STAGING deployment only" -ForegroundColor Yellow
Write-Host "   • DO NOT deploy to production yet" -ForegroundColor Yellow
Write-Host "   • Fix TypeScript errors before production" -ForegroundColor Yellow
Write-Host "   • Complete testing checklist" -ForegroundColor Yellow
Write-Host "   • Get stakeholder sign-off" -ForegroundColor Yellow
Write-Host ""

Write-Host "✅ Staging deployment preparation complete!" -ForegroundColor Green
Write-Host ""

# Return to main branch
Write-Host "Returning to main branch..." -ForegroundColor Gray
git checkout main 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Back on main branch" -ForegroundColor Green
} else {
    # Try master if main doesn't exist
    git checkout master 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Back on master branch" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "🎯 To push to staging remote:" -ForegroundColor Cyan
Write-Host "   git push origin staging/phase2-market-analysis" -ForegroundColor White
Write-Host ""

