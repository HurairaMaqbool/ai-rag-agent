import os
import shutil
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
import uvicorn
from rag_engine import RAGSystem

app = FastAPI(title="AI RAG Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Global RAG System instance
rag = RAGSystem()

@app.post("/chat")
async def chat(data: dict):
    query = data.get("question", "")
    api_key = data.get("api_key", "")

    if not query:
        return {"answer": "No question provided."}

    # Inject API key into the server process environment for this request
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key

    answer = await run_in_threadpool(rag.chat, query)
    return {"answer": answer}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    os.makedirs("temp_uploads", exist_ok=True)
    file_path = os.path.join("temp_uploads", file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        status_msg = await run_in_threadpool(rag.add_document, file_path, file.filename)
    except Exception as e:
        status_msg = f"Failed to process {file.filename}: {str(e)}"
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

    return {"status": status_msg, "filename": file.filename}

@app.get("/health")
async def health():
    return {"status": "online", "docs_indexed": len(rag.chunks)}

if __name__ == "__main__":
    print("✅ Starting FastAPI Server on port 8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
