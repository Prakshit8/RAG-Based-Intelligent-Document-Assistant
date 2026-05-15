# RAG Document Assistant 📚

A production-ready Retrieval-Augmented Generation (RAG) based intelligent document assistant built with Streamlit, LangChain, FAISS, and modern LLMs.

## 🌟 Features

- **Multi-PDF Support**: Upload and process multiple PDF documents simultaneously
- **Semantic Search**: Advanced vector similarity search using FAISS
- **Grounded Answers**: LLM responses grounded in retrieved document chunks
- **Source Citations**: Transparent source attribution for every answer
- **Chat Interface**: Modern conversational UI with conversation memory
- **Hybrid Search**: Optional semantic + keyword search combination
- **Re-ranking**: LLM-based result re-ranking for better relevance
- **Persistent Storage**: Save and load vector indexes
- **Streaming Responses**: Real-time answer generation
- **Dark/Light UI**: Modern responsive interface

## 🏗️ Architecture

```
RAG Document Assistant/
├── app.py                      # Streamlit frontend
├── rag_pipeline.py             # Complete RAG pipeline
├── pdf_processor.py            # PDF text extraction
├── vector_store.py             # FAISS indexing & search
├── llm_service.py              # LLM integration
├── utils.py                    # Helper functions
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── data/
│   ├── pdf_cache/              # Cached PDF files
│   └── vector_store/           # FAISS index storage
├── logs/                       # Application logs
└── docs/                       # Documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Groq API key (free at https://console.groq.com/) or OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd RAG
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your API key
```

5. Run the application:
```bash
streamlit run app.py
```

The application will open at `http://localhost:8501`

## 📖 How RAG Works

### What is RAG?

Retrieval-Augmented Generation (RAG) is a technique that enhances LLM responses by retrieving relevant information from a knowledge base before generating answers.

### RAG Workflow

1. **Document Ingestion**: Upload PDF documents
2. **Text Extraction**: Extract raw text from PDFs using PyPDF2
3. **Chunking**: Split text into semantic chunks using RecursiveCharacterTextSplitter
4. **Embedding Generation**: Convert chunks to vector embeddings using sentence-transformers
5. **Vector Storage**: Store embeddings in FAISS vector database
6. **Query Processing**: 
   - Generate embedding for user query
   - Perform semantic similarity search in FAISS
   - Retrieve top-k most relevant chunks
7. **Answer Generation**: 
   - Pass retrieved chunks as context to LLM
   - Generate grounded answer using only provided context
   - Return answer with source citations

### Why RecursiveCharacterTextSplitter?

- **Semantic Preservation**: Tries to split on larger separators first (paragraphs, sentences)
- **Context Continuity**: Falls back to smaller separators only when needed
- **Reduced Fragmentation**: Minimizes cutting sentences in the middle
- **Flexible**: Adapts to different document structures

### Importance of Chunk Overlap

- **Context Preservation**: Ensures important information isn't split between chunks
- **Better Retrieval**: Overlapping chunks increase chance of capturing relevant context
- **Continuity**: Maintains semantic flow across chunk boundaries
- **Typical Overlap**: 10-20% of chunk size (e.g., 200 chars overlap for 1000 char chunks)

### Why FAISS is Fast

- **Optimized Indexing**: Uses efficient data structures (IVF, HNSW)
- **Approximate Search**: Trades slight accuracy for massive speed improvements
- **GPU Acceleration**: Supports GPU for faster operations
- **Memory Efficiency**: Compact storage and retrieval
- **Scalability**: Handles billion-scale vector searches

### Semantic Search vs Keyword Search

| Aspect | Semantic Search | Keyword Search |
|--------|----------------|----------------|
| Matching | Vector similarity (meaning) | Exact term matching |
| Understanding | Context and intent | Literal words |
| Flexibility | Handles synonyms/paraphrases | Requires exact terms |
| Use Case | Concept-based queries | Specific term queries |
| Example | "automobile" matches "car" | "car" only matches "car" |

