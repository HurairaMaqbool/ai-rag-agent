<div align="center">

# ✦ Nexus AI Engine

### Advanced Retrieval-Augmented Generation · Live Web Search · Math Solver

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Groq-LPU_Inference-F55036?style=for-the-badge)](https://groq.com)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-1C3C3C?style=for-the-badge)](https://langchain.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**A production-ready, 100% professional AI research assistant powered by hybrid RAG, real-time web search, and Chain-of-Thought reasoning.**

[🚀 Quick Start](#-quick-start) · [📐 Architecture](#-architecture) · [🔌 API Reference](#-api-reference) · [🧪 Testing](#-testing) · [🛣️ Roadmap](#-roadmap)

</div>

---

## 📋 Table of Contents

- [What is Nexus AI?](#-what-is-nexus-ai)
- [Feature Highlights](#-feature-highlights)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [API Reference](#-api-reference)
- [How Each Module Works](#-how-each-module-works)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)

---

## 🤖 What is Nexus AI?

Nexus AI is a **full-stack, production-grade AI research engine** that combines:

| Capability | Description |
|---|---|
| 📄 **Document RAG** | Upload any PDF, DOCX, or TXT file and immediately ask questions about it using **Hybrid Search** (semantic + keyword) |
| 🌐 **Live Web Search** | Answers questions about current events and real-time information using DuckDuckGo, synthesized via LLM |
| 🧮 **Math Solver** | Safely evaluates mathematical expressions using a secure AST parser (no `eval()`), then explains the steps |
| 🧠 **Chain of Thought** | Every LLM response is guided by a few-shot Chain-of-Thought prompt for significantly higher accuracy |
| ⚡ **Groq LPU** | Powered by Groq's ultra-fast inference hardware running `llama-3.3-70b-versatile` |

---

## ✨ Feature Highlights

- **Hybrid Retrieval**: Combines dense semantic search (Sentence Transformers) with sparse BM25 keyword search — best of both worlds
- **Multi-format ingestion**: PDF, DOCX, TXT — auto-parsed, chunked with sliding window overlap
- **Secure Calculator**: Uses Python's `ast` module for safe math evaluation — **zero use of `eval()`**
- **Fault-tolerant LLM**: 4-model Groq fallback chain — automatically switches if one model is unavailable
- **Real health checks**: Status pill in UI reflects actual backend state (not hardcoded)
- **Non-blocking server**: Heavy ML work runs in thread pools — server handles concurrent requests
- **Content-hash deduplication**: MD5-based chunk deduplication prevents redundant context
- **DoS protection**: Expression length limits and division-by-zero guards on the calculator
- **Premium white UI**: Custom CSS glassmorphism sidebar, animated hero banner, micro-animations

---

## 🛠️ Tech Stack

```
Frontend  →  Streamlit 1.35+  (white theme, glassmorphism, custom CSS)
Backend   →  FastAPI 0.115+   (async, threadpool, CORS)
LLM       →  Groq LPU         (llama-3.3-70b-versatile, with 3 fallbacks)
Embeddings→  Sentence Transformers (all-MiniLM-L6-v2, 384-dim)
Search    →  NumpyFlatL2 (semantic) + BM25Okapi (keyword) = Hybrid
Web       →  ddgs (DuckDuckGo Search)
Parsing   →  pypdf, python-docx
```

---

## 📁 Project Structure

```
ai-rag-agent/
│
├── main.py              # FastAPI backend server
│   ├── POST /chat       # Main Q&A endpoint
│   ├── POST /upload     # Document upload & indexing
│   └── GET  /health     # Health check endpoint
│
├── rag_engine.py        # Core AI engine (all intelligence lives here)
│   ├── safe_eval()      # Secure AST math evaluator
│   ├── NumpyFlatL2      # FAISS-compatible vector index
│   └── RAGSystem        # Main orchestration class
│       ├── parse_file()       # PDF/DOCX/TXT parser
│       ├── chunk_text()       # Sliding window chunker
│       ├── add_document()     # Full ingestion pipeline
│       ├── hybrid_search()    # Semantic + BM25 fusion
│       ├── detect_intent()    # Smart query router
│       ├── calculator_tool()  # Math expression extractor
│       ├── web_search_tool()  # DuckDuckGo integration
│       ├── ask_rag()          # Document Q&A CoT prompt
│       ├── ask_web()          # Web answer CoT prompt
│       ├── ask_general()      # General knowledge prompt
│       ├── ask_math_explainer() # Step-by-step math explainer
│       └── chat()             # Main routing entry point
│
├── app.py               # Streamlit frontend UI
│
├── qa_test_suite.py     # Automated QA test suite (7 modules)
│
├── requirements.txt     # All dependencies with min versions
│
├── .streamlit/
│   └── config.toml      # Streamlit theme configuration
│
└── README.md            # This file
```

---

## 📐 Architecture

```
User (Browser)
     │
     ▼
┌─────────────────────────┐
│   Streamlit UI (8501)   │  app.py
│  ┌─────────────────┐    │  - Premium white UI
│  │  Sidebar        │    │  - File uploader
│  │  • API Key      │    │  - Real health check
│  │  • Upload Doc   │    │  - Chat interface
│  │  • Stats        │    │
│  └─────────────────┘    │
└────────┬────────────────┘
         │ HTTP POST /chat
         │ HTTP POST /upload
         │ HTTP GET  /health
         ▼
┌─────────────────────────┐
│   FastAPI Server (8000) │  main.py
│  - CORS middleware       │  - run_in_threadpool
│  - API key injection     │  - Async endpoints
│  - File temp storage     │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│              RAGSystem (rag_engine.py)           │
│                                                  │
│  detect_intent(query)                            │
│       │                                          │
│       ├── "calculator"                           │
│       │      └── safe_eval() → AST parser        │
│       │          + ask_math_explainer() → Groq   │
│       │                                          │
│       ├── "web_search"                           │
│       │      └── ddgs.text() → web results       │
│       │          + ask_web() → Groq CoT           │
│       │                                          │
│       └── "pdf_rag"                              │
│              └── hybrid_search()                 │
│                   ├── SentenceTransformer embeds  │
│                   │   └── NumpyFlatL2 search      │
│                   └── BM25Okapi keyword search    │
│                   + ask_rag() → Groq CoT          │
│                   (fallback: ask_general())        │
└──────────────────────────────────────────────────┘
         │
         ▼
   Groq LPU API
   llama-3.3-70b-versatile
   (fallback chain: llama3-70b → mixtral → gemma2)
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ (tested on 3.13)
- A free [Groq API key](https://console.groq.com)
- Windows / macOS / Linux

### 1. Clone the repository
```bash
git clone https://github.com/HurairaMaqbool/ai-rag-agent.git
cd ai-rag-agent
```

### 2. Create a virtual environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the FastAPI backend
```bash
# Windows (PowerShell)
$env:GROQ_API_KEY="gsk_your_key_here"; python main.py

# macOS / Linux
GROQ_API_KEY="gsk_your_key_here" python main.py
```
Backend will be live at → `http://localhost:8000`

### 5. Start the Streamlit frontend (new terminal)
```bash
.\venv\Scripts\activate   # Windows
streamlit run app.py
```
Frontend will open at → `http://localhost:8501`

### 6. Use it!
1. Paste your Groq API key in the sidebar
2. Upload a PDF/DOCX/TXT file
3. Click **"⚡ Process & Index Document"**
4. Ask questions in the chat!

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `GROQ_API_KEY` | Yes | Hardcoded fallback | Your Groq API key from console.groq.com |

### Streamlit Theme (`.streamlit/config.toml`)
```toml
[theme]
base = "light"
primaryColor = "#6366F1"
backgroundColor = "#F8F9FF"
secondaryBackgroundColor = "#F0F4FF"
textColor = "#1A1A2E"
font = "sans serif"
```

### Chunking Parameters (`rag_engine.py`)
```python
chunk_size = 800    # Characters per chunk
overlap    = 150    # Overlap between chunks for context continuity
top_k      = 5      # Number of chunks retrieved per query
```

### LLM Settings
```python
model       = "llama-3.3-70b-versatile"   # Primary model
temperature = 0.3                          # 0=deterministic, 1=creative
```

---

## 🔌 API Reference

### `POST /chat`
Ask the AI a question.

**Request Body:**
```json
{
  "question": "What is machine learning?",
  "api_key": "gsk_your_key_here"
}
```

**Response:**
```json
{
  "answer": "📄 **Document Answer**\n\nMachine learning is..."
}
```

**Response Prefixes by Intent:**
| Prefix | Meaning |
|---|---|
| `📄 **Document Answer**` | Answered from uploaded documents |
| `🌐 **Web Search Answer**` | Answered from live web search |
| `🧮 **Result: ...**` | Math calculation result |
| `💡 **General Answer**` | Answered from LLM general knowledge |

---

### `POST /upload`
Upload and index a document.

**Request:** `multipart/form-data` with `file` field (PDF, DOCX, or TXT)

**Response:**
```json
{
  "status": "Successfully indexed 24 chunks from report.pdf.",
  "filename": "report.pdf"
}
```

---

### `GET /health`
Check if the backend is running.

**Response:**
```json
{
  "status": "online",
  "docs_indexed": 48
}
```

---

## 🧩 How Each Module Works

### 1. Intent Detection (`detect_intent`)
The router uses regex pattern matching with clear priority:

```
Priority 1 → Calculator   (if numeric expression like "25 * 4" or keyword "calculate")
Priority 2 → Web Search   (if keywords: latest, news, today, current, 2025, price...)
Priority 3 → PDF RAG      (default — answer from documents or general knowledge)
```

### 2. Hybrid Search
Combines two retrieval methods:

```
Query → Sentence Transformer → Dense Vector → NumpyFlatL2 → Top-K semantic results
     → BM25 tokenization    → Sparse Score → BM25Okapi  → Top-K keyword results
                                              ↓
                              Merge + MD5 deduplicate → Final top-K unique chunks
```

### 3. Chain of Thought Prompting
Each intent uses a specialized prompt:

| Intent | Prompt Type | Few-Shot Examples |
|---|---|---|
| PDF RAG | Document analyst | 2 research examples |
| Web Search | News synthesizer | 1 web result example |
| General | General assistant | Chain of Thought only |
| Math | Math tutor | Step-by-step explainer |

### 4. Groq Model Fallback Chain
```python
GROQ_MODELS = [
    "llama-3.3-70b-versatile",   # Primary (fastest, smartest)
    "llama3-70b-8192",            # Fallback 1
    "mixtral-8x7b-32768",         # Fallback 2
    "gemma2-9b-it",               # Fallback 3 (always available)
]
```

---

## 🧪 Testing

Run the full automated QA test suite:

```bash
$env:PYTHONIOENCODING="utf-8"; python qa_test_suite.py
```

**Test Coverage — 7 Modules, 30+ Test Cases:**

| Module | What is Tested |
|---|---|
| Module 1 — Calculator | Addition, multiplication, division, exponentiation, modulo, negative numbers, division-by-zero guard, DoS guard |
| Module 2 — Intent Detection | 13 edge cases covering calculator, web search, and PDF RAG routing |
| Module 3 — Document Parsing | TXT parsing, key presence, chunking size, overlap, unsupported file type rejection |
| Module 4 — Vector Index | Empty index safety, add vectors, nearest-neighbour correctness, reset |
| Module 5 — Hybrid Search | Returns results, field presence, no duplicate chunks (hash check) |
| Module 6 — Calculator Tool | Expression extraction from natural language, no-number handling |
| Module 7 — Web Search | Returns string, non-empty response, graceful error handling |

**Expected output:**
```
============================================================
  NEXUS AI -- SENIOR QA EXPERT TEST SUITE
============================================================
  [PASS]  Basic addition
  [PASS]  Multiplication
  ...
  RESULT: 30/30 tests passed  (100% accuracy)
  *** ALL TESTS PASSED -- Project is 100% functional! ***
============================================================
```

---

## 🐛 Troubleshooting

### "Please set a valid GROQ_API_KEY"
**Cause:** The API key is not reaching the FastAPI process.
**Fix:** Start the server with the key pre-set:
```powershell
$env:GROQ_API_KEY="gsk_your_key"; python main.py
```

### "Cannot reach Nexus Core"
**Cause:** FastAPI backend is not running.
**Fix:** Open a separate terminal and run `python main.py` first, then start Streamlit.

### "Web search failed"
**Cause:** DuckDuckGo rate-limited or network timeout.
**Fix:** The system automatically falls back to general LLM knowledge. Retry the query.

### "Model decommissioned" error
**Cause:** Groq decommissioned a model.
**Fix:** The 4-model fallback chain handles this automatically. If all fail, update `GROQ_MODELS` in `rag_engine.py`.

### Slow first response
**Cause:** Sentence Transformer model loading on first request.
**Fix:** Normal behavior — takes ~2–5 seconds on first startup only.

### Windows Long Path Error during pip install
**Fix:** Use a local `venv` inside the project directory (already done). Do not install globally.

---

## 🛣️ Roadmap

### Version 2.1 (Next)
- [ ] **ChromaDB persistence** — Save vector index to disk so uploaded documents survive server restarts
- [ ] **Chat history export** — Download conversation as PDF or Markdown
- [ ] **Multi-document tracking** — Show which specific document each answer came from
- [ ] **Streaming responses** — Stream LLM tokens in real-time using Server-Sent Events

### Version 2.2
- [ ] **Authentication** — User login with JWT tokens and per-user document stores
- [ ] **Docker support** — Single `docker-compose up` to launch everything
- [ ] **OpenAI / Anthropic support** — Plug-and-play LLM provider switching
- [ ] **Re-ranking** — Add a cross-encoder re-ranker after hybrid retrieval for even higher precision

### Version 3.0
- [ ] **Agentic loop** — Full LangChain AgentExecutor with tool calling instead of manual routing
- [ ] **Image understanding** — OCR for scanned PDFs, image Q&A
- [ ] **Multi-language** — Support documents in multiple languages

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Run the QA suite: `python qa_test_suite.py`
4. Commit your changes: `git commit -m "Add amazing feature"`
5. Push and open a Pull Request

**Before submitting, ensure:**
- All 30+ QA tests pass (100% score)
- No new `eval()` usage introduced
- New features have corresponding test cases in `qa_test_suite.py`

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

<div align="center">

**Built with ❤️ by Huraira Maqbool — AI Engineer**

📧 [hurairac37@gmail.com](mailto:hurairac37@gmail.com) · 💼 [Fiverr](https://www.fiverr.com/huraira_maqbool) · 🔗 [LinkedIn](https://www.linkedin.com/in/huraira-maqbool-b696a5277/)

*Nexus AI v2.0 — llama-3.3-70b-versatile · FastAPI · Streamlit · Groq LPU*

</div>
