# RAG-Based Intelligent Document Assistant

**An advanced AI-powered document assistant that answers questions about your PDFs with interactive diagrams and visual explanations**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Groq](https://img.shields.io/badge/Groq-AI-purple.svg)

## Features

### Core Functionality
- **PDF Upload & Processing**: Seamlessly upload and process PDF documents
- **Intelligent Chunking**: Smart text segmentation with overlapping context
- **Semantic Search**: Advanced vector embeddings for precise content retrieval
- **Hybrid Search**: Combines semantic and keyword search for best results
- **AI-Powered Q&A**: Uses Groq AI for intelligent, context-aware answers

### Visual Intelligence
- **Diagram Generation**: Automatically creates flowcharts, graphs, and diagrams
- **Mermaid Integration**: Interactive visualizations rendered in real-time
- **Process Flows**: Visual explanations for complex processes
- **Architecture Diagrams**: System and workflow visualizations

### User Experience
- **Modern Web Interface**: Clean, responsive design with Tailwind CSS
- **Context Sources**: Shows which document chunks provided answers
- **Follow-up Questions**: Generates relevant next questions automatically
- **Document Management**: List, view, and delete documents easily
- **Real-time Feedback**: Live status updates and progress indicators

## Quick Start

### Prerequisites
- Python 3.8+
- Groq API key (get one at [console.groq.com](https://console.groq.com))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Prakshit8/RAG-Based-Intelligent-Document-Assistant.git
cd RAG-Based-Intelligent-Document-Assistant
```

2. **Install dependencies**
```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

3. **Set up environment**
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Groq API key
GROQ_API_KEY=your_groq_api_key_here
```

4. **Run the application**
```bash
# Using uv
uv run uvicorn main:app --reload

# Or using python
python main.py
```

5. **Access the application**
- Web Interface: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Usage Examples

### Web Interface
1. Open http://localhost:8000 in your browser
2. Upload a PDF document using the drag-and-drop interface
3. Ask questions about your document
4. Receive answers with interactive diagrams and visual explanations

### API Usage

#### Upload a Document
```bash
curl -X POST "http://localhost:8000/upload-pdf" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

#### Ask a Question
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Create a flowchart showing the machine learning process",
    "max_context_chunks": 3
  }'
```

#### Sample Response with Diagram
```json
{
  "answer": "Here's a flowchart showing the machine learning process:\n\n```mermaid\ngraph TD\n    A[Data Collection] --> B[Data Preprocessing]\n    B --> C[Feature Engineering]\n    C --> D[Model Selection]\n    D --> E[Model Training]\n    E --> F[Model Evaluation]\n    F --> G[Deployment]\n    G --> H[Monitoring]\n    H -->|Retraining Needed| C\n```\n\nThe machine learning process is iterative and involves several key stages...",
  "sources": [...],
  "confidence": 0.9,
  "follow_up_questions": [...]
}
```

## Diagram Generation

The assistant can create various types of diagrams:

### Flowcharts
```
"Create a flowchart showing the software development lifecycle"
```

### Process Diagrams
```
"Draw a diagram of the A* algorithm process"
```

### Architecture Diagrams
```
"Show the architecture of a microservices system"
```

### Decision Trees
```
"Create a decision tree for loan approval"
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information and endpoints |
| GET | `/health` | System health check with statistics |
| POST | `/upload-pdf` | Upload and process PDF documents |
| POST | `/ask` | Ask questions about documents |
| GET | `/documents` | List all uploaded documents |
| DELETE | `/documents/{id}` | Delete a specific document |
| GET | `/stats` | System statistics and metrics |

## Technology Stack

### Backend
- **FastAPI**: High-performance async web framework
- **Groq**: Ultra-fast AI inference
- **Sentence Transformers**: State-of-the-art embeddings
- **PyPDF2**: PDF text extraction
- **NumPy**: Numerical computations

### Frontend
- **HTML5/CSS3**: Modern web standards
- **Tailwind CSS**: Utility-first CSS framework
- **JavaScript ES6+**: Modern JavaScript features
- **Mermaid.js**: Diagram generation library

### AI/ML
- **all-MiniLM-L6-v2**: Sentence embedding model
- **llama-3.3-70b-versatile**: Groq's powerful language model
- **Hybrid Search**: Semantic + keyword search algorithm

## Configuration

### Environment Variables
```bash
GROQ_API_KEY=your_groq_api_key_here          # Required
INNGEST_EVENT_KEY=your_inngest_key_here      # Optional (async processing)
```

### Search Parameters
- **Chunk Size**: 1000 characters with 200 overlap
- **Embedding Model**: all-MiniLM-L6-v2
- **AI Model**: llama-3.3-70b-versatile
- **Max Context Chunks**: 3 (configurable per request)

## Project Structure

```
RAG-Based-Intelligent-Document-Assistant/
|
|-- main.py              # FastAPI application and routes
|-- models.py            # Pydantic data models
|-- rag_service.py       # Core RAG logic and AI services
|-- index.html           # Web interface
|-- script.js            # Frontend JavaScript
|-- styles.css           # Custom CSS styles
|-- test_client.py        # API testing client
|-- pyproject.toml       # Project dependencies
|-- .env.example         # Environment variables template
|-- README.md           # This file
```

## Development

### Running Tests
```bash
# Test API endpoints
uv run python test_client.py

# Test error handling
uv run python test_errors.py
```

### Adding New Features
1. Extend `RAGService` for new search methods
2. Add new endpoints in `main.py`
3. Update models in `models.py`
4. Add frontend components in `index.html` and `script.js`

### Code Style
- Follow PEP 8 for Python code
- Use semantic HTML5
- Write descriptive commit messages
- Add tests for new features

## Production Deployment

### Docker Deployment
```dockerfile
# Dockerfile example
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Setup
- Use environment variables for configuration
- Implement proper logging and monitoring
- Set up rate limiting and authentication
- Use Redis/database for persistence

## Troubleshooting

### Common Issues

#### API Key Error
```
Error: GROQ_API_KEY is not set or is using placeholder value
```
**Solution**: Get an API key from https://console.groq.com and update your `.env` file.

#### Module Not Found
```
Error: ModuleNotFoundError: No module named 'groq'
```
**Solution**: Install dependencies with `uv sync` or `pip install -r requirements.txt`.

#### Server Connection Refused
**Solution**: Ensure the server is running on port 8000 and check your firewall settings.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Groq](https://groq.com/) for providing fast AI inference
- [Sentence Transformers](https://www.sbert.net/) for embedding models
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [Mermaid.js](https://mermaid-js.github.io/) for diagram generation

## Support

If you find this project helpful, please give it a star! For issues and questions:
- Open an issue on GitHub
- Check the [documentation](http://localhost:8000/docs)
- Review the troubleshooting section above

---

**Made with AI and diagrams** ð¦¤â¨ï¸
