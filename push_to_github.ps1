# GitHub Push Helper Script
# Run this after creating your GitHub repository

Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host "               GITHUB PUSH HELPER                 " -ForegroundColor Yellow
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if already have remote
$hasRemote = git remote -v 2>&1
if ($hasRemote -match "origin") {
    Write-Host "⚠️  Remote 'origin' already exists. Removing it..." -ForegroundColor Yellow
    git remote remove origin
}

Write-Host "📝 STEP 1: Enter your GitHub username" -ForegroundColor Green
Write-Host ""
$username = Read-Host "GitHub Username"

Write-Host ""
Write-Host "🔗 Adding remote repository..." -ForegroundColor Yellow
git remote add origin "https://github.com/$username/smartcareer.git"

Write-Host ""
Write-Host "🌿 Setting main branch..." -ForegroundColor Yellow
git branch -M main

Write-Host ""
Write-Host "🚀 Pushing to GitHub..." -ForegroundColor Yellow
Write-Host ""

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=================================================================================" -ForegroundColor Green
    Write-Host "               ✅ SUCCESS! CODE PUSHED TO GITHUB!                " -ForegroundColor Green
    Write-Host "=================================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your repository: https://github.com/$username/smartcareer" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📋 NEXT STEP: Deploy to Render" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Go to: https://render.com" -ForegroundColor White
    Write-Host "2. Sign up with GitHub" -ForegroundColor White
    Write-Host "3. Click 'New +' → 'Web Service'" -ForegroundColor White
    Write-Host "4. Connect 'smartcareer' repository" -ForegroundColor White
    Write-Host "5. Configure and deploy!" -ForegroundColor White
    Write-Host ""
    Write-Host "See DEPLOY_NOW.md for detailed instructions!" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Push failed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "This usually means:" -ForegroundColor Yellow
    Write-Host "  1. GitHub repository doesn't exist yet" -ForegroundColor White
    Write-Host "     → Create it at: https://github.com/new" -ForegroundColor White
    Write-Host "  2. Wrong username entered" -ForegroundColor White
    Write-Host "  3. Not logged into Git" -ForegroundColor White
    Write-Host "     → Run: gh auth login" -ForegroundColor White
    Write-Host ""
}

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
