# PowerShell Script to Push to GitHub
# Run this in PowerShell

Write-Host "🚀 Preparing SmartCareer for GitHub..." -ForegroundColor Green

# Navigate to project directory
Set-Location "c:\Users\sheet\Downloads\CARRER GUIDANCE"

# Check if git is initialized
if (-not (Test-Path ".git")) {
    Write-Host "📦 Initializing Git repository..." -ForegroundColor Yellow
    git init
} else {
    Write-Host "✅ Git already initialized" -ForegroundColor Green
}

# Add all files
Write-Host "📁 Adding files..." -ForegroundColor Yellow
git add .

# Commit
Write-Host "💾 Committing changes..." -ForegroundColor Yellow
git commit -m "Deploy SmartCareer Platform to Render"

Write-Host ""
Write-Host "✅ Local repository ready!" -ForegroundColor Green
Write-Host ""
Write-Host "📌 NEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. Go to https://github.com/new" -ForegroundColor White
Write-Host "2. Repository name: smartcareer" -ForegroundColor White
Write-Host "3. Description: AI-Powered Career Guidance Platform" -ForegroundColor White
Write-Host "4. Keep it PUBLIC or PRIVATE (your choice)" -ForegroundColor White
Write-Host "5. DON'T initialize with README" -ForegroundColor White
Write-Host "6. Click 'Create repository'" -ForegroundColor White
Write-Host ""
Write-Host "7. Then run these commands (GitHub will show them):" -ForegroundColor Yellow
Write-Host ""
Write-Host "   git remote add origin https://github.com/YOUR_USERNAME/smartcareer.git" -ForegroundColor Cyan
Write-Host "   git branch -M main" -ForegroundColor Cyan
Write-Host "   git push -u origin main" -ForegroundColor Cyan
Write-Host ""
Write-Host "Replace YOUR_USERNAME with your actual GitHub username" -ForegroundColor Yellow
