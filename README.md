<div align="center">

# ✨ Nexus AI Engine — Hybrid Retrieval AI Agent

**A multi-tool RAG system combining semantic + keyword search, live web search, and step-by-step reasoning — powered by free-tier LLMs**

Ask questions from your PDFs, search the live web, and solve math — all in one agent, all in real time.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square&logo=langchain&logoColor=white)](https://langchain.com)
[![FAISS](https://img.shields.io/badge/FAISS-Semantic_Search-0057B7?style=flat-square)](https://faiss.ai)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Groq-Free_LLM-F55036?style=flat-square)](https://groq.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

[🚀 **Live Demo**](https://ai-rag-agent-8vfrcjngsjtppsrm2appwsc.streamlit.app/) · [📧 Contact](mailto:hurairac37@gmail.com) · [💼 Hire Me](https://www.fiverr.com/huraira_maqbool) · [🔗 LinkedIn](https://www.linkedin.com/in/huraira-maqbool-b696a5277/)

</div>

---

## 🧩 Overview

**Nexus AI Engine** is a production-grade Retrieval-Augmented Generation system that goes beyond a single vector lookup. It fuses **semantic search (FAISS)** with **keyword search (BM25)** in an ensemble retriever, wraps that in a tool-using LangChain agent (web search + calculator + retrieval), and serves it through a **FastAPI backend** with a **Streamlit frontend** — all running on free-tier infrastructure (Groq's LLaMA 3).

🟢 **Live and deployed** — try it now at the link above. No setup required.

This isn't a notebook demo. It's structured as a real app: a UI, an API layer, a retrieval system, and an LLM reasoning layer, each independently testable.

---

## ✨ Feature Highlights

| # | Feature | Description |
|---|---------|-------------|
| 1 | 📄 **Multi-format ingestion** | PDF, DOCX, and TXT — auto-parsed, cleaned, and chunked |
| 2 | 🔍 **Hybrid Retrieval** | FAISS (dense/semantic) + BM25 (sparse/keyword) combined via `EnsembleRetriever` |
| 3 | 🧠 **Intent Detection** | Routes a query to the right tool (retrieval, web, or calculator) before generating a response |
| 4 | 🧮 **Calculator Tool** | Solves math expressions inline, without hallucinating arithmetic |
| 5 | 🌐 **Web Search** | DuckDuckGo integration for live, up-to-date answers — no API key required |
| 6 | 🔁 **Chain-of-Thought Prompting** | Structured CoT prompt types improve multi-step reasoning quality |
| 7 | ♻️ **Groq Fallback Chain** | Automatically retries across multiple Groq models if one is rate-limited or unavailable |
| 8 | ⚡ **Full-Stack Deployment** | Streamlit UI + FastAPI backend, deployable independently or together |

---

## 🏗️ Architecture

```
┌────────────┐      HTTP       ┌─────────────┐
│  Browser   │ ───────────────▶│  Streamlit  │
│  (User)    │◀─────────────── │  Frontend   │
└────────────┘                 └──────┬──────┘
                                       │ REST (JSON)
                                       ▼
                                ┌─────────────┐
                                │   FastAPI   │
                                │   Backend   │
                                └──────┬──────┘
                                       │
                                       ▼
                            ┌────────────────────┐
                            │     RAGSystem       │
                            │  (Core Agent Logic)  │
                            └──────────┬──────────┘
                                       │
              ┌────────────────────────┼────────────────────────┐
              ▼                        ▼                         ▼
      ┌───────────────┐       ┌───────────────┐         ┌───────────────┐
      │ Hybrid Retriever│      │  Web Search    │         │  Calculator    │
      │ FAISS + BM25    │      │  (DuckDuckGo)  │         │  Tool          │
      │ EnsembleRetriever│     └───────────────┘         └───────────────┘
      └───────────────┘
              │
              ▼
      ┌───────────────────┐
      │   Groq LLaMA 3      │
      │  (Fallback Chain)   │
      └──────────┬──────────┘
                 │
                 ▼
         Final JSON Response
        (returned to FastAPI → Streamlit → Browser)
```

---

## 🛠️ Tech Stack

```python
stack = {
    "frontend":     "Streamlit",
    "backend":      "FastAPI",
    "framework":    "LangChain",
    "agent":        "LangChain AgentExecutor",
    "retrieval":    ["FAISS", "BM25Retriever", "EnsembleRetriever"],
    "embeddings":   "Sentence Transformers (all-MiniLM-L6-v2)",
    "llm":          "Groq → LLaMA3-70B (with fallback chain)",
    "tools":        ["DuckDuckGo Search", "Calculator", "RAG Retriever"],
    "testing":      "Custom 30+ QA test suite",
}
```

---

## 📁 Project Structure

```
nexus-ai-engine/
├── app.py                # Streamlit frontend
├── main.py                # FastAPI backend & routes
├── rag_system.py          # Core RAGSystem class (retrieval + agent logic)
├── tools/                 # Web search, calculator, retriever tool wrappers
├── tests/                 # 30+ QA test suite
├── requirements.txt       # All dependencies
├── .env.example            # Environment variable template
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- A free [Groq API key](https://console.groq.com)

### 1. Clone the repository
```bash
git clone https://github.com/HurairaMaqbool/nexus-ai-engine.git
cd nexus-ai-engine
```

### 2. Create a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
# then add your GROQ_API_KEY inside .env
```

### 5. Run the backend
```bash
uvicorn main:app --reload
```

### 6. Run the frontend (in a new terminal)
```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`, with the API at `http://localhost:8000`.

---

## ⚙️ Configuration

| Variable | Description | Default |
|----------|--------------|---------|
| `GROQ_API_KEY` | API key for Groq LLM access | — (required) |
| `CHUNK_SIZE` | Document chunk size (characters) | `1000` |
| `CHUNK_OVERLAP` | Overlap between chunks | `200` |
| `EMBEDDING_MODEL` | Sentence-transformer model name | `all-MiniLM-L6-v2` |
| `LLM_MODEL` | Primary Groq model | `llama3-70b-8192` |
| `RETRIEVER_K` | Number of chunks retrieved per query | `4` |

---

## 📡 API Reference

### `POST /chat`
Send a query to the agent.

**Request:**
```json
{
  "query": "What does the document say about quarterly revenue?",
  "session_id": "abc123"
}
```

**Response:**
```json
{
  "answer": "According to the document, quarterly revenue increased by 12%...",
  "source": "retriever",
  "session_id": "abc123"
}
```

### `POST /upload`
Upload a document (PDF/DOCX/TXT) for ingestion.

**Request:** `multipart/form-data` with a `file` field.

**Response:**
```json
{
  "status": "success",
  "chunks_created": 48,
  "filename": "report.pdf"
}
```

### `GET /health`
Health check endpoint.

**Response:**
```json
{ "status": "ok" }
```

---

## 🔍 How Each Module Works

**Intent Detection** — Before generating a response, the agent classifies the query (document lookup, web search, or calculation) and routes it to the matching tool, instead of relying on the LLM to decide blindly every time.

**Hybrid Search Flow** — Each query runs through both FAISS (semantic similarity) and BM25 (keyword overlap) simultaneously. Results are merged and re-ranked by the `EnsembleRetriever`, which improves recall on queries that mix exact terms with conceptual phrasing.

**Chain-of-Thought (CoT) Prompting** — Different query types (factual, comparative, multi-step) use different CoT prompt templates to guide the model's reasoning before the final answer.

**Groq Fallback Chain** — If the primary Groq model is rate-limited or returns an error, the system automatically retries with the next model in the configured fallback list, with no interruption to the user.

---

## 📊 Why Hybrid Search?

| Method | Strength | Weakness |
|--------|----------|----------|
| FAISS only | Strong semantic/conceptual matching | Misses exact keyword matches |
| BM25 only | Precise exact-term matching | No conceptual understanding |
| **Hybrid (Nexus AI Engine)** | **Combines both — higher recall & precision** | Minor added latency (negligible) |

---

## 🧪 Testing

The project ships with a 30+ question QA test suite covering retrieval accuracy, tool routing, and edge cases.

```bash
pytest tests/ -v
```

Expected output: pass/fail count per test category (retrieval, web search, calculator, fallback handling).

---

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| `GROQ_API_KEY not found` | Ensure `.env` exists and key is set correctly |
| `ModuleNotFoundError` | Re-run `pip install -r requirements.txt` inside your venv |
| FAISS index empty / no results | Confirm the document was uploaded via `/upload` before querying |
| Streamlit can't reach backend | Check FastAPI is running on `localhost:8000` and CORS is enabled |
| Groq `429 Too Many Requests` | Fallback chain should auto-retry; if persistent, wait for rate limit reset |
| Slow first response | First run downloads the embedding model (~80MB); subsequent runs are cached |

---

## 🗺️ Roadmap

- **v2.1** — Add conversation memory across sessions
- **v2.2** — Support image-based documents (OCR ingestion)
- **v3.0** — Multi-agent orchestration with specialized sub-agents per tool

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Run the test suite before submitting (`pytest tests/ -v`)
4. Open a pull request with a clear description of the change

---

## 👤 Author

Built by **Huraira Maqbool** — AI Engineer

📧 [hurairac37@gmail.com](mailto:hurairac37@gmail.com) · 💼 [Fiverr](https://www.fiverr.com/huraira_maqbool) · 🔗 [LinkedIn](https://www.linkedin.com/in/huraira-maqbool-b696a5277/)

</div>
