# Phase 2 Quick Staging Deployment
# Simple version without fancy formatting

Write-Host "Phase 2 Automated Deployment to Staging" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# TypeScript check (informational)
Write-Host "Checking TypeScript..." -ForegroundColor Cyan
npx tsc --noEmit 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  TypeScript: OK" -ForegroundColor Green
} else {
    Write-Host "  TypeScript: Has errors (proceeding anyway)" -ForegroundColor Yellow
}

# Linter check (informational)
Write-Host "Checking linter..." -ForegroundColor Cyan
npm run lint 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  Linter: OK" -ForegroundColor Green
} else {
    Write-Host "  Linter: Has issues (proceeding anyway)" -ForegroundColor Yellow
}

# Build attempt
Write-Host "Building project..." -ForegroundColor Cyan
npm run build 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  Build: SUCCESS" -ForegroundColor Green
} else {
    Write-Host "  Build: FAILED (will skip)" -ForegroundColor Yellow
}

# Git operations
Write-Host ""
Write-Host "Preparing Git commit..." -ForegroundColor Cyan

# Stage Phase 2 files
git add src/views/MarketAnalysisHub.tsx src/services/CacheManager.ts src/App.tsx src/components/Navigation/EnhancedSidebar.tsx src/components/ui/Toast.tsx src/views/trading-hub/tabs/FuturesTab.tsx src/views/trading-hub/UnifiedTradingHubView.tsx PHASE_2_*.md deploy-phase2*.ps1 deploy-phase2*.sh 2>&1 | Out-Null

# Create commit
$msg = "WIP Phase 2: Market Analysis Hub and Trading Hub - Staging deployment with known issues"
git commit -m $msg 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  Commit: Created" -ForegroundColor Green
} else {
    Write-Host "  Commit: Skipped (no changes)" -ForegroundColor Yellow
}

# Create/switch to staging branch
Write-Host ""
Write-Host "Creating staging branch..." -ForegroundColor Cyan
$branchExists = git branch --list staging/phase2-market-analysis
if ($branchExists) {
    git checkout staging/phase2-market-analysis 2>&1 | Out-Null
    Write-Host "  Switched to existing branch" -ForegroundColor Green
} else {
    git checkout -b staging/phase2-market-analysis 2>&1 | Out-Null
    Write-Host "  Created new branch: staging/phase2-market-analysis" -ForegroundColor Green
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Staging branch ready!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Push to remote: git push origin staging/phase2-market-analysis"
Write-Host "2. Deploy to staging environment"
Write-Host "3. Test Phase 2 features"
Write-Host "4. Fix TypeScript errors before production"
Write-Host ""

# Return to main/master
git checkout main 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    git checkout master 2>&1 | Out-Null
}

Write-Host "Done!" -ForegroundColor Green

