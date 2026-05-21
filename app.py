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

                        st.success(f"✅ Processed {stats['total_chunks']} chunks from {stats['total_documents']} documents")

                        # Display statistics
                        st.markdown("### 📊 Document Statistics")
                        st.metric("Total Chunks", stats['total_chunks'])
                        st.metric("Total Documents", stats['total_documents'])
                        st.metric("Avg Chunk Size", f"{stats['avg_chunk_size']:.0f} chars")

                        # ==============================
                        # AI AUTOMATION: AUTO SUMMARY
                        # ==============================

                        with st.spinner("🤖 Generating AI Summary & Insights..."):

                            # Retrieve important chunks
                            search_results = st.session_state.rag_pipeline.search(
                                query="Provide document summary and important insights",
                                k=5
                            )

                            # Combine chunk text
                            summary_context = "\n\n".join([
                                chunk["text"] for chunk in search_results
                            ])

                            # AI prompt
                            summary_prompt = f"""
                            Analyze the following document content.

                            Generate:
                            1. Executive Summary
                            2. Key Insights
                            3. Important Topics
                            4. Action Items / Deadlines (if present)

                            Document Content:
                            {summary_context}
                            """

                            # Generate AI response
                            response = st.session_state.rag_pipeline.llm_service.client.chat.completions.create(
                                model=config["llm_model"],
                                messages=[
                                    {
                                        "role": "user",
                                        "content": summary_prompt
                                    }
                                ],
                                temperature=0.2,
                                max_tokens=700
                            )

                            auto_summary = response.choices[0].message.content

                            # Save in session
                            st.session_state.auto_summary = auto_summary

                        # Display AI Summary
                        if "auto_summary" in st.session_state:

                            st.markdown("## 🤖 AI Generated Summary & Insights")

                            st.markdown(f"""
                            <div class="assistant-message">
                                {st.session_state.auto_summary}
                            </div>
                            """, unsafe_allow_html=True)

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
