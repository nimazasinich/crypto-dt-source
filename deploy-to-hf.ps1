# Hugging Face Spaces Deployment Helper Script (PowerShell)

Write-Host "🚀 Crypto Intelligence Hub - HF Spaces Deployment" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is installed
try {
    git --version | Out-Null
} catch {
    Write-Host "❌ Git is not installed. Please install git first." -ForegroundColor Red
    exit 1
}

# Ask for UI mode
Write-Host "Choose UI mode for Hugging Face Spaces:" -ForegroundColor Yellow
Write-Host "1) Gradio UI (Recommended - Interactive dashboard)"
Write-Host "2) FastAPI + HTML (REST API with HTML frontend)"
Write-Host ""
$ui_choice = Read-Host "Enter choice (1 or 2)"

if ($ui_choice -eq "1") {
    Write-Host "✅ Setting up Gradio UI mode..." -ForegroundColor Green
    
    # Read Dockerfile
    $dockerfile = Get-Content "Dockerfile" -Raw
    
    # Update environment variables
    $dockerfile = $dockerfile -replace 'ENV USE_FASTAPI_HTML=true', 'ENV USE_FASTAPI_HTML=false'
    $dockerfile = $dockerfile -replace 'ENV USE_GRADIO=false', 'ENV USE_GRADIO=true'
    
    # Write back
    Set-Content "Dockerfile" -Value $dockerfile
    
    Write-Host "✅ Dockerfile updated for Gradio mode" -ForegroundColor Green
    
} elseif ($ui_choice -eq "2") {
    Write-Host "✅ Setting up FastAPI + HTML mode..." -ForegroundColor Green
    
    # Read Dockerfile
    $dockerfile = Get-Content "Dockerfile" -Raw
    
    # Update environment variables
    $dockerfile = $dockerfile -replace 'ENV USE_FASTAPI_HTML=false', 'ENV USE_FASTAPI_HTML=true'
    $dockerfile = $dockerfile -replace 'ENV USE_GRADIO=true', 'ENV USE_GRADIO=false'
    
    # Write back
    Set-Content "Dockerfile" -Value $dockerfile
    
    Write-Host "✅ Dockerfile updated for FastAPI mode" -ForegroundColor Green
    
} else {
    Write-Host "❌ Invalid choice. Keeping current settings." -ForegroundColor Red
}

Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Yellow
Write-Host "1. Create a new Space at: https://huggingface.co/new-space"
Write-Host "   - Choose 'Docker' as SDK"
Write-Host "   - Choose your preferred hardware tier"
Write-Host ""
Write-Host "2. Clone your new Space:"
Write-Host "   git clone https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME"
Write-Host ""
Write-Host "3. Copy files to the Space directory:"
Write-Host "   Copy-Item -Recurse -Force * C:\path\to\your\space\"
Write-Host ""
Write-Host "4. Push to HF Spaces:"
Write-Host "   cd C:\path\to\your\space\"
Write-Host "   git add ."
Write-Host "   git commit -m 'Initial deployment'"
Write-Host "   git push"
Write-Host ""
Write-Host "✅ Your app is ready to deploy!" -ForegroundColor Green
