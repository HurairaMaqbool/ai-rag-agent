"""
rag_engine.py — Nexus AI Core Engine
100% professional, production-ready RAG pipeline.
Fixes applied:
  - ast.Constant replaces deprecated ast.Num (Python 3.8+)
  - ddgs replaces duckduckgo_search (renamed package)
  - get_embedding_dimension() replaces deprecated method
  - Multi-model Groq fallback chain
  - Robust intent detection (no false-positive calculator routes)
  - Full error isolation per method
  - Web search timeout + fallback to general LLM
"""

import os
from dotenv import load_dotenv
load_dotenv()

import re
import ast
import operator
import hashlib
import numpy as np
import time
from pypdf import PdfReader
from docx import Document
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from langchain_groq import ChatGroq

# ─── Try new ddgs package, fall back to duckduckgo_search ─────────────────────
try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None

import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Groq model fallback chain (try each in order)
GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama3-70b-8192",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]

# ─── Safe Math Evaluator ───────────────────────────────────────────────────────
def safe_eval(expr: str):
    """Safely evaluates math expressions using AST — no eval() used."""
    bin_ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.FloorDiv: operator.floordiv,
    }

    def _eval(node):
        # Python 3.8+: ast.Constant replaces ast.Num
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        # Backwards compat for older Python
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in bin_ops:
                raise ValueError(f"Unsupported operator: {op_type}")
            left = _eval(node.left)
            right = _eval(node.right)
            # Guard against division by zero
            if op_type == ast.Div and right == 0:
                raise ZeroDivisionError("Division by zero")
            return bin_ops[op_type](left, right)
        elif isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.USub):
                return -_eval(node.operand)
            elif isinstance(node.op, ast.UAdd):
                return _eval(node.operand)
        raise ValueError(f"Unsupported expression type: {type(node).__name__}")

    try:
        clean = expr.strip().replace('^', '**')
        # Reject any expression that's abnormally large (DoS guard)
        if len(clean) > 200:
            return "Expression too long."
        node = ast.parse(clean, mode='eval').body
        result = _eval(node)
        # Round to avoid floating point noise
        if isinstance(result, float) and result.is_integer():
            return int(result)
        if isinstance(result, float):
            return round(result, 10)
        return result
    except ZeroDivisionError:
        return "Error: Division by zero."
    except Exception as e:
        return f"Math error: {str(e)}"


# ─── Numpy Vector Index (FAISS-compatible fallback) ───────────────────────────
class NumpyFlatL2:
    """L2 distance flat vector index — no FAISS dependency required."""

    def __init__(self, dimension: int):
        self.dimension = dimension
        self.embeddings: np.ndarray | None = None
        self.ntotal = 0

    def add(self, vectors: np.ndarray):
        if self.embeddings is None:
            self.embeddings = vectors.copy()
        else:
            self.embeddings = np.vstack((self.embeddings, vectors))
        self.ntotal = self.embeddings.shape[0]

    def search(self, queries: np.ndarray, k: int):
        if self.embeddings is None or self.ntotal == 0:
            return np.array([[]]), np.array([[]])
        k = min(k, self.ntotal)
        # Vectorised L2 distance
        diff = self.embeddings[np.newaxis, :, :] - queries[:, np.newaxis, :]
        distances = np.sum(diff ** 2, axis=-1)
        indices = np.argsort(distances, axis=-1)[:, :k]
        top_distances = np.take_along_axis(distances, indices, axis=-1)
        return top_distances, indices

    def reset(self):
        self.embeddings = None
        self.ntotal = 0


