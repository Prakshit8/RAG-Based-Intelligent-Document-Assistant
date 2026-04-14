from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import inngest
import os
import datetime
from pathlib import Path
from typing import List
import logging

from .models import DocumentUpload, QuestionRequest, QuestionResponse, DocumentInfo, HealthResponse
from .rag_service import RAGService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG Production API",
    description="Document RAG Q&A System with PDF Upload and AI-powered Q&A",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

# Initialize services
try:
    rag_service = RAGService()
    inngest_client = inngest.Inngest(app_id="rag-app")
    logger.info("RAG Service initialized successfully")
except ValueError as e:
    logger.error(f"Failed to initialize RAG Service: {str(e)}")
    rag_service = None
    inngest_client = None

# Mount static files for frontend
frontend_path = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_path), html=True), name="static")

@app.get("/")
async def root():
    # Serve the frontend HTML file
    try:
        html_path = Path(__file__).parent.parent / "frontend" / "index.html"
        logger.info(f"Looking for HTML at: {html_path}")
        logger.info(f"HTML exists: {html_path.exists()}")
        
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
            logger.info("Successfully loaded HTML file")
            return HTMLResponse(content=content, media_type="text/html")
    except Exception as e:
        logger.error(f"Error loading HTML: {str(e)}")
        return {
            "message": "RAG Production API is running",
            "version": "1.0.0",
            "endpoints": {
                "upload_pdf": "POST /upload-pdf",
                "ask": "POST /ask",
                "documents": "GET /documents",
                "health": "GET /health"
            }
        }

@app.get("/api")
async def api_info():
    return {
        "message": "RAG Production API is running",
        "version": "1.0.0",
        "endpoints": {
            "upload_pdf": "POST /upload-pdf",
            "ask": "POST /ask",
            "documents": "GET /documents",
            "health": "GET /health"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    if rag_service is None:
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.datetime.now(),
            document_count=0,
            total_chunks=0
        )
    stats = rag_service.get_stats()
    return HealthResponse(
        status="healthy",
        timestamp=datetime.datetime.now(),
        document_count=stats['document_count'],
        total_chunks=stats['total_chunks']
    )

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process a PDF document"""
    if rag_service is None:
        raise HTTPException(status_code=503, detail="RAG Service is not available. Please check your API key configuration.")
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Read file content
        content = await file.read()
        
        # Process document
        document_id = rag_service.upload_document(file.filename, content)
        
        logger.info(f"Successfully uploaded and processed: {file.filename}")
        
        return {
            "message": "PDF uploaded and processed successfully",
            "document_id": document_id,
            "filename": file.filename,
            "file_size": len(content),
            "status": "processed"
        }
        
    except Exception as e:
        logger.error(f"Error processing PDF {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question about uploaded documents"""
    if rag_service is None:
        raise HTTPException(status_code=503, detail="RAG Service is not available. Please check your API key configuration.")
    
    try:
        # Search for relevant chunks
        relevant_chunks = rag_service.hybrid_search(
            request.question, 
            request.max_context_chunks
        )
        
        # Generate answer
        response = await rag_service.generate_answer(request.question, relevant_chunks)
        
        logger.info(f"Processed question: {request.question[:50]}...")
        return response
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.get("/documents")
async def get_documents():
    """Get list of all uploaded documents"""
    if rag_service is None:
        raise HTTPException(status_code=503, detail="RAG Service is not available. Please check your API key configuration.")
    
    try:
        documents = rag_service.get_document_list()
        return {
            "documents": documents,
            "count": len(documents)
        }
    except Exception as e:
        logger.error(f"Error fetching documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching documents: {str(e)}")

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a specific document"""
    if rag_service is None:
        raise HTTPException(status_code=503, detail="RAG Service is not available. Please check your API key configuration.")
    
    try:
        if document_id not in rag_service.documents:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Remove document and its chunks
        del rag_service.documents[document_id]
        rag_service.chunks = [chunk for chunk in rag_service.chunks if chunk.document_id != document_id]
        
        logger.info(f"Deleted document: {document_id}")
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    if rag_service is None:
        raise HTTPException(status_code=503, detail="RAG Service is not available. Please check your API key configuration.")
    
    try:
        return rag_service.get_stats()
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")

# Inngest function for async PDF processing
if inngest_client is not None:
    @inngest_client.create_function(
        fn_id="async_pdf_ingestion",
        trigger=inngest.TriggerEvent(event="rag/async_ingest_pdf"),
    )
    async def async_pdf_ingestion(ctx: inngest.Context, step: inngest.Step):
        """Handle async PDF ingestion via Inngest"""
        try:
            data = ctx.event.data
            file_content = data.get('content')
            filename = data.get('filename')
            
            # Process PDF
            document_id = rag_service.upload_document(filename, file_content)
            
            return {
                "status": "success",
                "document_id": document_id,
                "filename": filename
            }
            
        except Exception as e:
            logger.error(f"Error in async PDF ingestion: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
