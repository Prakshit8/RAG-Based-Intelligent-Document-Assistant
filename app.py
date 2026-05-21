"""
Streamlit App for RAG Document Assistant
Modern chat interface for document Q&A
"""

import streamlit as st
from typing import List, Dict, Any
import tempfile
from pathlib import Path

from rag_pipeline import RAGPipeline
from utils import setup_logger, validate_api_key


logger = setup_logger("streamlit_app")


# Page configuration
st.set_page_config(
    page_title="RAG Document Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for fully consistent dark theme
st.markdown("""
<style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Global styles */
    .stApp {
        background-color: #020817;
    }
    
    /* Main content area */
    .main .block-container {
        background-color: #020817;
        padding-top: 2rem;
    }
    
    /* Text colors for visibility */
    .stMarkdown, .stText, p, span, div {
        color: #F8FAFC !important;
    }
    
    /* Sidebar - Dark background with bright text */
    [data-testid="stSidebar"] {
        background-color: #0F172A !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background-color: #0F172A !important;
    }
    
    /* Sidebar text and labels */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {
        color: #FFFFFF !important;
    }
    
    /* Sidebar sections */
    [data-testid="stSidebar"] .stSubheader {
        color: #FFFFFF !important;
        font-weight: 600;
    }
    
    /* File uploader - Dark theme */
    [data-testid="stFileUploader"] {
        background-color: #1E293B !important;
        border: 2px dashed #475569 !important;
        border-radius: 0.5rem !important;
        padding: 2rem !important;
    }
    
    [data-testid="stFileUploader"] label {
        color: #F8FAFC !important;
    }
    
    [data-testid="stFileUploader"] span {
        color: #94A3B8 !important;
    }
    
    [data-testid="stFileUploader"] button {
        background-color: #3B82F6 !important;
        color: #FFFFFF !important;
        border: none !important;
    }
    
    /* Chat messages */
    .chat-message {
        padding: 1.25rem;
        border-radius: 0.75rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
        line-height: 1.6;
    }
    
    .user-message {
        background-color: #172554;
        border-left: 4px solid #3B82F6;
        color: #F8FAFC;
    }
    
    .assistant-message {
        background-color: #1E293B;
        border-left: 4px solid #10B981;
        color: #F8FAFC;
    }
    
    /* Message content */
    .chat-message p, .chat-message strong, .chat-message em {
        color: #F8FAFC !important;
    }
    
    /* Source chunks */
    .source-chunk {
        background-color: #0F172A;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.75rem 0;
        border-left: 3px solid #6366F1;
        font-size: 0.875rem;
        color: #F8FAFC;
    }
    
    .source-chunk strong {
        color: #A5B4FC !important;
    }
    
    /* Metric cards */
    .metric-card {
        background-color: #1E293B;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        color: #F8FAFC;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #F8FAFC !important;
    }
    
    /* Input fields - ALL input elements */
    input, textarea, [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        border-color: #334155 !important;
        caret-color: #FFFFFF !important;
    }
    
    input::placeholder, textarea::placeholder,
    [data-testid="stTextInput"] input::placeholder,
    [data-testid="stTextArea"] textarea::placeholder {
        color: #94A3B8 !important;
    }
    
    /* Chat input - specific styling */
    [data-testid="stChatInput"] {
        background-color: #1E293B !important;
    }
    
    [data-testid="stChatInput"] > div > div > textarea {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        caret-color: #FFFFFF !important;
    }
    
    [data-testid="stChatInput"] > div > div > textarea::placeholder {
        color: #94A3B8 !important;
    }
    
    /* Additional input selectors */
    .stTextInput input, .stTextArea textarea {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        caret-color: #FFFFFF !important;
    }
    
    .stTextInput input::placeholder, .stTextArea textarea::placeholder {
        color: #94A3B8 !important;
    }
    
    /* Buttons */
    .stButton > button {
        width: 100%;
        background-color: #3B82F6 !important;
        color: #F8FAFC !important;
        border: none !important;
    }
    
    .stButton > button:hover {
        background-color: #2563EB !important;
    }
    
    /* Selectbox */
    .stSelectbox > div > div > select {
        background-color: #1E293B !important;
        color: #F8FAFC !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        color: #F8FAFC !important;
    }
    
    /* Info messages */
    .stAlert {
        background-color: #1E293B !important;
        color: #F8FAFC !important;
    }
    
    /* Error messages */
    .stAlert[data-baseweb="toast"][kind="error"] {
        background-color: #7F1D1D !important;
        color: #FECACA !important;
    }
    
    /* Success messages */
    .stAlert[data-baseweb="toast"][kind="success"] {
        background-color: #064E3B !important;
        color: #D1FAE5 !important;
    }
    
    /* Markdown content */
    .stMarkdown {
        color: #F8FAFC !important;
    }
    
    .stMarkdown ul, .stMarkdown ol {
        color: #F8FAFC !important;
    }
    
    .stMarkdown li {
        color: #F8FAFC !important;
    }
    
    .stMarkdown code {
        background-color: #1E293B !important;
        color: #A5B4FC !important;
        padding: 0.2rem 0.4rem;
        border-radius: 0.25rem;
    }
    
    .stMarkdown pre {
        background-color: #0F172A !important;
        color: #F8FAFC !important;
        padding: 1rem;
        border-radius: 0.5rem;
        overflow-x: auto;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #F8FAFC !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
    }
    
    /* Text elements in sidebar */
    [data-testid="stSidebar"] .stText {
        color: #F8FAFC !important;
    }
    
    /* Icons in sidebar */
    [data-testid="stSidebar"] svg {
        fill: #F8FAFC !important;
    }
</style>
""", unsafe_allow_html=True)


def get_config():
    """Get configuration from Streamlit secrets with fallback to defaults"""
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "")
        llm_provider = st.secrets.get("LLM_PROVIDER", "groq")
        llm_model = st.secrets.get("LLM_MODEL", "llama-3.1-8b-instant")
        chunk_size = st.secrets.get("CHUNK_SIZE", 1000)
        chunk_overlap = st.secrets.get("CHUNK_OVERLAP", 200)
        
        return {
            "api_key": api_key,
            "llm_provider": llm_provider,
            "llm_model": llm_model,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap
        }
    except Exception as e:
        st.error("⚠️ Configuration error. Please check your Streamlit secrets.")
        return None


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'rag_pipeline' not in st.session_state:
        st.session_state.rag_pipeline = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = []
    if 'config' not in st.session_state:
        st.session_state.config = get_config()
    if 'auto_summary' not in st.session_state:
        st.session_state.auto_summary = None
    if 'summary_sources' not in st.session_state:
        st.session_state.summary_sources = []
    if 'summary_status' not in st.session_state:
        st.session_state.summary_status = None
    if 'ai_actions' not in st.session_state:
        st.session_state.ai_actions = {}
    if 'ai_action_status' not in st.session_state:
        st.session_state.ai_action_status = None


