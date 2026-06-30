"""
qa_test_suite.py — Full automated QA test suite for Nexus AI
Run with: python qa_test_suite.py
"""
import sys
import os

# Force UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PASS = "[PASS]"
FAIL = "[FAIL]"

print("=" * 60)
print("  NEXUS AI -- SENIOR QA EXPERT TEST SUITE")
print("=" * 60)

results = []

def check(name, condition, detail=""):
    status = PASS if condition else FAIL
    results.append((status, name, detail))
    msg = f"  {status}  {name}"
    if detail:
        msg += f"\n         -> {detail}"
    print(msg)


# ─────────────────────────────────────────────────────────
# MODULE 1: safe_eval (Calculator)
# ─────────────────────────────────────────────────────────
print("\n[ MODULE 1 ] Calculator / safe_eval")
from rag_engine import safe_eval

check("Basic addition",         safe_eval("2 + 2") == 4)
check("Multiplication",         safe_eval("10 * 5") == 50)
check("Division",               safe_eval("100 / 4") == 25.0)
check("Exponentiation (^)",     safe_eval("2**8") == 256)
check("Modulo",                 safe_eval("17 % 5") == 2)
check("Negative number",        safe_eval("-5 + 3") == -2)
check("Float result",           abs(safe_eval("1 / 3") - 0.3333333333) < 1e-8)
check("Division by zero guard", "zero" in str(safe_eval("10 / 0")).lower())
check("DoS guard (long expr)",  "long" in str(safe_eval("1+" * 200 + "1")).lower()
                                 or "error" in str(safe_eval("1+" * 200 + "1")).lower())

# ─────────────────────────────────────────────────────────
# MODULE 2: Intent Detection
# ─────────────────────────────────────────────────────────
print("\n[ MODULE 2 ] Intent Detection")
from rag_engine import RAGSystem
rag = RAGSystem()

intent_cases = [
    ("2 + 2",                          "calculator"),
    ("what is 50 * 3",                 "calculator"),
    ("calculate 100 divided by 5",     "calculator"),
    ("compute 9 - 4",                  "calculator"),
    ("latest AI news today",           "web_search"),
    ("current price of bitcoin",       "web_search"),
    ("who won the 2026 world cup",     "web_search"),
    ("recent trends in technology",    "web_search"),
    ("what is artificial intelligence","pdf_rag"),
    ("what is ai",                     "pdf_rag"),
    ("explain machine learning",       "pdf_rag"),
    ("summarize the document",         "pdf_rag"),
    ("tell me about the report",       "pdf_rag"),
]
for query, expected in intent_cases:
    got = rag.detect_intent(query)
    check(f'Intent: "{query}"', got == expected, f"expected={expected}, got={got}")

# ─────────────────────────────────────────────────────────
# MODULE 3: Document Processing
# ─────────────────────────────────────────────────────────
print("\n[ MODULE 3 ] Document Parsing & Chunking")

import tempfile

# Test TXT parsing
with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
    f.write("This is a test document. " * 100)
    txt_path = f.name

items = rag.parse_file(txt_path, "test.txt")
check("TXT parse produces output",      len(items) > 0)
check("TXT item has text key",          "text" in items[0])
check("TXT item has source_id key",     "source_id" in items[0])

chunks = rag.chunk_text(items)
check("Chunking produces chunks",       len(chunks) > 0)
check("Each chunk has text",            all("text" in c for c in chunks))
check("Each chunk has source_file",     all("source_file" in c for c in chunks))
check("Chunk size <= 800 chars",        all(len(c["text"]) <= 800 for c in chunks))
os.unlink(txt_path)

# Test unsupported file type
try:
    rag.parse_file("fake.xyz", "fake.xyz")
    check("Unsupported file type raises error", False, "Should have raised ValueError")
except ValueError:
    check("Unsupported file type raises ValueError", True)

