# AI Chatbot with Memory

A production-ready AI chatbot application with conversation memory, real-time streaming responses, and interrupt/continue functionality.

## Features

- 🤖 Powered by Mistral-7B-Instruct
- 💾 Full conversation memory
- ⚡ Real-time streaming responses
- ⏸️ Interrupt and continue generation
- 🎨 Modern dark-themed GUI
- 🔧 Configurable via YAML

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

## Usage

```bash
python src/main.py
```

## Configuration

Edit `config/config.yaml` to customize:
- Model selection
- Generation parameters
- UI settings

## Project Structure

```
src/
├── main.py              # Application entry point
├── models/              # Model loading and management
├── ui/                  # GUI components
├── core/                # Core logic (conversation, generation)
└── utils/               # Utilities and helpers
```

## License

MIT License - See LICENSE file for details

## Contributing

Pull requests are welcome! Please read CONTRIBUTING.md first.

## Acknowledgments

- Mistral AI for the base model
- HuggingFace for transformers library
