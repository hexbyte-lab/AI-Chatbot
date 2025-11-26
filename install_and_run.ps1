# AI Chatbot - Quick Installation and Launch Script
# For Windows PowerShell

Write-Host "🤖 AI Chatbot - Installation & Launch" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if venv exists
if (Test-Path "venv") {
    Write-Host "✅ Virtual environment found" -ForegroundColor Green
} else {
    Write-Host "⚠️ Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& "venv\Scripts\Activate.ps1"

# Check if Gradio is installed
$gradioInstalled = python -c "import gradio" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "📦 Installing new dependencies (Gradio, LiteLLM)..." -ForegroundColor Yellow
    pip install gradio litellm --quiet
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✅ Gradio already installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "🚀 Launching AI Chatbot..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Choose your version:" -ForegroundColor Yellow
Write-Host "1. Gradio Persistent (Recommended) - Full features + storage" -ForegroundColor White
Write-Host "2. Gradio Basic - Simple web UI (no persistence)" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter choice (1-2, default: 1)"

if ([string]::IsNullOrWhiteSpace($choice)) {
    $choice = "1"
}

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🌟 Starting Gradio Persistent version..." -ForegroundColor Green
        Write-Host "Features: Web UI, SQLite storage, session management, export" -ForegroundColor Gray
        Write-Host ""
        python app_gradio_persistent.py
    }
    "2" {
        Write-Host ""
        Write-Host "🌐 Starting Gradio Basic version..." -ForegroundColor Green
        Write-Host "Features: Web UI, streaming, temporary conversations" -ForegroundColor Gray
        Write-Host ""
        python app_gradio.py
    }
    default {
        Write-Host "Invalid choice. Starting recommended version (Gradio Persistent)..." -ForegroundColor Yellow
        python app_gradio_persistent.py
    }
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