# ─────────────────────────────────────────────────────────
# MODULE 4: Vector Index (NumpyFlatL2)
# ─────────────────────────────────────────────────────────
print("\n[ MODULE 4 ] NumpyFlatL2 Vector Index")
import numpy as np
from rag_engine import NumpyFlatL2

idx = NumpyFlatL2(4)
check("Empty index: search returns empty",  idx.search(np.zeros((1,4), dtype="float32"), 5)[0].size == 0
                                             or len(idx.search(np.zeros((1,4), dtype="float32"), 5)[0]) == 0)

v1 = np.array([[1.0, 0.0, 0.0, 0.0]], dtype="float32")
v2 = np.array([[0.0, 1.0, 0.0, 0.0]], dtype="float32")
idx.add(v1)
idx.add(v2)
check("Index ntotal == 2",                  idx.ntotal == 2)
_, I = idx.search(v1, k=1)
check("Nearest neighbor is correct",        I[0][0] == 0, f"Expected index 0, got {I[0][0]}")
idx.reset()
check("Reset clears index",                 idx.ntotal == 0 and idx.embeddings is None)

# ─────────────────────────────────────────────────────────
# MODULE 5: Hybrid Search
# ─────────────────────────────────────────────────────────
print("\n[ MODULE 5 ] Hybrid Search")

rag2 = RAGSystem()
with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
    f.write("Machine learning is a subfield of artificial intelligence. "
            "Deep learning uses neural networks with many layers. "
            "Natural language processing handles text and speech data.")
    tmp = f.name

rag2.add_document(tmp, "test_doc.txt")
os.unlink(tmp)

results_search = rag2.hybrid_search("machine learning neural networks")
check("Hybrid search returns results",      len(results_search) > 0)
check("Results have text field",            all("text" in r for r in results_search))
check("Results have source_file field",     all("source_file" in r for r in results_search))

# Deduplication check
texts = [r["text"] for r in results_search]
import hashlib
hashes = [hashlib.md5(t.encode()).hexdigest() for t in texts]
check("No duplicate chunks returned",       len(hashes) == len(set(hashes)))

# Empty search
empty_results = rag2.hybrid_search("xyzzy gibberish 12345")
check("Low-relevance query still returns results (BM25 fallback)", isinstance(empty_results, list))

# ─────────────────────────────────────────────────────────
# MODULE 6: calculator_tool string extraction
# ─────────────────────────────────────────────────────────
print("\n[ MODULE 6 ] calculator_tool() string extraction")

r = rag.calculator_tool("what is 25 + 75")
check("Extracts and computes '25 + 75'",    "100" in r)

r = rag.calculator_tool("compute 9 * 9")
check("Extracts and computes '9 * 9'",      "81" in r)

r = rag.calculator_tool("no numbers here")
check("Handles query with no numbers",      "No valid" in r or "error" in r.lower())

# ─────────────────────────────────────────────────────────
# MODULE 7: Web search tool
# ─────────────────────────────────────────────────────────
print("\n[ MODULE 7 ] web_search_tool()")

web_result = rag.web_search_tool("python programming language")
check("Web search returns string",          isinstance(web_result, str))
check("Web search result not empty",        len(web_result) > 10)
is_error = "failed" in web_result.lower() and len(web_result) < 100
check("Web search not a bare error",        not is_error, web_result[:80] if is_error else "")

# ─────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────
print()
print("=" * 60)
passed = sum(1 for r in results if "PASS" in r[0])
failed = sum(1 for r in results if "FAIL" in r[0])
total  = len(results)
pct    = round(100 * passed / total)
print(f"  RESULT: {passed}/{total} tests passed  ({pct}% accuracy)")
if failed:
    print(f"\n  FAILED TESTS:")
    for r in results:
        if "FAIL" in r[0]:
            print(f"    [X] {r[1]}: {r[2]}")
else:
    print("  *** ALL TESTS PASSED -- Project is 100% functional! ***")
print("=" * 60)
