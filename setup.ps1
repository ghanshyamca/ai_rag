# Setup and Run Script for RAG Q&A Bot
# This script automates the setup process

Write-Host "`n╔═══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   RAG Q&A Bot - Automated Setup              ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+ first." -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "`nCreating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "⚠️  Virtual environment already exists. Skipping..." -ForegroundColor Yellow
} else {
    python -m venv venv
    if ($?) {
        Write-Host "✅ Virtual environment created" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment
Write-Host "`nActivating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
if ($?) {
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
if ($?) {
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Create .env file if it doesn't exist
Write-Host "`nConfiguring environment..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "⚠️  .env file already exists. Skipping..." -ForegroundColor Yellow
} else {
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Created .env file" -ForegroundColor Green
    Write-Host "`n⚠️  IMPORTANT: Please edit .env and add your OPENAI_API_KEY" -ForegroundColor Yellow
    
    $response = Read-Host "`nDo you want to enter your OpenAI API key now? (y/n)"
    if ($response -eq 'y') {
        $apiKey = Read-Host "Enter your OpenAI API key"
        if ($apiKey) {
            (Get-Content ".env") -replace 'your_openai_api_key_here', $apiKey | Set-Content ".env"
            Write-Host "✅ API key configured" -ForegroundColor Green
        }
    }
}

# Check if .env has API key
$envContent = Get-Content ".env" -Raw
if ($envContent -match "your_openai_api_key_here") {
    Write-Host "`n⚠️  WARNING: You still need to set your OPENAI_API_KEY in .env file" -ForegroundColor Red
    Write-Host "Edit the .env file and replace 'your_openai_api_key_here' with your actual API key" -ForegroundColor Yellow
    
    $continue = Read-Host "`nDo you want to continue anyway? (y/n)"
    if ($continue -ne 'y') {
        exit 0
    }
}

Write-Host "`n╔═══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Setup Complete!                             ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Make sure your OPENAI_API_KEY is set in .env file" -ForegroundColor White
Write-Host "2. Run: python main.py" -ForegroundColor White
Write-Host "   (This will crawl the website and build the knowledge base)" -ForegroundColor Gray
Write-Host "3. Run: python api.py" -ForegroundColor White
Write-Host "   (This will start the API server)" -ForegroundColor Gray
Write-Host "4. Test: Visit http://localhost:8000/docs" -ForegroundColor White
Write-Host "   (Or run: .\test_api.ps1)" -ForegroundColor Gray

$buildNow = Read-Host "`nDo you want to build the knowledge base now? (y/n)"
if ($buildNow -eq 'y') {
    Write-Host "`nBuilding knowledge base..." -ForegroundColor Yellow
    python main.py
    
    if ($?) {
        Write-Host "`n✅ Knowledge base built successfully!" -ForegroundColor Green
        
        $startApi = Read-Host "`nDo you want to start the API server now? (y/n)"
        if ($startApi -eq 'y') {
            Write-Host "`nStarting API server..." -ForegroundColor Yellow
            Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
            python api.py
        } else {
            Write-Host "`nTo start the API server later, run: python api.py" -ForegroundColor Yellow
        }
    }
}
