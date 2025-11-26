#!/bin/bash
# AI Chatbot - Quick Installation and Launch Script
# For Linux/Mac

echo "🤖 AI Chatbot - Installation & Launch"
echo "======================================"
echo ""

# Check if venv exists
if [ -d "venv" ]; then
    echo "✅ Virtual environment found"
else
    echo "⚠️ Virtual environment not found. Creating..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate venv
echo "Activating virtual environment..."
source venv/bin/activate

# Check if Gradio is installed
if python -c "import gradio" 2>/dev/null; then
    echo "✅ Gradio already installed"
else
    echo "📦 Installing new dependencies (Gradio, LiteLLM)..."
    pip install gradio litellm --quiet
    echo "✅ Dependencies installed"
fi

echo ""
echo "🚀 Launching AI Chatbot..."
echo ""
echo "Choose your version:"
echo "1. Gradio Persistent (Recommended) - Full features + storage"
echo "2. Gradio Basic - Simple web UI"
echo "3. Original Desktop (tkinter) - Desktop app"
echo ""

read -p "Enter choice (1-3, default: 1): " choice
choice=${choice:-1}

case $choice in
    1)
        echo ""
        echo "🌟 Starting Gradio Persistent version..."
        echo "Features: Web UI, SQLite storage, session management, export"
        echo ""
        python app_gradio_persistent.py
        ;;
    2)
        echo ""
        echo "🌐 Starting Gradio Basic version..."
        echo "Features: Web UI, streaming, basic features"
        echo ""
        python app_gradio.py
        ;;
    3)
        echo ""
        echo "🖥️ Starting Desktop version..."
        echo "Features: Desktop GUI, basic features"
        echo ""
        python src/main.py
        ;;
    *)
        echo "Invalid choice. Starting recommended version (Gradio Persistent)..."
        python app_gradio_persistent.py
        ;;
esac

