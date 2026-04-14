from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DocumentUpload(BaseModel):
    filename: str
    content: str
    file_size: int

class QuestionRequest(BaseModel):
    question: str
    max_context_chunks: int = 3

class QuestionResponse(BaseModel):
    answer: str
    sources: List[dict]
    confidence: float
    follow_up_questions: List[str] = []

class DocumentInfo(BaseModel):
    id: str
    filename: str
    file_size: int
    chunk_count: int
    uploaded_at: datetime
    status: str

class ChunkInfo(BaseModel):
    id: str
    document_id: str
    text: str
    chunk_index: int
    embedding: Optional[List[float]] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    document_count: int
    total_chunks: int
