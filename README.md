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

- 🤖 Powered by Mistral-7B-Instruct (or 100+ other models via LiteLLM)
- 🌐 Beautiful web interface (Gradio)
- 💾 **Permanent storage** (SQLite persistence)
- ⚡ Real-time streaming responses
- 🎯 Session management - organize multiple conversations
- 📝 Pre-built prompt templates for common tasks
- 📤 Export conversations to JSON/Markdown
- 🔍 Search through conversation history
- 📊 Statistics and analytics dashboard
- 🔧 Advanced configuration options
- 🔄 Multi-backend support (local + cloud APIs)

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

```bash
# Install dependencies
pip install -r requirements.txt

# Run persistent web UI (recommended)
python app_gradio_persistent.py

# Or run basic version without persistence
python app_gradio.py
```

Opens automatically in your browser at `http://localhost:7860`

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
├── models/
│   └── model_manager.py       # Model loading & management
├── storage/                   # Persistence layer
│   ├── database.py           # SQLite wrapper
│   └── session_manager.py    # CRUD operations
├── core/
│   ├── conversation.py       # Conversation state
│   ├── generator.py          # Response generation
│   └── llm_wrapper.py        # Multi-backend support
└── utils/
    ├── logger.py             # Logging
    └── prompts.py            # Prompt templates

# Web Applications (at project root)
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
| **app_gradio_persistent.py** ⭐ | Daily use, production | Full features, persistence, session management | None |
| **app_gradio.py** | Quick testing, temporary chats | Simple, fast setup | No persistence |

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
