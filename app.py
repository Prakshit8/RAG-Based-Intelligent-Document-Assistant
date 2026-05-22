"""
DocuPilot AI - No Sidebar Version
All controls and AI Actions on main page
"""

import streamlit as st
import tempfile
from pathlib import Path

from rag_pipeline import RAGPipeline
from utils import setup_logger, validate_api_key

logger = setup_logger("streamlit_app")

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="DocuPilot AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Hide sidebar completely */
[data-testid="stSidebar"] {
    display: none !important;
}
[data-testid="collapsedControl"] {
    display: none !important;
}

/* Main app background */
.stApp {
    background-color: #020817;
}

.main .block-container {
    padding-top: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 100% !important;
}

/* Text */
h1, h2, h3, h4, h5, h6, p, span, label, div {
    color: #F8FAFC !important;
}

/* Inputs */
input, textarea {
    background-color: #1E293B !important;
    color: white !important;
    border: 1px solid #334155 !important;
}

/* All buttons */
.stButton > button {
    background-color: #2563EB !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 1rem !important;
    font-weight: 600 !important;
    width: 100% !important;
    transition: background-color 0.2s ease !important;
}

.stButton > button:hover {
    background-color: #1D4ED8 !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #1E293B !important;
    border: 2px dashed #475569 !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}

/* Chat messages */
.chat-message {
    padding: 1rem;
    border-radius: 12px;
    margin-bottom: 1rem;
}

.user-message {
    background: #172554;
    border-left: 5px solid #3B82F6;
}

.assistant-message {
    background: #1E293B;
    border-left: 5px solid #10B981;
}

/* Sources */
.source-chunk {
    background: #0F172A;
    padding: 1rem;
    border-radius: 10px;
    margin-top: 10px;
    border-left: 4px solid #6366F1;
}

/* AI action result box */
.ai-action-box {
    background: #1E293B;
    padding: 1.2rem;
    border-radius: 12px;
    margin-top: 1rem;
    border: 1px solid #334155;
}

/* Divider */
hr {
    border-color: #1E293B !important;
    margin: 1.5rem 0 !important;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# CONFIG
# =========================================================

def get_config():
    try:
        return {
            "api_key": st.secrets.get("GROQ_API_KEY", ""),
            "llm_provider": st.secrets.get("LLM_PROVIDER", "groq"),
            "llm_model": st.secrets.get("LLM_MODEL", "llama-3.1-8b-instant"),
            "chunk_size": st.secrets.get("CHUNK_SIZE", 1000),
            "chunk_overlap": st.secrets.get("CHUNK_OVERLAP", 200)
        }
    except Exception:
        st.error("Configuration error. Check your secrets.")
        return None

# =========================================================
# SESSION STATE
# =========================================================

def initialize_session_state():
    defaults = {
        "rag_pipeline": None,
        "chat_history": [],
        "processed_files": [],
        "config": get_config()
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# =========================================================
# PROCESS DOCUMENTS
# =========================================================

def process_uploaded_documents(uploaded_files):
    config = get_config()

    if config is None:
        return False

    if not validate_api_key(config["api_key"]):
        st.error("GROQ API key missing. Add it in Streamlit Cloud secrets.")
        return False

    with st.spinner("Processing documents..."):
        try:
            temp_dir = tempfile.mkdtemp()
            pdf_paths = []

            for uploaded_file in uploaded_files:
                temp_path = Path(temp_dir) / uploaded_file.name
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                pdf_paths.append(str(temp_path))

            st.session_state.rag_pipeline = RAGPipeline(
                api_key=config["api_key"],
                llm_model=config["llm_model"],
                llm_provider=config["llm_provider"],
                chunk_size=config["chunk_size"],
                chunk_overlap=config["chunk_overlap"]
            )

            stats = st.session_state.rag_pipeline.process_documents(pdf_paths)
            st.session_state.processed_files = [f.name for f in uploaded_files]

            st.success(f"✅ {stats['total_documents']} document(s) processed successfully!")
            return True

        except Exception as e:
            st.error(f"Error: {str(e)}")
            return False

# =========================================================
# CHAT UI
# =========================================================

def display_chat_message(role, content, sources=None):
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>👤 You</strong>
            <p>{content}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>🤖 Assistant</strong>
            <p>{content}</p>
        </div>
        """, unsafe_allow_html=True)

        if sources:
            st.markdown("**📚 Sources**")
            for i, source in enumerate(sources[:3], 1):
                st.markdown(f"""
                <div class="source-chunk">
                    <strong>Source {i}</strong><br>
                    {source.get('source', 'Unknown')}<br>
                    Page: {source.get('page', 'N/A')}
                </div>
                """, unsafe_allow_html=True)

# =========================================================
# AI ACTIONS
# =========================================================

def run_ai_action(action_type):
    if st.session_state.rag_pipeline is None:
        st.warning("⚠️ Upload and process documents first.")
        return

    prompts = {
        "summary":   "Generate a complete and detailed summary of all the documents.",
        "actions":   "Extract all action items, tasks, and deadlines from the documents.",
        "risks":     "Identify all risks, concerns, and important warnings in the documents.",
        "questions": "Generate 5 intelligent and insightful questions based on the documents."
    }

    action_labels = {
        "summary":   "📝 Document Summary",
        "actions":   "📌 Action Items",
        "risks":     "⚠️ Risks & Concerns",
        "questions": "❓ Suggested Questions"
    }

    with st.spinner(f"Running {action_labels[action_type]}..."):
        try:
            result = st.session_state.rag_pipeline.query(
                question=prompts[action_type],
                k=5,
                use_reranking=False,
                stream=False
            )
            st.markdown(f"""
            <div class="ai-action-box">
                <h4>{action_labels[action_type]}</h4>
                <p>{result['answer']}</p>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Action failed: {str(e)}")

# =========================================================
# MAIN
# =========================================================

def main():
    initialize_session_state()

    # ── Header ──────────────────────────────────────────
    st.title("📚 DocuPilot AI")
    st.markdown("Upload PDF documents and ask questions about them.")
    st.markdown("---")

    # ── Upload Section ───────────────────────────────────
    st.markdown("### 📂 Upload Documents")

    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        if uploaded_files:
            if st.button("📥 Process Documents"):
                if process_uploaded_documents(uploaded_files):
                    st.rerun()

    # Processed files list
    if st.session_state.processed_files:
        st.markdown("**✅ Processed Files:**")
        for f in st.session_state.processed_files:
            st.write(f"  ✓ {f}")

    st.markdown("---")

    # ── AI Actions Section ───────────────────────────────
    if st.session_state.rag_pipeline:
        st.markdown("### 🤖 AI Actions")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("📝 Generate Summary"):
                run_ai_action("summary")

        with col2:
            if st.button("📌 Extract Actions"):
                run_ai_action("actions")

        with col3:
            if st.button("⚠️ Find Risks"):
                run_ai_action("risks")

        with col4:
            if st.button("❓ Suggest Questions"):
                run_ai_action("questions")

        st.markdown("---")

    # ── Chat Section ─────────────────────────────────────
    if st.session_state.rag_pipeline is None:
        st.info("👆 Upload PDFs above to get started.")
        return

    st.markdown("### 💬 Chat with Documents")

    # Clear chat button
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            if st.session_state.rag_pipeline:
                st.session_state.rag_pipeline.clear_conversation()
            st.rerun()

    # Display chat history
    for message in st.session_state.chat_history:
        display_chat_message(
            message["role"],
            message["content"],
            message.get("sources")
        )

    # Chat input
    user_input = st.chat_input("Ask something about your documents...")

    if user_input:
        display_chat_message("user", user_input)
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })

        with st.spinner("Thinking..."):
            try:
                result = st.session_state.rag_pipeline.query(
                    question=user_input,
                    k=5,
                    use_reranking=False,
                    stream=False
                )

                display_chat_message(
                    "assistant",
                    result["answer"],
                    result["sources"]
                )

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result["sources"]
                })

            except Exception as e:
                st.error(f"Query failed: {str(e)}")

# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    main()