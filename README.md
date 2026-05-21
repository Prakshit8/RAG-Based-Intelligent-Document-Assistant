# DocuPilot AI

DocuPilot AI is a Streamlit-based document automation assistant for uploading PDF documents, building a FAISS vector index, asking grounded questions, and generating useful document intelligence outputs such as summaries, action items, risk scans, suggested questions, and downloadable chat reports.

This project goes beyond a basic RAG chatbot. It combines document retrieval, LLM reasoning, source citations, and one-click AI automation workflows.

## Features

- Upload and process one or more PDF documents
- Extract, chunk, embed, and index PDF text
- Store document chunks in a FAISS vector database
- Ask questions through a chat interface
- Generate grounded answers using retrieved document context
- Show source citations for assistant responses
- Run AI automation actions:
  - Generate Summary
  - Extract Actions
  - Find Risks
  - Suggest Questions
- Download a Markdown chat report after conversations
- Include processed documents, pipeline stats, AI action outputs, chat transcript, and sources in the report
- Keep LLM usage provider-independent through the `LLMService` abstraction
- Prevent document upload from crashing when optional AI generation fails

## Tech Stack

- Python
- Streamlit
- FAISS
- Sentence Transformers
- PyPDF2
- LangChain text splitters
- Groq API or OpenAI API

## Project Structure

```text
RAG/
+-- app.py                  # Streamlit UI and AI automation actions
+-- rag_pipeline.py         # End-to-end RAG orchestration
+-- pdf_processor.py        # PDF extraction and chunking
+-- vector_store.py         # FAISS indexing and semantic search
+-- llm_service.py          # LLM provider abstraction
+-- utils.py                # Logging, validation, and helper functions
+-- requirements.txt        # Python dependencies
+-- data/
|   +-- vector_store/       # Saved FAISS index files
+-- logs/                   # Runtime logs
+-- docs/                   # Supporting documentation
```

## How It Works

1. User uploads PDF files in the Streamlit sidebar.
2. Text is extracted from each PDF.
3. Text is split into overlapping chunks.
4. Sentence Transformer embeddings are generated for each chunk.
5. Chunks and embeddings are stored in FAISS.
6. User asks a question or runs an AI action.
7. The app retrieves relevant chunks with semantic search.
8. Retrieved chunks are passed to the LLM through `LLMService.generate_answer()`.
9. The LLM returns grounded output with source metadata.
10. The user can download a Markdown report of the chat and AI results.

## AI Automation Actions

The sidebar includes focused automation buttons after documents are processed.

| Action | Purpose |
| --- | --- |
| Generate Summary | Creates a decision-ready document brief |
| Extract Actions | Finds tasks, owners, deadlines, priorities, and evidence |
| Find Risks | Identifies risks, blockers, gaps, assumptions, and next steps |
| Suggest Questions | Generates smart questions users should ask about the documents |

Each action retrieves relevant document chunks from FAISS, sends only those chunks to the LLM, stores the result in session state, and displays source references.

## Chat Report Export

After a conversation or AI action, the app can generate a downloadable Markdown report.

The report includes:

- report generation timestamp
- processed document names
- pipeline statistics
- AI automation results
- full chat transcript
- source citations for assistant answers and AI actions

This makes the app useful as a lightweight document analysis workflow, not only a Q&A tool.

## Setup

### 1. Create a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\activate
```

On macOS/Linux:

```bash
python -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Streamlit secrets

Create this file:

```text
.streamlit/secrets.toml
```

For Groq:

```toml
GROQ_API_KEY = "your_groq_api_key"
LLM_PROVIDER = "groq"
LLM_MODEL = "llama-3.1-8b-instant"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
```

For OpenAI:

```toml
GROQ_API_KEY = "your_openai_api_key"
LLM_PROVIDER = "openai"
LLM_MODEL = "gpt-4o-mini"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
```

Note: the app currently reads the key from `GROQ_API_KEY` even when `LLM_PROVIDER` is set to `openai`.

### 4. Run the app

```bash
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

## Usage

1. Upload one or more PDF files.
2. Click `Process Documents`.
3. Ask questions in the chat box.
4. Use `Generate Summary`, `Extract Actions`, `Find Risks`, or `Suggest Questions`.
5. Download the chat report from the sidebar.

## Example Questions

- What is this document mainly about?
- What are the most important deadlines?
- Who owns the next steps?
- What risks or gaps are mentioned?
- Summarize the requirements in simple language.
- What questions should I ask before making a decision?

## Why This Is a Good AI Automation Project

This project demonstrates:

- RAG architecture
- vector search with FAISS
- embedding-based semantic retrieval
- PDF document processing
- LLM abstraction design
- grounded answer generation
- source citation handling
- AI workflow automation
- Streamlit product UI
- exportable reporting
- safer failure handling around LLM calls

## Important Implementation Detail

All LLM calls should go through:

```python
llm_service.generate_answer(query, context_chunks, conversation_history)
```

Avoid directly calling provider SDK internals from the app, such as:

```python
llm_service.client.chat.completions.create(...)
```

Keeping calls inside `LLMService` makes the app modular and provider-independent.

## Configuration Notes

Default values are defined in `app.py` and `llm_service.py`.

Common settings:

- `LLM_PROVIDER`: `groq` or `openai`
- `LLM_MODEL`: model name used by the selected provider
- `CHUNK_SIZE`: number of characters per chunk
- `CHUNK_OVERLAP`: overlap between chunks

The default embedding model is:

```text
all-MiniLM-L6-v2
```

## Limitations

- Currently supports PDF input only.
- Report export is Markdown, not PDF or DOCX.
- Uploaded files are processed during the active Streamlit session.
- OpenAI provider support uses the same API key setting name currently used for Groq.

## Future Improvements

- Export reports as PDF or DOCX
- Add document comparison between multiple PDFs
- Add entity extraction for people, companies, dates, and amounts
- Add automation history
- Add persistent chat sessions
- Add filters for source documents and pages
- Add evaluation metrics for retrieval quality
- Add user-selectable action templates

## Run Checks

Compile the main app:

```bash
python -B -m py_compile app.py
```

Run the app:

```bash
streamlit run app.py
```

## License

This project is intended for learning, portfolio use, and experimentation. Add a license file before publishing publicly.
