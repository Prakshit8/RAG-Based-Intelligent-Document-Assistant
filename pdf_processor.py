"""
PDF Processor Module
Handles PDF text extraction, document processing, and chunking
"""

import PyPDF2
from typing import List, Dict, Any, Tuple
import logging
from pathlib import Path
import uuid

from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils import setup_logger, generate_document_id, clean_text, get_timestamp, merge_metadata


class PDFProcessor:
    """
    Process PDF documents: extract text, split into chunks, and prepare for embedding
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: List[str] = None
    ):
        """
        Initialize PDF processor with chunking parameters
        
        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
            separators: List of separators for splitting (default: paragraph, sentence, word)
        """
        self.logger = setup_logger("pdf_processor")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Default separators: paragraph, sentence, word, character
        if separators is None:
            separators = ["\n\n", "\n", ". ", " ", ""]
        
        # Initialize RecursiveCharacterTextSplitter
        # Why RecursiveCharacterTextSplitter?
        # - It tries to split on larger separators first (paragraphs)
        # - Falls back to smaller separators (sentences, words) if needed
        # - Preserves semantic meaning better than fixed-size splitting
        # - Reduces chance of cutting sentences in the middle
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=len
        )
        
        self.logger.info(f"PDFProcessor initialized with chunk_size={chunk_size}, overlap={chunk_overlap}")
    
    def extract_text_from_pdf(self, pdf_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Extract all text from a PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Tuple of (extracted_text, metadata)
        """
        self.logger.info(f"Extracting text from: {pdf_path}")
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Get PDF metadata
                num_pages = len(pdf_reader.pages)
                pdf_info = pdf_reader.metadata or {}
                
                # Extract text from all pages
                text_content = []
                for page_num, page in enumerate(pdf_reader.pages, start=1):
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_content.append(f"--- Page {page_num} ---\n{page_text}")
                
                full_text = "\n\n".join(text_content)
                full_text = clean_text(full_text)
                
                # Create metadata
                metadata = {
                    "source": Path(pdf_path).name,
                    "file_path": pdf_path,
                    "num_pages": num_pages,
                    "document_id": generate_document_id(),
                    "processed_at": get_timestamp(),
                    "pdf_info": {
                        "title": pdf_info.get('/Title', 'Unknown'),
                        "author": pdf_info.get('/Author', 'Unknown'),
                        "creator": pdf_info.get('/Creator', 'Unknown')
                    }
                }
                
                self.logger.info(f"Extracted {len(full_text)} characters from {num_pages} pages")
                return full_text, metadata
                
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def split_text_into_chunks(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Split text into semantic chunks with metadata
        
        Args:
            text: Full text to split
            metadata: Document metadata to attach to each chunk
            
        Returns:
            List of chunks with metadata
        """
        self.logger.info(f"Splitting text into chunks (chunk_size={self.chunk_size})")
        
        # Split text using RecursiveCharacterTextSplitter
        chunks = self.text_splitter.split_text(text)
        
        # Create chunk objects with metadata
        chunk_objects = []
        for idx, chunk_text in enumerate(chunks):
            chunk_metadata = merge_metadata(metadata, {
                "chunk_index": idx,
                "chunk_size": len(chunk_text),
                "total_chunks": len(chunks)
            })
            
            chunk_objects.append({
                "text": chunk_text,
                "metadata": chunk_metadata
            })
        
        self.logger.info(f"Created {len(chunks)} chunks from document")
        return chunk_objects
    
    def process_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Complete pipeline: extract text and split into chunks
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of chunks with metadata
        """
        self.logger.info(f"Processing PDF: {pdf_path}")
        
        # Extract text
        text, metadata = self.extract_text_from_pdf(pdf_path)
        
        # Split into chunks
        chunks = self.split_text_into_chunks(text, metadata)
        
        return chunks
    
    def process_multiple_pdfs(self, pdf_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Process multiple PDF files and combine all chunks
        
        Args:
            pdf_paths: List of PDF file paths
            
        Returns:
            List of all chunks from all PDFs
        """
        self.logger.info(f"Processing {len(pdf_paths)} PDF files")
        
        all_chunks = []
        for pdf_path in pdf_paths:
            try:
                chunks = self.process_pdf(pdf_path)
                all_chunks.extend(chunks)
            except Exception as e:
                self.logger.error(f"Failed to process {pdf_path}: {e}")
                continue
        
        self.logger.info(f"Total chunks from all PDFs: {len(all_chunks)}")
        return all_chunks
    
    def get_document_stats(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about processed documents
        
        Args:
            chunks: List of processed chunks
            
        Returns:
            Statistics dictionary
        """
        if not chunks:
            return {"total_chunks": 0, "total_documents": 0}
        
        # Count unique documents
        document_ids = set(chunk["metadata"].get("document_id") for chunk in chunks)
        
        # Calculate chunk sizes
        chunk_sizes = [len(chunk["text"]) for chunk in chunks]
        
        stats = {
            "total_chunks": len(chunks),
            "total_documents": len(document_ids),
            "avg_chunk_size": sum(chunk_sizes) / len(chunk_sizes),
            "min_chunk_size": min(chunk_sizes),
            "max_chunk_size": max(chunk_sizes),
            "total_characters": sum(chunk_sizes)
        }
        
        return stats
