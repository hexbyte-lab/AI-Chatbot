# Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Prerequisites
- Python 3.8+
- NVIDIA GPU with 12GB+ VRAM (recommended) or CPU
- 20GB free disk space for model

---

## Option 1: Gradio Web UI (Recommended)

### 1. Install New Dependencies
```bash
# Activate your venv
.\venv\Scripts\activate

# Install Gradio
pip install gradio
```

### 2. Run Basic Web UI
```bash
python app_gradio.py
```

**Features:**
- Modern web interface
- Works on any device with browser
- Streaming responses
- Export to JSON/Markdown
- Better controls

**Access:** Opens automatically in browser at `http://localhost:7860`

---

## Option 2: Gradio with Persistence (Best)

### 1. Run Persistent Version
```bash
# Activate your venv
.\venv\Scripts\activate

python app_gradio_persistent.py
```

**Features:**
- Everything from basic Gradio +
- SQLite conversation storage
- Session management (save/load/delete)
- Search conversations
- Database statistics
- Survives restarts

**Access:** Opens automatically at `http://localhost:7860`

---

## Option 3: Multi-Backend (Cloud APIs)

### 1. Install LiteLLM
```bash
pip install litellm
```

### 2. Configure Backend
Edit `config/config-enhanced.yaml`:

```yaml
model:
  backend: "openai"  # or "anthropic", "cohere", etc.
  name: "gpt-4o-mini"
  backend_config:
    api_key: "your-api-key-here"  # or set via OPENAI_API_KEY env var
```

### 3. Set Environment Variable (Recommended)
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-key-here"

# Windows CMD
set OPENAI_API_KEY=sk-your-key-here

# Linux/Mac
export OPENAI_API_KEY="sk-your-key-here"
```

### 4. Run with LiteLLM Wrapper
Create a new launcher file `app_multi_backend.py`:

```python
from src.core.llm_wrapper import LLMWrapper

# Initialize with enhanced config
llm = LLMWrapper("config/config-enhanced.yaml")
llm.load_model()

# Use in your app
messages = [{"role": "user", "content": "Hello!"}]
response = llm.generate(messages, stream=False)
print(response)
```

**Benefits:**
- No GPU required (uses cloud APIs)
- Works on any machine
- Support 100+ models
- Easy A/B testing

---

## 📂 File Overview

### What Each App Does:

| File | Description | Persistence | UI Type | Backend |
|------|-------------|------------|---------|---------|
| `app_gradio_persistent.py` | Advanced web | ✅ SQLite | Web | Local + Multi-backend |
| `app_gradio.py` | Basic web | ❌ In-memory | Web | Local + Multi-backend |

### Which Should You Use?

**For daily use:** `app_gradio_persistent.py` ⭐ **RECOMMENDED**
**For quick testing:** `app_gradio.py`
**For deployment:** `app_gradio_persistent.py` + LiteLLM

---

## 🎨 Using Prompt Templates

### 1. List Available Templates
```python
from src.utils.prompts import PromptManager

pm = PromptManager()
templates = pm.list()

for t in templates:
    print(f"{t.name}: {t.description}")
```

### 2. Use a Template
```python
# Code review template
prompt = pm.format_prompt(
    "code_review",
    code="def add(a, b): return a + b",
    language="python"
)

print(prompt)
# Output:
# Review the following code for bugs, security issues, and improvements:
# ```python
# def add(a, b): return a + b
# ```
# Provide specific, actionable feedback.
```

### 3. Add Custom Template
```python
from src.utils.prompts import PromptTemplate

custom = PromptTemplate(
    name="my_template",
    template="Help me with {task}",
    description="My custom prompt",
    variables=["task"],
    category="custom"
)

pm.add_template(custom)
pm.save_to_file()  # Saves to config/prompts.yaml
```

---

## 💾 Working with Persistent Storage

### Create a New Session
```python
from src.storage import SessionManager

sm = SessionManager()
session_id = sm.create_session(title="My First Chat")
```

### Add Messages
```python
sm.add_message(session_id, "user", "Hello!")
sm.add_message(session_id, "assistant", "Hi! How can I help?")
```

### Load a Session
```python
messages = sm.get_messages(session_id)
for msg in messages:
    print(f"{msg['role']}: {msg['content']}")