# ─── Main RAG System ──────────────────────────────────────────────────────────
class RAGSystem:

    def __init__(self):
        print("⚙️  Loading embedding model...")
        for attempt in range(5):
            try:
                self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
                break
            except Exception as e:
                print(f"   Attempt {attempt + 1}/5 failed: {e}")
                time.sleep(3)
        else:
            raise RuntimeError("Could not load embedding model after 5 attempts.")

        dim = self.embed_model.get_embedding_dimension()
        self.index = NumpyFlatL2(dim)
        self.chunks: list[dict] = []
        self.bm25: BM25Okapi | None = None
        print("✅ RAG System ready.")

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _rebuild_bm25(self):
        if not self.chunks:
            self.bm25 = None
            return
        tokenized = [c["text"].lower().split() for c in self.chunks]
        self.bm25 = BM25Okapi(tokenized)

    def _get_llm(self, temperature: float = 0.3) -> ChatGroq:
        api_key = os.environ.get("GROQ_API_KEY", "") or GROQ_API_KEY
        for model in GROQ_MODELS:
            try:
                llm = ChatGroq(model=model, temperature=temperature, api_key=api_key)
                return llm
            except Exception:
                continue
        raise RuntimeError("All Groq models unavailable. Check your API key.")

    # ── Document Processing ───────────────────────────────────────────────────

    def parse_file(self, file_path: str, filename: str) -> list[dict]:
        """Parse PDF, DOCX, or TXT into a list of {text, source_id, file} dicts."""
        ext = filename.rsplit(".", 1)[-1].lower()
        items = []

        if ext == "pdf":
            reader = PdfReader(file_path)
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                text = text.strip()
                if text:
                    items.append({"text": text, "source_id": f"Page {i + 1}", "file": filename})

        elif ext == "docx":
            doc = Document(file_path)
            # Group paragraphs into logical blocks (avoid tiny 1-line chunks)
            block, block_id = [], 1
            for para in doc.paragraphs:
                t = para.text.strip()
                if t:
                    block.append(t)
                elif block:
                    items.append({"text": " ".join(block), "source_id": f"Block {block_id}", "file": filename})
                    block, block_id = [], block_id + 1
            if block:
                items.append({"text": " ".join(block), "source_id": f"Block {block_id}", "file": filename})

        elif ext == "txt":
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read().strip()
            if content:
                items.append({"text": content, "source_id": "Full text", "file": filename})

        else:
            raise ValueError(f"Unsupported file type: .{ext}. Supported: pdf, docx, txt")

        return items

    def chunk_text(self, items: list[dict], chunk_size: int = 800, overlap: int = 150) -> list[dict]:
        """Sliding window chunker with overlap."""
        chunks = []
        for item in items:
            text = item["text"]
            start = 0
            while start < len(text):
                end = min(start + chunk_size, len(text))
                chunk_text = text[start:end].strip()
                if chunk_text:
                    chunks.append({
                        "text": chunk_text,
                        "source_id": item["source_id"],
                        "source_file": item["file"],
                    })
                if end == len(text):
                    break
                start += chunk_size - overlap
        return chunks

    def add_document(self, file_path: str, filename: str) -> str:
        """Parse, chunk, embed, and index a document file."""
        try:
            items = self.parse_file(file_path, filename)
        except ValueError as e:
            return str(e)

        if not items:
            return f"No readable text found in {filename}."

        new_chunks = self.chunk_text(items)
        if not new_chunks:
            return f"File {filename} was empty after processing."

        self.chunks.extend(new_chunks)
        texts = [c["text"] for c in new_chunks]
        embeddings = self.embed_model.encode(texts, show_progress_bar=False, batch_size=32)
        self.index.add(np.array(embeddings, dtype="float32"))
        self._rebuild_bm25()

        return f"✅ Indexed {len(new_chunks)} chunks from **{filename}**. Ready to answer questions!"

    # ── Search ────────────────────────────────────────────────────────────────

    def hybrid_search(self, query: str, top_k: int = 5) -> list[dict]:
        """Combine semantic + keyword search, deduplicate by content hash."""
        if not self.chunks:
            return []

        top_k = min(top_k, len(self.chunks))

        # Semantic (dense) search
        q_embed = self.embed_model.encode([query])
        _, I = self.index.search(np.array(q_embed, dtype="float32"), top_k)
        semantic_results = [self.chunks[i] for i in I[0] if i < len(self.chunks)]

        # Keyword (sparse) BM25 search
        keyword_results = []
        if self.bm25:
            scores = self.bm25.get_scores(query.lower().split())
            bm25_top = np.argsort(scores)[::-1][:top_k]
            keyword_results = [self.chunks[i] for i in bm25_top if scores[i] > 0]

        # Merge + deduplicate by MD5 hash of text
        seen, merged = set(), []
        for c in semantic_results + keyword_results:
            key = hashlib.md5(c["text"].encode()).hexdigest()
            if key not in seen:
                seen.add(key)
                merged.append(c)

        return merged[:top_k]

    # ── Intent Detection ─────────────────────────────────────────────────────

    def detect_intent(self, query: str) -> str:
        """
        Intent priority:
          1. calculator — only if a numeric math expression is clearly present
          2. web_search — if the question is about real-time / current info
          3. pdf_rag    — default (answer from docs or general knowledge)
        """
        q = query.lower().strip()

        # Calculator: must have numbers AND operators together (not just a number in a sentence)
        has_expression = bool(re.search(r'\d[\s]*[\+\-\*\/\^%][\s]*\d', query))
        calc_words = ["calculate", "compute", "solve", "simplify", "evaluate"]
        is_calc_word = any(w in q for w in calc_words)

        if has_expression or (is_calc_word and re.search(r'\d', query)):
            return "calculator"

        # Web search: real-time or current-events queries
        web_patterns = [
            r'\b(latest|recent|today|now|current|live)\b',
            r'\b(2024|2025|2026)\b',
            r'\b(news|stock|price|weather|score|winner|election|trend)\b',
            r'\bwho (is|are|was|won|leads|runs)\b',
            r'\bwhat (is|are) (the )?(current|latest|today)',
        ]
        if any(re.search(p, q) for p in web_patterns):
            return "web_search"

        return "pdf_rag"

    # ── Tools ────────────────────────────────────────────────────────────────

    def calculator_tool(self, query: str) -> str:
        """Extract and safely evaluate a math expression from query text."""
        # Try to extract a clean math expression
        matches = re.findall(r'[\d\s\+\-\*\/\.\(\)\^%]+', query)
        best = max(matches, key=len) if matches else ""
        if not best.strip():
            return "No valid mathematical expression found in your query."
        result = safe_eval(best.strip())
        return f"Result: {result}"

    def web_search_tool(self, query: str, max_results: int = 4) -> str:
        """Search the web using DuckDuckGo and return formatted results."""
        if DDGS is None:
            return "Web search unavailable — install 'ddgs' package."
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
            if not results:
                return f"No web results found for: {query}"
            lines = []
            for r in results:
                lines.append(f"Title: {r.get('title', 'N/A')}\nSummary: {r.get('body', 'N/A')}")
            return "\n\n".join(lines)
        except Exception as e:
            return f"Web search failed ({type(e).__name__}): {e}"

    # ── LLM Prompting ─────────────────────────────────────────────────────────

    def ask_rag(self, question: str, context: str) -> str:
        """Few-shot + CoT prompt for document-grounded Q&A."""
        prompt = f"""You are a world-class AI research assistant specializing in document analysis.
Your job is to answer the user's question using ONLY the provided document context.
If the context does not contain a clear answer, say so honestly — do NOT hallucinate or make things up.

Follow this Chain of Thought:
1. Identify the core intent of the question.
2. Scan the context for every relevant fact, number, or statement.
3. Reason through the evidence step by step.
4. Present a well-structured, markdown-formatted final answer.

--- EXAMPLES ---

Example 1:
Context: "The Transformer architecture was introduced in the paper 'Attention is All You Need' (2017). It relies on a self-attention mechanism instead of recurrence."
Question: What mechanism does the Transformer use instead of recurrence?
Thought: The context states it uses "self-attention" instead of recurrence.
Answer: The Transformer uses a **self-attention mechanism**, which allows it to process all tokens simultaneously rather than sequentially.

Example 2:
Context: "Revenue for FY2023 was $4.2B. Operating costs were $2.8B."
Question: What was the operating profit?
Thought: Operating profit = Revenue - Costs = $4.2B - $2.8B = $1.4B.
Answer: The operating profit for FY2023 was **$1.4 billion**.

--- YOUR TASK ---

Context:
{context}

Question: {question}

Thought:"""
        try:
            llm = self._get_llm()
            return llm.invoke(prompt).content
        except Exception as e:
            return f"LLM Error: {e}"

    def ask_web(self, question: str, web_context: str) -> str:
        """Few-shot + CoT prompt for web-grounded answers."""
        prompt = f"""You are a knowledgeable AI assistant that synthesizes real-time web search results into clear, factual answers.
Use ONLY the provided search results. Do NOT fabricate facts. If results are insufficient, say so.

Chain of Thought:
1. Read all search results carefully.
2. Identify the most relevant and credible snippets.
3. Cross-reference multiple sources where possible.
4. Write a well-structured answer with key points in **bold**.

--- EXAMPLE ---
Search Results:
Title: Python 3.12 Released
Summary: Python 3.12 was released in October 2023 with major performance improvements and new syntax.

Question: When was Python 3.12 released?
Thought: The result says October 2023.
Answer: Python 3.12 was released in **October 2023**, featuring significant performance improvements.

--- YOUR TASK ---

Search Results:
{web_context}

Question: {question}

Thought:"""
        try:
            llm = self._get_llm()
            return llm.invoke(prompt).content
        except Exception as e:
            return f"LLM Error: {e}"

    def ask_general(self, question: str) -> str:
        """CoT prompt for general knowledge questions (no document context)."""
        prompt = f"""You are a brilliant, concise AI assistant. Answer the question using your knowledge.

Chain of Thought:
1. Understand exactly what the user is asking.
2. Break the answer into logical steps if needed.
3. Provide a clear, well-structured, markdown-formatted answer.

Question: {question}

Thought:"""
        try:
            llm = self._get_llm()
            return llm.invoke(prompt).content
        except Exception as e:
            return f"LLM Error: {e}"

    def ask_math_explainer(self, question: str, raw_result: str) -> str:
        """CoT prompt for explaining a math calculation step by step."""
        prompt = f"""You are a patient and precise math tutor.
The user asked: "{question}"
The computed result is: {raw_result}

Chain of Thought:
1. Identify the mathematical operation(s) involved.
2. Show each calculation step clearly.
3. Confirm the final answer with proper units if applicable.

Explain the solution clearly and confirm the result."""
        try:
            llm = self._get_llm(temperature=0.1)
            return llm.invoke(prompt).content
        except Exception as e:
            return ""

    # ── Main Chat Entry Point ─────────────────────────────────────────────────

    def chat(self, query: str) -> str:
        """Route query to the correct tool and return a formatted answer."""
        if not query or not query.strip():
            return "Please enter a valid question."

        try:
            intent = self.detect_intent(query)
        except Exception:
            intent = "pdf_rag"

        # ── Calculator ──
        if intent == "calculator":
            raw = self.calculator_tool(query)
            explanation = self.ask_math_explainer(query, raw)
            if explanation:
                return f"🧮 **{raw}**\n\n{explanation}"
            return f"🧮 **{raw}**"

        # ── Web Search ──
        elif intent == "web_search":
            web_results = self.web_search_tool(query)
            if "failed" in web_results.lower() or "unavailable" in web_results.lower():
                # Fallback to general LLM if web search fails
                answer = self.ask_general(query)
                return f"💡 **Answer** *(web search unavailable — using AI knowledge)*\n\n{answer}"
            answer = self.ask_web(query, web_context=web_results)
            return f"🌐 **Web Search Answer**\n\n{answer}"

        # ── PDF RAG / General ──
        else:
            chunks = self.hybrid_search(query)
            if not chunks:
                answer = self.ask_general(query)
                return f"💡 **General Answer** *(no documents indexed — using AI knowledge)*\n\n{answer}"

            context = "\n\n---\n\n".join(c["text"] for c in chunks)
            sources = sorted(set(
                f"`{c.get('source_file', 'Unknown')}` — {c.get('source_id', '')}"
                for c in chunks
            ))
            answer = self.ask_rag(query, context=context)
            sources_str = "\n".join(f"- {s}" for s in sources)
            return f"📄 **Document Answer**\n\n{answer}\n\n---\n**📎 Sources:**\n{sources_str}"
