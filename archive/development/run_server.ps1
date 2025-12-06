# PowerShell script to set environment variables and run the server
# Usage: .\run_server.ps1

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Crypto Intelligence Hub - Server Startup" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Set environment variables
Write-Host "[1/3] Setting environment variables..." -ForegroundColor Yellow
$env:HF_TOKEN = "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"
$env:HF_MODE = "public"
$env:PORT = "7860"

Write-Host "  ✓ HF_TOKEN set" -ForegroundColor Green
Write-Host "  ✓ HF_MODE set to: public" -ForegroundColor Green
Write-Host "  ✓ PORT set to: 7860" -ForegroundColor Green
Write-Host ""

# Run tests
Write-Host "[2/3] Running system tests..." -ForegroundColor Yellow
python test_fixes.py
$testResult = $LASTEXITCODE

if ($testResult -eq 0) {
    Write-Host "`n  ✓ All tests passed!" -ForegroundColor Green
} else {
    Write-Host "`n  ⚠ Some tests failed, but continuing..." -ForegroundColor Yellow
}
Write-Host ""

# Start server
Write-Host "[3/3] Starting server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Server will be available at:" -ForegroundColor Cyan
Write-Host "  • Main Dashboard: http://localhost:7860/" -ForegroundColor White
Write-Host "  • AI Tools: http://localhost:7860/ai-tools" -ForegroundColor White
Write-Host "  • API Docs: http://localhost:7860/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

python api_server_extended.py

