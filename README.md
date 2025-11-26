# AI Chatbot with Memory

A **production-ready AI chatbot** with conversation persistence, multi-backend support, web UI, and advanced features.

## 🚀 Now Modernized with:

- 🌐 **Modern Web UI** (Gradio) - Works on any device
- 💾 **SQLite Persistence** - Never lose conversations
- 🔄 **Multi-Backend Support** - Local + Cloud (OpenAI, Claude, etc.)
- 📝 **Prompt Templates** - 10+ built-in templates for common tasks
- 📤 **Export** - Save conversations as JSON/Markdown
- 🔍 **Search** - Find past conversations instantly
- 🎯 **Session Management** - Organize multiple conversations

## Features

### Original (tkinter):
- 🤖 Powered by Mistral-7B-Instruct
- 💾 In-memory conversation history
- ⚡ Real-time streaming responses
- ⏸️ Interrupt and continue generation
- 🎨 Desktop GUI

### New (Gradio + Enhanced):
- ✨ Everything above **PLUS:**
- 🌐 Beautiful web interface
- 💾 **Permanent storage** (SQLite)
- 🔄 **100+ AI models** supported (via LiteLLM)
- 📝 Pre-built prompt templates
- 📊 Statistics and analytics
- 🔧 Advanced configuration options

## Requirements

- Python 3.8+
- NVIDIA GPU with CUDA support (12GB+ VRAM recommended)
- 20GB free disk space

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/AI-Chatbot.git
cd AI-Chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### **Recommended: Modern Web Version**
```bash
# Install dependencies
pip install -r requirements.txt

# Run persistent web UI (best option)
python app_gradio_persistent.py
```

Opens automatically in your browser at `http://localhost:7860`

### **Alternative: Original Desktop Version**
```bash
python src/main.py
```

---

## 📖 Full Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Detailed usage guide
- **[MODERNIZATION_SUMMARY.md](MODERNIZATION_SUMMARY.md)** - What's new
- **[BUGS_AND_IMPROVEMENTS.md](BUGS_AND_IMPROVEMENTS.md)** - All improvements
- **[IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md)** - Technical details

## Configuration

Edit `config/config.yaml` to customize:
- Model selection
- Generation parameters
- UI settings

## Project Structure

```
src/
├── main.py                    # Original desktop app entry point
├── models/
│   └── model_manager.py       # Model loading & management
├── storage/                   # NEW: Persistence layer
│   ├── database.py           # SQLite wrapper
│   └── session_manager.py    # CRUD operations
├── core/
│   ├── conversation.py       # Conversation state
│   ├── generator.py          # Response generation
│   └── llm_wrapper.py        # NEW: Multi-backend support
├── ui/
│   ├── chat_window.py        # Desktop UI components
│   └── components.py         # Reusable widgets
└── utils/
    ├── logger.py             # Logging
    └── prompts.py            # NEW: Prompt templates

# New Web Apps (Recommended)
app_gradio.py                 # Basic web UI
app_gradio_persistent.py      # Advanced web UI with storage ⭐
```

## License

MIT License - See LICENSE file for details

## Contributing

Pull requests are welcome! Please read CONTRIBUTING.md first.

## 🎯 Which Version Should I Use?

| Version | Best For | Pros | Cons |
|---------|----------|------|------|
| **app_gradio_persistent.py** ⭐ | Daily use, production | Web UI, persistence, all features | Requires Gradio |
| **app_gradio.py** | Quick testing | Simple, fast setup | No persistence |
| **src/main.py** | Desktop preference | Standalone, no web server | Limited features |

**Recommendation:** Use `app_gradio_persistent.py` for the best experience!

---

## 🔥 New Features

### Prompt Templates
```python
from src.utils.prompts import PromptManager

pm = PromptManager()
prompt = pm.format_prompt("code_review", 
    code="your code here",
    language="python"
)
```

### Multi-Backend Support
```yaml
# config/config-enhanced.yaml
model:
  backend: "openai"  # or "local", "anthropic", "cohere"
  name: "gpt-4o-mini"
```

### Session Management
- Save/load conversations
- Search history
- Export to JSON/Markdown
- Organize multiple chats

---

## 🚀 Deployment

### Hugging Face Spaces (Free)
```bash
# Push to HF Spaces for free hosting
git push hf main
```

### Docker
```bash
# Coming soon - containerized deployment
docker build -t ai-chatbot .
docker run -p 7860:7860 ai-chatbot
```

---

## Acknowledgments

- Mistral AI for the base model
- HuggingFace for transformers library
- Gradio for the web UI framework
- LiteLLM for multi-provider support