### How Hallucinations are Reduced

1. **Grounding**: LLM instructed to use ONLY provided context
2. **Source Citations**: Every answer includes source references
3. **Low Temperature**: Reduces creative/incorrect responses
4. **Explicit Instructions**: Clear directives to not use outside knowledge
5. **Context Limitation**: Model cannot access training data for answers

## 🔧 Configuration

### Environment Variables

```env
GROQ_API_KEY=your_api_key_here
LLM_PROVIDER=groq
LLM_MODEL=llama3-70b-8192
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
```

### Chunking Parameters

- **CHUNK_SIZE**: 1000 characters (adjust based on document complexity)
- **CHUNK_OVERLAP**: 200 characters (20% overlap recommended)

### Search Parameters

- **TOP_K_RESULTS**: Number of chunks to retrieve (default: 5)
- **USE_HYBRID_SEARCH**: Combine semantic + keyword search (default: false)
- **SEMANTIC_WEIGHT**: Weight for semantic search (default: 0.7)
- **KEYWORD_WEIGHT**: Weight for keyword search (default: 0.3)

## 📊 Advanced Features

### Hybrid Search

Combines semantic similarity with keyword matching for better retrieval:

```python
# In rag_pipeline.py
pipeline = RAGPipeline(
    use_hybrid_search=True,
    semantic_weight=0.7,
    keyword_weight=0.3
)
```

### Re-ranking

Uses LLM to re-rank retrieved results for better relevance:

```python
result = pipeline.query(
    question="Your question",
    use_reranking=True
)
```

### Persistent Storage

Save and load vector indexes:

```python
# Save index
pipeline.save_index("my_index")

# Load index
pipeline.load_index("my_index")
```

### Streaming Responses

Enable real-time answer generation:

```python
result = pipeline.query(
    question="Your question",
    stream=True
)
```

## 🧪 Testing

### Example Queries

1. **Summarization**: "Summarize the main points of this document"
2. **Specific Information**: "What is the deadline mentioned in section 3?"
3. **Comparison**: "Compare the approaches described in chapters 1 and 2"
4. **Extraction**: "List all the dates mentioned in the document"
5. **Clarification**: "What does the author mean by 'strategic alignment'?"

### Sample Output

**User**: What are the key benefits of using RAG systems?

**Assistant**: According to the documents, the key benefits of RAG systems include:
1. **Reduced Hallucinations**: By grounding responses in retrieved context, RAG systems significantly reduce the likelihood of generating incorrect information
2. **Up-to-date Information**: Can access the latest information without retraining the model
3. **Transparency**: Source citations allow users to verify information
4. **Domain Adaptation**: Can be specialized for specific domains without fine-tuning

**Sources**: 
- [1] Source: rag_benefits.pdf (Page 3)
- [2] Source: ai_systems.pdf (Page 7)

## 🚢 Deployment

### Streamlit Cloud

1. Push code to GitHub
2. Go to https://share.streamlit.io/
3. Connect your GitHub repository
4. Add environment variables in deployment settings
5. Deploy

See `docs/DEPLOYMENT.md` for detailed deployment guide.

### Docker

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

## 📚 Documentation

- [Deployment Guide](docs/DEPLOYMENT.md)
- [System Design](docs/SYSTEM_DESIGN.md)
- [Interview Questions](docs/INTERVIEW_QUESTIONS.md)
- [Resume Bullet Points](docs/RESUME_BULLETS.md)
- [RAG Workflow](docs/RAG_WORKFLOW.md)
- [Evaluation Examples](docs/EVALUATION_EXAMPLES.md)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Streamlit for the amazing web framework
- LangChain for the LLM framework
- FAISS by Facebook Research for vector search
- Sentence Transformers for embeddings
- Groq for fast LLM inference

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

Built with ❤️ using Python, Streamlit, and modern AI technologies