def display_chat_message(role: str, content: str, sources: List[Dict] = None):
    """
    Display a chat message with styling
    
    Args:
        role: 'user' or 'assistant'
        content: Message content
        sources: Optional source citations
    """
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
        
        # Display sources if available
        if sources:
            st.markdown("### 📚 Sources")
            for i, source in enumerate(sources[:3], 1):
                st.markdown(f"""
                <div class="source-chunk">
                    <strong>Source {i}:</strong> {source.get('source', 'Unknown')} 
                    (Page {source.get('page', 'N/A')})
                </div>
                """, unsafe_allow_html=True)


def _chunk_key(chunk: Dict[str, Any]) -> str:
    """Create a stable key for deduplicating retrieved chunks."""
    metadata = chunk.get("metadata", {})
    return "|".join([
        str(metadata.get("source", "")),
        str(metadata.get("page", "")),
        chunk.get("text", "")[:120]
    ])


AI_ACTIONS = {
    "summary": {
        "title": "Document Brief",
        "button": "Generate Summary",
        "refresh": "Refresh Summary",
        "spinner": "Building a document brief...",
        "searches": [
            "executive summary key findings important topics decisions risks deadlines action items",
            "main themes conclusions recommendations owners next steps dates obligations",
            "critical insights notable facts document purpose requirements follow up tasks"
        ],
        "prompt": """
Create a polished, decision-ready document brief using only the provided context.

Include these sections:
1. Executive Summary - 3 to 5 concise bullets covering the document's purpose and bottom line.
2. Key Insights - the most important facts, decisions, requirements, risks, or opportunities.
3. Important Topics - grouped themes with short explanations.
4. Action Items / Deadlines - tasks, owners, dates, obligations, and follow-ups. If none are present, say "No explicit action items or deadlines found."
5. Source Notes - mention the pages or files that support the summary where available.

Be specific. Do not invent details outside the retrieved document context.
        """
    },
    "actions": {
        "title": "Action Items",
        "button": "Extract Actions",
        "refresh": "Refresh Actions",
        "spinner": "Extracting tasks and deadlines...",
        "searches": [
            "action items tasks owners deadlines due dates obligations follow up next steps",
            "requirements responsibilities deliverables assigned owner timeline dates",
            "must should required deadline submit complete review approve"
        ],
        "prompt": """
Extract every action item, task, obligation, owner, due date, and follow-up from the provided context.

Return a compact table with these columns:
Task | Owner | Deadline | Priority | Evidence

Rules:
- If owner, deadline, or priority is missing, write "Not specified".
- Set Priority to High only for explicit urgency, risk, legal/compliance, money, customer, or deadline impact.
- Include page/file evidence in the Evidence column when available.
- If there are no action items, say "No explicit action items found."
        """
    },
    "risks": {
        "title": "Risk Scan",
        "button": "Find Risks",
        "refresh": "Refresh Risks",
        "spinner": "Scanning for risks...",
        "searches": [
            "risks issues blockers gaps concerns dependencies constraints assumptions",
            "legal compliance financial operational security privacy deadline risk",
            "limitations missing information exceptions warnings unresolved"
        ],
        "prompt": """
Analyze the provided context for risks, blockers, unresolved issues, assumptions, and missing information.

Return these sections:
1. High-Risk Items
2. Medium-Risk Items
3. Missing Information / Open Questions
4. Recommended Next Steps

For each risk, include why it matters and the source page/file if available.
Do not invent risks that are not supported by the context.
        """
    },
    "questions": {
        "title": "Suggested Questions",
        "button": "Suggest Questions",
        "refresh": "Refresh Questions",
        "spinner": "Creating suggested questions...",
        "searches": [
            "main topics important details decisions requirements risks deadlines",
            "summary insights document purpose key facts open questions",
            "themes recommendations obligations constraints follow up"
        ],
        "prompt": """
Generate smart questions a user should ask about these documents.

Return:
1. 5 practical questions for understanding the document.
2. 3 deeper analysis questions about risks, gaps, or decisions.
3. 2 follow-up questions for action planning.

Make every question specific to the retrieved document context.
        """
    }
}


