# PowerShell script to set environment variables
# Run this before starting the server

Write-Host "Setting Hugging Face environment variables..." -ForegroundColor Cyan

$env:HF_TOKEN = "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"
$env:HF_MODE = "public"
$env:PORT = "7860"

Write-Host "✓ HF_TOKEN set" -ForegroundColor Green
Write-Host "✓ HF_MODE set to: $env:HF_MODE" -ForegroundColor Green
Write-Host "✓ PORT set to: $env:PORT" -ForegroundColor Green

Write-Host "`nVerifying settings..." -ForegroundColor Cyan
Write-Host "HF_TOKEN: $(if ($env:HF_TOKEN) { 'SET (length: ' + $env:HF_TOKEN.Length + ')' } else { 'NOT SET' })" -ForegroundColor Yellow
Write-Host "HF_MODE: $env:HF_MODE" -ForegroundColor Yellow

Write-Host "`nEnvironment variables are ready!" -ForegroundColor Green
Write-Host "Now you can run: python api_server_extended.py" -ForegroundColor Cyan

