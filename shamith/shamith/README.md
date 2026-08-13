# 🏗️ Construction Intelligence Hub

**AI-Powered Smart Construction Planning and Estimation Platform**

Powered by **Llama 3.1** running locally via **Ollama** — no cloud APIs, complete privacy.

---

## ✨ Features

| Page | Description |
|------|-------------|
| **Home** | Dashboard with live metrics, AI status, and quick navigation |
| **Project Details** | Enter project info + get **AI Project Insights** |
| **House Planner** | Dynamic room management + **AI Room Optimization** |
| **Material Estimation** | Engineering-formula-based quantities + **AI Material Analysis** |
| **Cost Estimation** | 5-category cost breakdown with charts + **AI Cost Optimization** |
| **Report** | Complete project summary with CSV/PDF export + **AI Summary** |
| **AI Chat** | Full streaming chat with Llama 3.1 (conversation memory) |
| **About** | Tech stack, milestones, and supported models |

---

## 🚀 Quick Start

### Prerequisites

1. **Python 3.9+**
2. **Ollama** — Install from [ollama.com](https://ollama.com)
3. **Llama 3.1** model pulled:

```bash
ollama pull llama3.1
```

### Installation

```bash
# Clone the project
cd Construction_Intelligence_Hub

# Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Run

```bash
# Make sure Ollama is running
ollama serve

# In another terminal, start the app
streamlit run app.py
```

---

## 🏛️ Architecture

```
Construction_Intelligence_Hub/
├── .streamlit/config.toml          # Streamlit theme configuration
├── backend/
│   ├── __init__.py                 # Package exports
│   ├── config.py                   # Central configuration (model, prompts, prices)
│   ├── llama_service.py            # Ollama API communication (streaming + single-shot)
│   ├── prompt_manager.py           # AI prompt templates for all features
│   ├── memory_manager.py           # Conversation history with sliding window
│   ├── material_calculator.py      # Engineering formulas for material estimation
│   ├── cost_calculator.py          # Cost estimation with per-unit pricing
│   ├── logger.py                   # Structured file + console logging
│   └── utils.py                    # Shared helpers (formatting, validation)
├── utils/
│   └── ui_utils.py                 # Custom CSS injection
├── logs/                           # Auto-created log files
├── app.py                          # Streamlit entry point + routing
├── views.py                        # All page rendering with AI integration
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## 🤖 AI Features

### Streaming Chat
The AI Chat page provides real-time streaming responses from Llama 3.1. Your conversation history is maintained within the session (last 20 messages).

### AI Analysis Buttons
Every major page has an AI analysis button:
- **✨ AI Project Insights** — Analyzes your project data and gives recommendations
- **🧠 AI Room Optimization** — Suggests optimal room dimensions and layout
- **🔬 AI Material Analysis** — Reviews material estimates and identifies gaps
- **💡 AI Cost Optimization** — Budget optimization and cost-saving strategies
- **📋 AI Project Summary** — Comprehensive executive summary

### Conversation Memory
The AI remembers your project context and previous messages. Ask "How much cement do I need?" and it knows which project you're referring to.

---

## ⚙️ Configuration

All settings are in `backend/config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `MODEL_NAME` | `llama3.1` | Ollama model to use |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama API endpoint |
| `TEMPERATURE` | `0.7` | AI creativity level (0.0–1.0) |
| `MAX_TOKENS` | `2048` | Maximum response length |
| `TIMEOUT` | `120` | API timeout in seconds |

### Switching Models

Change `MODEL_NAME` in `backend/config.py` to any model you have pulled:

```python
MODEL_NAME = "qwen3:14b"      # More detailed analysis
MODEL_NAME = "gemma3:4b"      # Faster responses
MODEL_NAME = "qwen2.5:7b"     # Balanced
```

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Ollama Offline" badge | Run `ollama serve` in terminal |
| "Model Not Found" | Run `ollama pull llama3.1` |
| Slow responses | Try a smaller model like `gemma3:4b` |
| Timeout errors | Increase `TIMEOUT` in `backend/config.py` |
| Import errors | Run `pip install -r requirements.txt` |

---

## 📝 Example Prompts

Try these in the AI Chat:
- "How much cement do I need for my 2500 sq ft villa?"
- "What type of foundation should I use for 2 floors?"
- "How can I reduce my construction cost by 20%?"
- "Compare clay bricks vs fly-ash bricks"
- "What is the recommended steel ratio for columns?"
- "Suggest a construction timeline for my project"

---

## 🛣️ Roadmap

- [x] **Milestone 1** — Professional Streamlit Frontend
- [x] **Milestone 2** — Llama 3.1 AI Integration via Ollama
- [ ] **Milestone 3** — Multi-model support, blueprint analysis, real-time pricing
- [ ] **Milestone 4** — Auth, database, deployment, PWA

---

© 2026 Construction Intelligence Hub Project