```

### Search Sessions
```python
results = sm.search_sessions("python code")
for session in results:
    print(f"{session['title']} - {session['message_count']} messages")
```

### Export Session
```python
# JSON export
data = sm.export_session_json(session_id)
print(data)

# Markdown export
markdown = sm.export_session_markdown(session_id)
print(markdown)
```

---

## 🔧 Configuration Tips

### Adjust Generation Settings

Edit `config/config.yaml` or `config/config-enhanced.yaml`:

```yaml
generation:
  max_new_tokens: 1024  # Longer responses
  temperature: 0.3      # More focused (0.1-1.0)
  top_p: 0.95           # Nucleus sampling
  top_k: 40             # Diversity control
```

**Temperature Guide:**
- `0.1-0.3`: Focused, deterministic (good for code)
- `0.7`: Balanced (default)
- `1.0-2.0`: Creative, diverse (good for writing)

### Enable 4-bit Quantization (Save VRAM)

```yaml
model:
  load_in_4bit: true  # Reduces VRAM by ~75%
  torch_dtype: "float16"
```

**Tradeoff:** Slightly lower quality, much less memory.

### Change Port

```yaml
ui:
  gradio:
    server_port: 8080  # Default is 7860
```

---

## 🐛 Troubleshooting

### Issue: "Model not found" or Download Fails
**Solution:** Pre-download the model:
```bash
# Activate venv first
.\venv\Scripts\activate

# Download model
python -c "from transformers import AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('mistralai/Mistral-7B-Instruct-v0.3')"
```

### Issue: Out of Memory (CUDA OOM)
**Solutions:**
1. Enable 4-bit quantization (see config above)
2. Reduce `max_new_tokens`
3. Use smaller model
4. Use cloud API via LiteLLM

### Issue: Slow Generation
**Solutions:**
1. Ensure GPU is being used (check "Device: CUDA" in UI)
2. Reduce `max_new_tokens`
3. Use quantization
4. Close other GPU programs

### Issue: "CUDA not available"
**Solutions:**
1. Install CUDA-enabled PyTorch:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cu118
```
2. Or use CPU (much slower):
```yaml
model:
  device_map: "cpu"
```

### Issue: Web UI Won't Open
**Solutions:**
1. Check if port 7860 is in use
2. Change port in config
3. Manually open: `http://localhost:7860`
4. Check firewall settings

---

## 📊 Performance Tips

### Faster First Response
The first response is slow because the model loads. Solutions:
1. Keep app running (don't close)
2. Use persistent web version (stays loaded)
3. Pre-load model in background

### Reduce VRAM Usage
```yaml
model:
  load_in_4bit: true        # Biggest impact
  torch_dtype: "float16"    # vs float32
  device_map: "auto"        # Smart allocation
```

### Speed Up Response Time
1. Use GPU (20-50x faster than CPU)
2. Reduce `max_new_tokens` (proportional speedup)
3. Use `temperature: 0.1` (less sampling)
4. Use cloud APIs for instant responses

---

## 🚀 Next Steps

### 1. **Try the Gradio Persistent Version** (Recommended)
```bash
python app_gradio_persistent.py
```

### 2. **Explore Prompt Templates**
Open `config/prompts.yaml` and add your own.

### 3. **Set Up Cloud Fallback**
Configure LiteLLM for when GPU isn't available.

### 4. **Deploy to Production**
- Docker containerization
- Hugging Face Spaces (free hosting)
- Modal.com (serverless GPU)

### 5. **Report Bugs**
Found issues? Document in BUGS_AND_IMPROVEMENTS.md

---

## 📚 Additional Resources

- **HuggingFace Docs:** https://huggingface.co/docs/transformers
- **Gradio Docs:** https://gradio.app/docs
- **LiteLLM Docs:** https://docs.litellm.ai/

---

## 💡 Pro Tips

1. **Save Your Conversations:** Use persistent version to never lose data
2. **Use Templates:** Save time with pre-built prompts
3. **Adjust Temperature:** Lower for code, higher for creative writing
4. **Export Regularly:** Backup important conversations to markdown
5. **Monitor VRAM:** Keep task manager open to watch GPU usage

---

## 🎉 You're Ready!

Pick your preferred option above and start chatting! For the best experience, we recommend:

```bash
python app_gradio_persistent.py
```

**Happy chatting! 🤖**

