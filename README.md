# 🤖 AI RAG Agent with Hybrid Search

A multi-tool AI agent that can answer questions from PDFs,
search the web, and solve math — all for FREE.

## Features
- 📄 PDF/DOCX/TXT parsing
- 🔍 Hybrid Search (FAISS semantic + BM25 keyword)
- 🧮 Calculator tool
- 🌐 Web search (DuckDuckGo, no API key)
- 🤖 LLM via Groq (free tier)
- ⚡ FastAPI backend

## Setup
1. Clone the repo
2. pip install -r requirements.txt
3. Set GROQ_API_KEY in your environment
4. Run in Google Colab or locally

## Tech Stack
LangChain • FAISS • BM25 • Groq LLaMA3 • FastAPI • Sentence Transformers
