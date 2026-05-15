"""
RAG Pipeline Module
Complete Retrieval-Augmented Generation pipeline
"""

from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
import os

from pdf_processor import PDFProcessor
from vector_store import VectorStore, HybridSearch
from llm_service import LLMService, LLMConfig
from utils import setup_logger, format_source_citation, format_chat_message


class RAGPipeline:
    """
    Complete RAG pipeline orchestrating document processing, retrieval, and generation
    
    RAG Workflow:
    1. Upload PDF documents
    2. Extract text from PDFs
    3. Split text into chunks using RecursiveCharacterTextSplitter
    4. Generate embeddings using sentence-transformers
    5. Store embeddings in FAISS vector database
    6. For each query:
       - Generate query embedding
       - Perform semantic similarity search in FAISS
       - Retrieve top-k relevant chunks
       - Generate grounded answer using LLM with retrieved context
       - Return answer with source citations
    """
    
    def __init__(
        self,
        api_key: str,
        model_name: str = "all-MiniLM-L6-v2",
        llm_model: str = "llama3-70b-8192",
        llm_provider: str = "groq",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        use_hybrid_search: bool = False,
        persist_directory: str = "data/vector_store"
    ):
        """
        Initialize RAG pipeline with all components
        
        Args:
            api_key: API key for LLM service
            model_name: Sentence transformer model name
            llm_model: LLM model name
            llm_provider: LLM provider ('groq' or 'openai')
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            use_hybrid_search: Whether to use hybrid semantic+keyword search
            persist_directory: Directory for vector store persistence
        """
        self.logger = setup_logger("rag_pipeline")
        
        # Initialize PDF processor
        self.pdf_processor = PDFProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        # Initialize vector store
        if use_hybrid_search:
            self.vector_store = HybridSearch(
                model_name=model_name,
                semantic_weight=0.7,
                keyword_weight=0.3
            )
        else:
            self.vector_store = VectorStore(
                model_name=model_name,
                persist_directory=persist_directory
            )
        
        # Initialize LLM service
        llm_config = LLMConfig(
            api_key=api_key,
            model=llm_model,
            provider=llm_provider,
            temperature=0.1,
            streaming=True
        )
        self.llm_service = LLMService(llm_config)
        
        # Conversation history
        self.conversation_history: List[Dict[str, str]] = []
        
        # Track processed documents
        self.processed_documents: List[str] = []
        
        self.logger.info("RAG Pipeline initialized successfully")
    
    def process_documents(
        self,
        pdf_paths: List[str],
        save_index: bool = True
    ) -> Dict[str, Any]:
        """
        Process PDF documents and build vector index
        
        Args:
            pdf_paths: List of PDF file paths
            save_index: Whether to save the index to disk
            
        Returns:
            Processing statistics
        """
        self.logger.info(f"Processing {len(pdf_paths)} documents")
        
        # Process PDFs
        chunks = self.pdf_processor.process_multiple_pdfs(pdf_paths)
        
        if not chunks:
            raise ValueError("No chunks extracted from documents")
        
        # Add to vector store
        self.vector_store.add_documents(chunks)
        
        # Save index if requested
        if save_index:
            self.vector_store.save()
        
        # Track processed documents
        for pdf_path in pdf_paths:
            if pdf_path not in self.processed_documents:
                self.processed_documents.append(pdf_path)
        
        # Get statistics
        stats = self.pdf_processor.get_document_stats(chunks)
        stats["vector_store_stats"] = self.vector_store.get_stats()
        
        self.logger.info(f"Document processing complete: {stats}")
        return stats
    
    def query(
        self,
        question: str,
        k: int = 5,
        use_reranking: bool = False,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Query the RAG pipeline with a question
        
        Args:
            question: User question
            k: Number of chunks to retrieve
            use_reranking: Whether to use LLM re-ranking
            stream: Whether to stream the response
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        self.logger.info(f"Processing query: {question[:50]}...")
        
        # Check if vector store has documents
        if self.vector_store.index is None or self.vector_store.index.ntotal == 0:
            return {
                "answer": "No documents have been processed yet. Please upload PDF documents first.",
                "sources": [],
                "retrieved_chunks": []
            }
        
        # Perform search
        if isinstance(self.vector_store, HybridSearch):
            retrieved_chunks = self.vector_store.hybrid_search(question, k=k)
        else:
            retrieved_chunks = self.vector_store.search(question, k=k)
        
        if not retrieved_chunks:
            return {
                "answer": "No relevant information found in the documents.",
                "sources": [],
                "retrieved_chunks": []
            }
        
        # Re-rank if requested
        if use_reranking and len(retrieved_chunks) > 1:
            retrieved_chunks = self.llm_service.re_rank_results(
                question,
                retrieved_chunks,
                top_k=k
            )
        
        # Generate answer
        if stream:
            # For streaming, return generator
            answer_stream = self.llm_service.generate_answer_stream(
                question,
                retrieved_chunks,
                self.conversation_history
            )
            
            return {
                "answer_stream": answer_stream,
                "sources": [chunk["metadata"] for chunk in retrieved_chunks],
                "retrieved_chunks": retrieved_chunks
            }
        else:
            # Non-streaming
            result = self.llm_service.generate_answer(
                question,
                retrieved_chunks,
                self.conversation_history
            )
        
        # Add to conversation history
        self.conversation_history.append(format_chat_message("user", question))
        self.conversation_history.append(format_chat_message("assistant", result["answer"]))
        
        # Prepare response
        response = {
            "answer": result["answer"],
            "sources": [chunk["metadata"] for chunk in retrieved_chunks],
            "retrieved_chunks": retrieved_chunks,
            "source_citations": [
                format_source_citation(chunk, i)
                for i, chunk in enumerate(retrieved_chunks)
            ],
            "token_usage": {
                "prompt_tokens": result.get("prompt_tokens", 0),
                "completion_tokens": result.get("completion_tokens", 0),
                "total_tokens": result.get("total_tokens", 0)
            },
            "model": result.get("model", "unknown")
        }
        
        self.logger.info(f"Query processed successfully")
        return response
    
    def clear_conversation(self) -> None:
        """Clear conversation history"""
        self.logger.info("Clearing conversation history")
        self.conversation_history = []
    
    def clear_documents(self) -> None:
        """Clear all documents from vector store"""
        self.logger.info("Clearing all documents")
        self.vector_store.clear()
        self.processed_documents = []
        self.conversation_history = []
    
    def load_index(self, filename: str = "faiss_index") -> None:
        """
        Load saved vector index from disk
        
        Args:
            filename: Base filename for index
        """
        self.logger.info(f"Loading index: {filename}")
        self.vector_store.load(filename)
    
    def save_index(self, filename: str = "faiss_index") -> None:
        """
        Save vector index to disk
        
        Args:
            filename: Base filename for index
        """
        self.logger.info(f"Saving index: {filename}")
        self.vector_store.save(filename)
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the RAG pipeline
        
        Returns:
            Statistics dictionary
        """
        return {
            "processed_documents": len(self.processed_documents),
            "document_names": [Path(d).name for d in self.processed_documents],
            "conversation_length": len(self.conversation_history),
            "vector_store_stats": self.vector_store.get_stats()
        }
    
    def get_retrieval_evaluation(
        self,
        question: str,
        ground_truth_chunks: List[int],
        k: int = 5
    ) -> Dict[str, Any]:
        """
        Evaluate retrieval quality against ground truth
        
        Args:
            question: Query question
            ground_truth_chunks: Indices of relevant chunks
            k: Number of chunks to retrieve
            
        Returns:
            Evaluation metrics
        """
        # Retrieve chunks
        retrieved_chunks = self.vector_store.search(question, k=k)
        
        # Calculate metrics
        retrieved_indices = [
            chunk["metadata"].get("chunk_index", -1)
            for chunk in retrieved_chunks
        ]
        
        # Precision@k
        relevant_retrieved = sum(
            1 for idx in retrieved_indices if idx in ground_truth_chunks
        )
        precision_at_k = relevant_retrieved / k if k > 0 else 0
        
        # Recall@k
        recall_at_k = relevant_retrieved / len(ground_truth_chunks) if ground_truth_chunks else 0
        
        # MRR (Mean Reciprocal Rank)
        mrr = 0
        for i, idx in enumerate(retrieved_indices):
            if idx in ground_truth_chunks:
                mrr = 1 / (i + 1)
                break
        
        return {
            "question": question,
            "retrieved_indices": retrieved_indices,
            "ground_truth_indices": ground_truth_chunks,
            "precision_at_k": precision_at_k,
            "recall_at_k": recall_at_k,
            "mrr": mrr,
            "relevant_retrieved": relevant_retrieved
        }
