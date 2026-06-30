import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

import requests
import time

st.set_page_config(
    page_title="Nexus AI | Smart Research Engine",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Premium White Theme CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;600;800;900&display=swap');

/* ─── Reset & Base ─── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #F8F9FF;
    color: #1A1A2E;
}

/* ─── Hide Streamlit branding ─── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {background: transparent !important;}
.stDeployButton {display: none;}

/* ─── Sidebar ─── */
[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #FFFFFF 0%, #F0F4FF 100%) !important;
    border-right: 1px solid #E2E8F5;
    box-shadow: 4px 0 24px rgba(99, 102, 241, 0.06);
}
[data-testid="stSidebar"] .stMarkdown p {
    color: #64748B;
}

/* ─── Main area ─── */
.main .block-container {
    padding-top: 1.5rem;
    max-width: 900px;
    margin: 0 auto;
}

/* ─── Hero Header ─── */
.hero-header {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 50%, #EC4899 100%);
    border-radius: 24px;
    margin-bottom: 1.5rem;
    box-shadow: 0 20px 60px rgba(99, 102, 241, 0.25);
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 60%);
    animation: shimmer 4s infinite;
}
@keyframes shimmer {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
.hero-title {
    font-family: 'Outfit', sans-serif;
    font-size: 2.8rem;
    font-weight: 900;
    color: #FFFFFF;
    letter-spacing: -1px;
    margin: 0;
    text-shadow: 0 2px 20px rgba(0,0,0,0.15);
}
.hero-subtitle {
    color: rgba(255,255,255,0.85);
    font-size: 1rem;
    font-weight: 400;
    margin-top: 0.5rem;
    letter-spacing: 0.3px;
}
.badge-row {
    display: flex;
    justify-content: center;
    gap: 0.6rem;
    margin-top: 1.2rem;
    flex-wrap: wrap;
}
.badge {
    background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.75rem;
    color: white;
    font-weight: 500;
    backdrop-filter: blur(4px);
}

/* ─── Chat messages ─── */
[data-testid="stChatMessage"] {
    background: #FFFFFF !important;
    border: 1px solid #E8ECFF;
    border-radius: 16px;
    padding: 16px !important;
    margin: 8px 0;
    box-shadow: 0 2px 12px rgba(99, 102, 241, 0.06);
    transition: all 0.25s ease;
}
[data-testid="stChatMessage"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(99, 102, 241, 0.12);
    border-color: #C7D2FE;
}
[data-testid="stChatMessage"] p {
    color: #1E293B !important;
    line-height: 1.75;
}

/* ─── Chat input ─── */
[data-testid="stChatInput"] {
    background: #FFFFFF;
    border: 2px solid #E8ECFF;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(99, 102, 241, 0.08);
    transition: all 0.25s ease;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #6366F1;
    box-shadow: 0 4px 24px rgba(99, 102, 241, 0.2);
}

/* ─── Sidebar buttons ─── */
.stButton > button {
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.6rem 1.2rem;
    font-weight: 600;
    font-size: 0.9rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
    width: 100%;
    letter-spacing: 0.2px;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
    color: white;
}
.stButton > button:active {
    transform: translateY(0px);
}

/* ─── Inputs ─── */
.stTextInput > div > div > input {
    background: #FFFFFF !important;
    border: 1.5px solid #E2E8F0 !important;
    border-radius: 10px !important;
    color: #1E293B !important;
    font-size: 0.9rem;
    transition: all 0.2s ease;
}
.stTextInput > div > div > input:focus {
    border-color: #6366F1 !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12) !important;
}

/* ─── File uploader ─── */
[data-testid="stFileUploader"] {
    background: #F8F9FF;
    border: 2px dashed #C7D2FE;
    border-radius: 12px;
    padding: 1rem;
    transition: all 0.2s;
}
[data-testid="stFileUploader"]:hover {
    border-color: #6366F1;
    background: #EEF2FF;
}

/* ─── Expanders ─── */
.streamlit-expanderHeader {
    background: #F1F5F9 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    color: #374151 !important;
    border: 1px solid #E2E8F0 !important;
}
.streamlit-expanderContent {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-top: none !important;
    border-radius: 0 0 10px 10px !important;
}

/* ─── Dividers ─── */
hr {
    border-color: #E8ECFF !important;
}

/* ─── Scrollbar ─── */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-track {
    background: #F1F5F9;
}
::-webkit-scrollbar-thumb {
    background: #C7D2FE;
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
    background: #6366F1;
}

/* ─── Sidebar section headers ─── */
.sidebar-section-title {
    font-family: 'Outfit', sans-serif;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: #6366F1;
    margin: 1rem 0 0.5rem;
}

/* ─── Status pills ─── */
.status-online {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #F0FDF4;
    border: 1px solid #BBF7D0;
    color: #15803D;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.75rem;
    font-weight: 600;
}
.status-dot {
    width: 7px;
    height: 7px;
    background: #22C55E;
    border-radius: 50%;
    display: inline-block;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* ─── Stat cards ─── */
.stat-card {
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
    border-radius: 14px;
    padding: 1rem 1.2rem;
    color: white;
    margin-bottom: 0.5rem;
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.25);
}
.stat-label {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    opacity: 0.8;
}
.stat-value {
    font-family: 'Outfit', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    margin-top: 2px;
}

/* ─── Welcome message card ─── */
.welcome-card {
    background: linear-gradient(135deg, #EEF2FF 0%, #F5F3FF 100%);
    border: 1px solid #C7D2FE;
    border-radius: 16px;
    padding: 1.5rem;
    margin: 1rem 0;
}
.welcome-card h4 {
    color: #4338CA;
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    margin-bottom: 0.5rem;
}
.capability-chip {
    display: inline-block;
    background: white;
    border: 1px solid #C7D2FE;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 0.8rem;
    color: #4338CA;
    font-weight: 500;
    margin: 4px 4px 4px 0;
}
</style>
""", unsafe_allow_html=True)

GROQ_KEY_DEFAULT = ""

# ─── Load Embedding Model & RAG System locally ───────────────────────────────
@st.cache_resource
def load_shared_embed_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")

from rag_engine import RAGSystem

# Initialize session-specific RAG System
if "rag" not in st.session_state:
    shared_model = load_shared_embed_model()
    st.session_state.rag = RAGSystem(embed_model=shared_model)

# ─── Initialize session state ──────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "doc_count" not in st.session_state:
    st.session_state.doc_count = 0
if "query_count" not in st.session_state:
    st.session_state.query_count = 0

# Engine is always online locally
backend_ok = True

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    if backend_ok:
        status_html = "<span class='status-online'><span class='status-dot'></span>Engine Online</span>"
    else:
        status_html = "<span style='display:inline-flex;align-items:center;gap:6px;background:#FEF2F2;border:1px solid #FECACA;color:#DC2626;border-radius:20px;padding:4px 12px;font-size:0.75rem;font-weight:600;'>⚠️ Backend Offline</span>"
    st.markdown(f"""
    <div style='text-align:center; padding: 1rem 0 0.5rem;'>
        <span style='font-family: Outfit; font-size: 1.4rem; font-weight: 900;
                     background: linear-gradient(135deg, #6366F1, #EC4899);
                     -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
            ✦ Nexus AI
        </span>
        <div style='margin-top: 6px;'>{status_html}</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Stats ──
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-label'>Documents</div>
            <div class='stat-value'>{st.session_state.doc_count}</div>
        </div>""", unsafe_allow_html=True)
    with col_b:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-label'>Queries</div>
            <div class='stat-value'>{st.session_state.query_count}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <p style='text-align:center; font-size:0.72rem; color:#94A3B8; line-height:1.7;'>
        Nexus AI Core v2.0<br>
        LangChain · FastAPI · Groq LPU<br>
        <span style='color:#C7D2FE;'>llama-3.3-70b-versatile</span>
    </p>""", unsafe_allow_html=True)

    # ── API Key ──
    st.markdown("<div class='sidebar-section-title'>🔑 Authentication</div>", unsafe_allow_html=True)
    default_key = os.environ.get("GROQ_API_KEY", GROQ_KEY_DEFAULT)
    api_key = st.text_input("Groq API Key", value=default_key, type="password",
                             placeholder="gsk_...", label_visibility="collapsed")
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key
        st.success("API Key Configured ✓")

    st.markdown("<div class='sidebar-section-title'>📄 Knowledge Base</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload Document",
        type=["pdf", "docx", "txt"],
        label_visibility="collapsed",
        help="Upload a PDF, DOCX, or TXT file to add to the AI's knowledge base."
    )

    if st.button("⚡ Process & Index Document"):
        if uploaded_file is not None:
            with st.spinner("Embedding document into neural index..."):
                import tempfile
                suffix = os.path.splitext(uploaded_file.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                    temp_file.write(uploaded_file.getvalue())
                    temp_file_path = temp_file.name
                
                try:
                    status_msg = st.session_state.rag.add_document(temp_file_path, uploaded_file.name)
                    st.session_state.doc_count = len(set(c.get("source_file", "") for c in st.session_state.rag.chunks))
                    st.toast(status_msg, icon="📄")
                    time.sleep(0.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"Processing failed: {e}")
                finally:
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
        else:
            st.warning("Please upload a file first.")

    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.session_state.query_count = 0
        st.rerun()

    st.divider()
    st.markdown("""
    <p style='text-align:center; font-size:0.72rem; color:#94A3B8; line-height:1.7;'>
        Nexus AI Core v2.0<br>
        LangChain · FastAPI · Groq LPU<br>
        <span style='color:#C7D2FE;'>llama-3.3-70b-versatile</span>
    </p>""", unsafe_allow_html=True)

# ─── Main Content ──────────────────────────────────────────────────────────────

# Hero Banner
st.markdown("""
<div class='hero-header'>
    <div class='hero-title'>✦ Nexus AI Engine</div>
    <div class='hero-subtitle'>Advanced Retrieval-Augmented Generation · Live Web Search · Math Solver</div>
    <div class='badge-row'>
        <span class='badge'>📄 PDF / DOCX / TXT</span>
        <span class='badge'>🌐 Web Search</span>
        <span class='badge'>🧮 Calculator</span>
        <span class='badge'>🧠 Chain of Thought</span>
        <span class='badge'>⚡ Groq LPU</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Welcome card if no messages
if not st.session_state.messages:
    st.markdown("""
    <div class='welcome-card'>
        <h4>👋 Welcome to Nexus AI!</h4>
        <p style='color:#4B5563; font-size:0.9rem; margin-bottom:0.8rem;'>
            I'm your intelligent research assistant powered by advanced RAG technology.
            Here's what I can do:
        </p>
        <span class='capability-chip'>📄 Answer from your uploaded documents</span>
        <span class='capability-chip'>🌐 Search the web in real-time</span>
        <span class='capability-chip'>🧮 Solve complex math step-by-step</span>
        <span class='capability-chip'>🧠 Reason with Chain of Thought</span>
        <span class='capability-chip'>💡 Answer general knowledge questions</span>
        <p style='color:#6B7280; font-size:0.82rem; margin-top:0.8rem;'>
            💡 <b>Tip:</b> Upload a PDF in the sidebar, then ask questions about it below!
        </p>
    </div>
    """, unsafe_allow_html=True)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask about your documents, search the web, or solve math..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.query_count += 1

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Thinking..."):
            try:
                current_api_key = os.environ.get("GROQ_API_KEY", GROQ_KEY_DEFAULT)
                if current_api_key:
                    os.environ["GROQ_API_KEY"] = current_api_key
                
                # Direct local call to the embedded RAG System
                answer = st.session_state.rag.chat(prompt)
                message_placeholder.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                message_placeholder.error(f"⚠️ Error: {e}")

