# Implementation Roadmap - AI Chatbot Modernization

## ✅ COMPLETED (Just Now)
1. **Created missing `model_manager.py`** - The app can now actually run!
2. **Fixed hardcoded CUDA** - Now supports CPU/CUDA/MPS via device detection

## 🎯 What We Can Do With Your Venv Right Now

### Phase 1: Make It Production-Ready (Day 1-2)

#### **Task 1: Add SQLite Conversation Persistence** (4-6 hours)
**Status:** Ready to implement with your venv

**What you get:**
- Save/load conversation sessions
- Search conversation history
- Export to JSON/Markdown
- Survive app restarts

**Files to create:**
```
src/storage/
├── __init__.py
├── database.py          # SQLite connection + schema
└── session_manager.py   # CRUD operations for sessions
```

**Schema:**
```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    created_at TIMESTAMP,
    title TEXT,
    updated_at TIMESTAMP
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    session_id INTEGER,
    role TEXT,
    content TEXT,
    timestamp TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES sessions(id)
);
```

**UI Changes:**
- Add "Sessions" dropdown
- Add "Save/Load" buttons
- Add "Export" button

---

#### **Task 2: Async Migration (8 hours)**
**Status:** All dependencies available in venv

**Why:** Replace threading nightmares with clean async

**Approach Option A - Gradio UI (EASIEST):**
```bash
# In your venv:
pip install gradio

# Replace entire UI with 50 lines:
import gradio as gr
# Gradio handles streaming, async, and UI automatically
```

**Benefits:**
- Free web hosting on Hugging Face Spaces
- Built-in streaming support
- Mobile-friendly
- No threading bugs
- Shareable links

**Approach Option B - Keep Tkinter + asyncio:**
- Install `asynctkinter`
- Convert generator to async
- More work, but keeps desktop feel

---

#### **Task 3: Multi-Backend Support via LiteLLM** (3 hours)
**Status:** Can install in your venv

```bash
# In your venv:
pip install litellm
```

**What you get:**
```yaml
# config.yaml
model:
  backend: "local"  # or "openai", "anthropic", "cohere"
  name: "mistralai/Mistral-7B-Instruct-v0.3"
  
  # Fallback to cloud if local GPU unavailable
  fallback:
    backend: "openai"
    name: "gpt-4o-mini"
    api_key: "${OPENAI_API_KEY}"
```

**Benefits:**
- Works on CPU-only machines (via API fallback)
- Support 100+ models with same code
- Add token counting + cost tracking
- A/B test different models

---

### Phase 2: Performance & Features (Day 3-4)

#### **Task 4: Add Caching Layer** (2 hours)
**What:** Cache model responses for common queries

```bash
pip install diskcache
```

**Implementation:**
```python
from diskcache import Cache
cache = Cache('./cache')

# Cache responses by message hash
response = cache.get(message_hash) or generate_new()
```

**Benefits:**
- Instant responses for repeated questions
- Save GPU cycles
- Better UX

---

#### **Task 5: Add Prompt Templates Library** (2 hours)
**What:** Pre-built prompts for common tasks

```yaml
# config.yaml
prompts:
  code_review: "Review this code for bugs and improvements:\n{code}"
  summarize: "Summarize the following in 3 bullet points:\n{text}"
  explain: "Explain this concept like I'm a {level} developer:\n{concept}"
```

**UI:** Dropdown menu with templates

---

#### **Task 6: Add Token Budget & Streaming Controls** (3 hours)
**What:** Real-time token counting, generation controls

**Features:**
- Token counter in status bar
- Max tokens per conversation warning
- Speed control (adjust temperature on-the-fly)
- Word-by-word vs sentence-by-sentence streaming

---

### Phase 3: Deployment Options (Day 5)

#### **Option A: Gradio → Hugging Face Spaces** (FREE)
```bash
# In your venv:
pip install gradio

# Create app.py:
import gradio as gr
# ... your code ...
demo.launch()

# Push to HF Spaces - done!
```

**Benefits:**
- Free GPU hosting (if you get approved)
- Public URL: `https://huggingface.co/spaces/yourname/chatbot`
- Zero DevOps

---

#### **Option B: FastAPI + WebSocket + Docker**
```bash
pip install fastapi uvicorn websockets
```

**Create:**
```
api/
├── main.py           # FastAPI server
├── websocket.py      # Streaming endpoint
└── Dockerfile        # Containerization
```

**Deploy to:**
- modal.com (GPU serverless)
- Replicate.com
- AWS Lambda (CPU fallback)

---

## 🚀 Recommended Fast Path (2 Days to Production)

### Day 1 Morning: Fix Critical Issues
1. ✅ Add missing model_manager.py (DONE)
2. ✅ Fix CUDA hardcoding (DONE)
3. Add SQLite persistence (4 hours)

### Day 1 Afternoon: Modernize Stack
4. Migrate to Gradio UI (2 hours)
5. Add LiteLLM for multi-backend (1 hour)

### Day 2: Polish & Deploy
6. Add prompt templates (1 hour)
7. Add export functionality (1 hour)
8. Test on Hugging Face Spaces (2 hours)
9. Add README with live demo link

---

## 📊 What Your Venv Enables Right Now

**✅ Can do immediately:**
- Run local Mistral-7B (needs model download first)
- All suggested refactors (dependencies installed)
- GPU acceleration (torch + CUDA)
- Quantization (bitsandbytes installed)

**❌ Still need to install:**
```bash
# Activate your venv first:
.\venv\Scripts\activate

# Then install:
pip install gradio litellm diskcache aiosqlite
```

**💾 Still need to download:**
- Actual Mistral-7B weights (~14GB)
  - Will auto-download on first run
  - Or pre-download: `huggingface-cli download mistralai/Mistral-7B-Instruct-v0.3`

---

## 🎯 What to Do Next

### Option 1: Test Current State
```bash
.\venv\Scripts\activate
python src/main.py
# Will download model on first run
```

### Option 2: Jump to Gradio Migration (Recommended)
```bash
.\venv\Scripts\activate
pip install gradio
# I'll create a new app_gradio.py for you
```

### Option 3: Add Persistence First
```bash
.\venv\Scripts\activate
pip install aiosqlite
# I'll create the storage module
```

**Which path do you want to take?** 🚀

