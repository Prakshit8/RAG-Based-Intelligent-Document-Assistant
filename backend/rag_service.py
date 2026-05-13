import os
import uuid
from typing import List, Dict, Any
from datetime import datetime
import PyPDF2
from groq import Groq
from sentence_transformers import SentenceTransformer
import numpy as np
from models import DocumentUpload, QuestionResponse, ChunkInfo

class RAGService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_groq_api_key_here":
            raise ValueError("GROQ_API_KEY is not set or is using placeholder value. Please set a valid API key in your .env file.")
        self.groq_client = Groq(api_key=api_key)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.documents: Dict[str, Dict] = {}
        self.chunks: List[ChunkInfo] = []
        
    def extract_pdf_text(self, pdf_content: bytes) -> str:
        """Extract text from PDF bytes"""
        try:
            import io
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text
        except Exception as e:
            raise Exception(f"Error extracting PDF text: {str(e)}")
    
    def create_chunks(self, text: str, document_id: str, chunk_size: int = 1000, overlap: int = 200) -> List[ChunkInfo]:
        """Create text chunks from document text"""
        chunks = []
        sentences = text.split('. ')
        
        current_chunk = ""
        chunk_index = 0
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                chunk_id = f"{document_id}-{chunk_index}"
                chunks.append(ChunkInfo(
                    id=chunk_id,
                    document_id=document_id,
                    text=current_chunk.strip(),
                    chunk_index=chunk_index
                ))
                current_chunk = sentence
                chunk_index += 1
            else:
                current_chunk += sentence + ". "
        
        # Add remaining text
        if current_chunk.strip():
            chunk_id = f"{document_id}-{chunk_index}"
            chunks.append(ChunkInfo(
                id=chunk_id,
                document_id=document_id,
                text=current_chunk.strip(),
                chunk_index=chunk_index
            ))
        
        return chunks
    
    def generate_embeddings(self, chunks: List[ChunkInfo]) -> List[ChunkInfo]:
        """Generate embeddings for text chunks"""
        texts = [chunk.text for chunk in chunks]
        embeddings = self.embedding_model.encode(texts)
        
        for i, chunk in enumerate(chunks):
            chunk.embedding = embeddings[i].tolist()
        
        return chunks
    
    def semantic_search(self, query: str, max_results: int = 3) -> List[ChunkInfo]:
        """Perform semantic search on document chunks"""
        if not self.chunks:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0]
        
        # Calculate similarities
        scored_chunks = []
        for chunk in self.chunks:
            if chunk.embedding:
                chunk_embedding = np.array(chunk.embedding)
                similarity = np.dot(query_embedding, chunk_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(chunk_embedding)
                )
                scored_chunks.append((chunk, similarity))
        
        # Sort by similarity and return top results
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in scored_chunks[:max_results] if _ > 0.1]
    
    def keyword_search(self, query: str, max_results: int = 3) -> List[ChunkInfo]:
        """Perform keyword search on document chunks"""
        query_words = query.lower().split()
        scored_chunks = []
        
        for chunk in self.chunks:
            chunk_text = chunk.text.lower()
            score = 0
            
            for word in query_words:
                if len(word) > 2:
                    matches = chunk_text.count(word)
                    score += matches * (len(word) / 10)
            
            if score > 0:
                scored_chunks.append((chunk, score))
        
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in scored_chunks[:max_results]]
    
    def hybrid_search(self, query: str, max_results: int = 3) -> List[ChunkInfo]:
        """Perform hybrid search combining semantic and keyword search"""
        semantic_results = self.semantic_search(query, max_results * 2)
        keyword_results = self.keyword_search(query, max_results * 2)
        
        # Combine results
        combined = {}
        
        # Add semantic results (70% weight)
        for chunk in semantic_results:
            combined[chunk.id] = {
                'chunk': chunk,
                'score': 0.7  # Will be calculated properly
            }
        
        # Add keyword results (30% weight)
        for chunk in keyword_results:
            if chunk.id in combined:
                combined[chunk.id]['score'] += 0.3
            else:
                combined[chunk.id] = {
                    'chunk': chunk,
                    'score': 0.3
                }
        
        # Sort and return top results
        results = sorted(combined.values(), key=lambda x: x['score'], reverse=True)
        return [item['chunk'] for item in results[:max_results]]
    
    async def generate_answer(self, question: str, context_chunks: List[ChunkInfo]) -> QuestionResponse:
        """Generate answer using Groq AI"""
        if not context_chunks:
            return QuestionResponse(
                answer="I couldn't find relevant information in your documents. Please try rephrasing your question or upload more documents.",
                sources=[],
                confidence=0.0
            )
        
        # Create context from chunks
        context = "\n\n".join([f"Document {i+1}: {chunk.text}" for i, chunk in enumerate(context_chunks)])
        
        # Generate prompt
        prompt = f"""Based on the following context, answer the question clearly and comprehensively.

CONTEXT:
{context}

QUESTION: {question}

Please provide a well-structured answer using:
- Clear headings or bullet points when appropriate
- Specific details from the context
- Easy-to-read formatting
- Direct, concise language

IMPORTANT: If the question asks for visual explanations like flowcharts, graphs, diagrams, or process flows, create them using Mermaid syntax. Include the Mermaid code in markdown code blocks with mermaid language identifier.

Examples of when to use Mermaid:
- Process flows and workflows
- System architectures
- Decision trees
- Timeline diagrams
- Relationship diagrams
- Step-by-step procedures

Mermaid syntax examples:
- Flowcharts: ```mermaid\ngraph TD\n    A[Start] --> B[Process]\n```
- Sequence diagrams: ```mermaid\nsequenceDiagram\n    A->>B: Message\n```
- Pie charts: ```mermaid\npie\n    title Data Distribution\n    "Category A" : 30\n    "Category B" : 70\n```

If the context doesn't contain enough information, clearly state what information is available and what is missing.

ANSWER:"""
        
        try:
            # Generate answer using Groq
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant that answers questions based on provided context. Always provide clear, well-structured answers with proper formatting. Use bullet points, numbered lists, or paragraphs to make your answers easy to read and understand. Be direct and specific. When questions require visual explanations like flowcharts, graphs, or diagrams, create them using Mermaid syntax in markdown code blocks."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.5,
                max_tokens=1000
            )
            
            answer = chat_completion.choices[0].message.content
            
            # Generate follow-up questions
            follow_up_prompt = f"""Based on this question and answer, generate 3 relevant follow-up questions:

Question: {question}
Answer: {answer}

Generate 3 follow-up questions, one per line:"""
            
            follow_up_completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "user", "content": follow_up_prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.3,
                max_tokens=200
            )
            
            follow_up_text = follow_up_completion.choices[0].message.content
            follow_up_questions = [q.strip() for q in follow_up_text.split('\n') if q.strip()][:3]
            
            # Calculate confidence based on search scores
            confidence = min(len(context_chunks) / 3.0, 1.0)  # Simple confidence calculation
            
            # Create sources
            sources = [
                {
                    "document_id": chunk.document_id,
                    "chunk_id": chunk.id,
                    "chunk_index": chunk.chunk_index,
                    "text_preview": chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text
                }
                for chunk in context_chunks
            ]
            
            return QuestionResponse(
                answer=answer,
                sources=sources,
                confidence=confidence,
                follow_up_questions=follow_up_questions
            )
            
        except Exception as e:
            return QuestionResponse(
                answer=f"Error generating answer: {str(e)}",
                sources=[],
                confidence=0.0
            )
    
    def upload_document(self, filename: str, content: bytes) -> str:
        """Upload and process a document"""
        document_id = str(uuid.uuid4())
        
        # Extract text from PDF
        text = self.extract_pdf_text(content)
        
        # Create chunks
        chunks = self.create_chunks(text, document_id)
        
        # Generate embeddings
        chunks_with_embeddings = self.generate_embeddings(chunks)
        
        # Store document and chunks
        self.documents[document_id] = {
            'id': document_id,
            'filename': filename,
            'file_size': len(content),
            'chunk_count': len(chunks),
            'uploaded_at': datetime.now(),
            'status': 'processed'
        }
        
        self.chunks.extend(chunks_with_embeddings)
        
        return document_id
    
    def get_document_list(self) -> List[Dict]:
        """Get list of all documents"""
        return list(self.documents.values())
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        return {
            'document_count': len(self.documents),
            'total_chunks': len(self.chunks),
            'total_text_length': sum(len(chunk.text) for chunk in self.chunks)
        }