def _retrieve_action_chunks(action_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Retrieve a broader, deduplicated context set for an AI automation action."""
    if st.session_state.rag_pipeline is None:
        return []

    vector_store = st.session_state.rag_pipeline.vector_store
    if vector_store.index is None or vector_store.index.ntotal == 0:
        return []

    max_results = min(12, vector_store.index.ntotal)
    retrieved_chunks = []
    seen = set()
    for search_query in action_config["searches"]:
        for chunk in vector_store.search(search_query, k=max_results):
            key = _chunk_key(chunk)
            if key not in seen:
                seen.add(key)
                retrieved_chunks.append(chunk)

    return retrieved_chunks[:max_results]


def run_ai_action(action_key: str) -> bool:
    """Run an AI automation action and store the output for display."""
    action_config = AI_ACTIONS[action_key]

    if st.session_state.rag_pipeline is None:
        st.session_state.ai_action_status = "Upload and process documents before running AI actions."
        return False

    retrieved_chunks = _retrieve_action_chunks(action_config)
    if not retrieved_chunks:
        st.session_state.ai_action_status = "Documents were indexed, but no useful chunks were retrieved for this AI action."
        return False

    try:
        action_result = st.session_state.rag_pipeline.llm_service.generate_answer(
            action_config["prompt"],
            retrieved_chunks,
            []
        )
        output = action_result["answer"]
        status = f"{action_config['title']} generated successfully."
        ok = True
    except Exception as action_error:
        logger.exception("AI automation action failed")
        fallback_lines = [
            f"{action_config['title']} could not complete with the LLM, so here are the most relevant source excerpts:",
            ""
        ]

        for index, chunk in enumerate(retrieved_chunks[:6], 1):
            metadata = chunk.get("metadata", {})
            source = metadata.get("source", "Unknown source")
            page = metadata.get("page", "N/A")
            text = " ".join(chunk.get("text", "").split())
            fallback_lines.append(f"{index}. {source} (Page {page}): {text[:500]}")

        output = "\n\n".join(fallback_lines)
        status = f"{action_config['title']} LLM step failed, but source excerpts are shown. Error: {action_error}"
        ok = False

    sources = [chunk.get("metadata", {}) for chunk in retrieved_chunks]
    st.session_state.ai_actions[action_key] = {
        "title": action_config["title"],
        "output": output,
        "sources": sources,
        "status": status,
        "success": ok
    }
    st.session_state.ai_action_status = status

    if action_key == "summary":
        st.session_state.auto_summary = output
        st.session_state.summary_sources = sources
        st.session_state.summary_status = status

    return ok


def generate_document_summary() -> bool:
    """Generate and store a useful document summary without breaking the app."""
    return run_ai_action("summary")


def display_ai_actions():
    """Display generated AI automation outputs."""
    if not st.session_state.ai_actions:
        return

    st.markdown("## AI Automation Results")

    for action_key, action in st.session_state.ai_actions.items():
        st.markdown(f"### {action['title']}")
        st.markdown(f"""
        <div class="assistant-message">
            {action['output']}
        </div>
        """, unsafe_allow_html=True)

        sources = action.get("sources", [])
        if sources:
            with st.expander(f"{action['title']} sources"):
                for index, source in enumerate(sources[:8], 1):
                    st.markdown(
                        f"{index}. {source.get('source', 'Unknown')} "
                        f"(Page {source.get('page', 'N/A')})"
                    )


def display_document_summary():
    """Display generated summary and supporting sources."""
    if not st.session_state.auto_summary:
        return

    st.markdown("## AI Generated Summary & Insights")
    st.markdown(f"""
    <div class="assistant-message">
        {st.session_state.auto_summary}
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.summary_sources:
        with st.expander("Summary sources"):
            for index, source in enumerate(st.session_state.summary_sources[:8], 1):
                st.markdown(
                    f"{index}. {source.get('source', 'Unknown')} "
                    f"(Page {source.get('page', 'N/A')})"
                )


def sidebar():
    """Render sidebar with configuration options"""
    with st.sidebar:
        st.title("📚 RAG Assistant")
        st.markdown("---")
        
        # Document Upload
        st.subheader("� Upload Documents")
        uploaded_files = st.file_uploader(
            "Upload PDF files",
            type=['pdf'],
            accept_multiple_files=True,
            help="Upload one or more PDF documents to query"
        )
        
        if uploaded_files:
            if st.button("📥 Process Documents", use_container_width=True):
                # Get configuration from secrets
                config = get_config()
                
                if config is None:
                    st.error("⚠️ Configuration error. Please check your Streamlit secrets.")
                    return
                
                if not validate_api_key(config["api_key"]):
                    st.error("⚠️ API key not configured. Please add GROQ_API_KEY to your Streamlit secrets.")
                    st.info("📖 For local development: Create `.streamlit/secrets.toml` with your API key.")
                    st.info("📖 For Streamlit Cloud: Add GROQ_API_KEY in your app settings.")
                    return
                
                with st.spinner("Processing documents..."):
                    try:
                        # Save uploaded files to temp directory
                        temp_dir = tempfile.mkdtemp()
                        pdf_paths = []
                        
                        for uploaded_file in uploaded_files:
                            temp_path = Path(temp_dir) / uploaded_file.name
                            with open(temp_path, 'wb') as f:
                                f.write(uploaded_file.getbuffer())
                            pdf_paths.append(str(temp_path))
                        
                        # Initialize RAG pipeline
                        st.session_state.rag_pipeline = RAGPipeline(
                            api_key=config["api_key"],
                            llm_model=config["llm_model"],
                            llm_provider=config["llm_provider"],
                            chunk_size=config["chunk_size"],
                            chunk_overlap=config["chunk_overlap"]
                        )

                        # Process documents
                        stats = st.session_state.rag_pipeline.process_documents(pdf_paths)

                        st.session_state.processed_files = [f.name for f in uploaded_files]
                        st.session_state.config = config
                        st.session_state.auto_summary = None
                        st.session_state.summary_sources = []
                        st.session_state.summary_status = None
                        st.session_state.ai_actions = {}
                        st.session_state.ai_action_status = None

                        st.success(f"✅ Processed {stats['total_chunks']} chunks from {stats['total_documents']} documents")

                        # Display statistics
                        st.markdown("### 📊 Document Statistics")
                        st.metric("Total Chunks", stats['total_chunks'])
                        st.metric("Total Documents", stats['total_documents'])
                        st.metric("Avg Chunk Size", f"{stats['avg_chunk_size']:.0f} chars")

                        st.info("Documents are ready. Use AI Actions below to generate structured automation outputs.")

                    except Exception as e:
                        st.error(f"❌ Error processing documents: {str(e)}")
                        st.error("Please check your API key and try again.")
        
        st.markdown("---")
        
        # Display processed files
        if st.session_state.processed_files:
            st.subheader("📁 Processed Files")
            for file in st.session_state.processed_files:
                st.text(f"✓ {file}")

            st.markdown("---")
            st.subheader("AI Actions")
            st.caption("Run focused automations on the indexed documents.")

            action_keys = list(AI_ACTIONS.keys())
            for row_start in range(0, len(action_keys), 2):
                columns = st.columns(2)
                for column, action_key in zip(columns, action_keys[row_start:row_start + 2]):
                    action_config = AI_ACTIONS[action_key]
                    has_result = action_key in st.session_state.ai_actions
                    label = action_config["refresh"] if has_result else action_config["button"]

                    with column:
                        if st.button(label, type="primary", use_container_width=True):
                            with st.spinner(action_config["spinner"]):
                                if run_ai_action(action_key):
                                    st.success(st.session_state.ai_action_status)
                                else:
                                    st.warning(st.session_state.ai_action_status)

            if st.session_state.ai_action_status:
                st.caption(st.session_state.ai_action_status)
        
        st.markdown("---")
        
        # Clear buttons
        st.subheader("🗑️ Clear Data")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                if st.session_state.rag_pipeline:
                    st.session_state.rag_pipeline.clear_conversation()
                st.success("Chat cleared!")
        
        with col2:
            if st.button("Clear All", use_container_width=True):
                st.session_state.chat_history = []
                st.session_state.processed_files = []
                st.session_state.rag_pipeline = None
                st.session_state.auto_summary = None
                st.session_state.summary_sources = []
                st.session_state.summary_status = None
                st.session_state.ai_actions = {}
                st.session_state.ai_action_status = None
                st.success("All data cleared!")
        
        st.markdown("---")
        
        # Pipeline stats
        if st.session_state.rag_pipeline:
            stats = st.session_state.rag_pipeline.get_pipeline_stats()
            st.subheader("📈 Pipeline Stats")
            st.text(f"Documents: {stats['processed_documents']}")
            st.text(f"Messages: {stats['conversation_length']}")
            st.text(f"Vectors: {stats['vector_store_stats']['total_documents']}")


def main():
    """Main application logic"""
    initialize_session_state()
    sidebar()
    
    # Main content area
    st.title("💬 Chat with Your Documents")
    st.markdown("Upload PDF documents and ask questions about their content.")
    
    # Check if pipeline is initialized
    if st.session_state.rag_pipeline is None:
        st.info("👈 Please upload PDF documents in the sidebar to get started.")
        return

    display_ai_actions()
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("---")
        for message in st.session_state.chat_history:
            display_chat_message(
                message['role'],
                message['content'],
                message.get('sources')
            )
    
    # Chat input
    st.markdown("---")
    user_input = st.chat_input("Ask a question about your documents...")
    
    if user_input:
        # Display user message
        display_chat_message("user", user_input)
        
        # Add to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Generate response
        with st.spinner("🤔 Thinking..."):
            try:
                result = st.session_state.rag_pipeline.query(
                    question=user_input,
                    k=5,
                    use_reranking=False,
                    stream=False
                )
                
                # Display assistant response
                display_chat_message(
                    "assistant",
                    result['answer'],
                    result['sources']
                )
                
                # Add to history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": result['answer'],
                    "sources": result['sources']
                })
                
                # Display token usage
                with st.expander("📊 Token Usage"):
                    st.json(result['token_usage'])
                
            except Exception as e:
                st.markdown(f"""
                <div style="
                    background-color: #7f1d1d;
                    border: 2px solid #dc2626;
                    border-radius: 0.5rem;
                    padding: 1rem;
                    margin: 1rem 0;
                ">
                    <h4 style="color: #fecaca; margin: 0 0 0.5rem 0;">❌ Error generating response</h4>
                    <p style="color: #fecaca; margin: 0; font-size: 0.9rem;">{str(e)}</p>
                </div>
                """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
