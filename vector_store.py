"""
Vector Store Module
Handles FAISS indexing, embedding generation, and similarity search
"""

import pickle
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import logging

from sentence_transformers import SentenceTransformer
import faiss
from utils import setup_logger, get_timestamp


class VectorStore:
    """
    FAISS-based vector store for semantic similarity search
    
    Why FAISS?
    - Facebook AI Similarity Search (FAISS) is optimized for fast similarity search
    - Uses efficient indexing structures (IVF, HNSW) for billion-scale vectors
    - GPU acceleration support for faster operations
    - Memory-efficient storage and retrieval
    - Open-source and production-ready
    """
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        index_type: str = "flat",
        vector_dimension: int = 384,
        persist_directory: str = "data/vector_store"
    ):
        """
        Initialize vector store with embedding model and FAISS index
        
        Args:
            model_name: Sentence transformer model name
            index_type: Type of FAISS index ('flat', 'ivf', 'hnsw')
            vector_dimension: Dimension of embedding vectors
            persist_directory: Directory to save/load index
        """
        self.logger = setup_logger("vector_store")
        self.model_name = model_name
        self.persist_directory = persist_directory
        self.vector_dimension = vector_dimension
        
        
        
        self.logger.info(f"Loading embedding model: {model_name}")
        self.embedding_model = SentenceTransformer(model_name)
        
        
        self.index = None
        self.index_type = index_type
        self.documents = []  # Store document texts
        self.metadata = []  # Store metadata for each document
        
        # Create persist directory
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"VectorStore initialized with {index_type} index")
    
    def create_index(self, index_type: str = None) -> faiss.Index:
        """
        Create FAISS index based on type
        
        Args:
            index_type: Type of index ('flat', 'ivf', 'hnsw')
            
        Returns:
            FAISS index object
        """
        if index_type is None:
            index_type = self.index_type
        
        dimension = self.vector_dimension
        
        if index_type == "flat":
            # Flat index: Exact search, O(n) complexity
            # Best for accuracy, slower for large datasets
            index = faiss.IndexFlatL2(dimension)
            self.logger.info("Created FlatL2 index (exact search)")
            
        elif index_type == "ivf":
            # IVF (Inverted File Index): Approximate search, O(sqrt(n))
            # Faster for large datasets, slight accuracy trade-off
            nlist = 100  # Number of clusters
            quantizer = faiss.IndexFlatL2(dimension)
            index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
            self.logger.info("Created IVFFlat index (approximate search)")
            
        elif index_type == "hnsw":
            # HNSW (Hierarchical Navigable Small World): Fast approximate search
            # Best balance of speed and accuracy for large datasets
            M = 16  # Number of connections per node
            index = faiss.IndexHNSWFlat(dimension, M)
            self.logger.info("Created HNSW index (fast approximate search)")
            
        else:
            raise ValueError(f"Unknown index type: {index_type}")
        
        return index
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings
            
        Returns:
            Numpy array of embeddings
        """
        self.logger.info(f"Generating embeddings for {len(texts)} texts")
        
        # Generate embeddings using sentence transformer
        embeddings = self.embedding_model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True  # Normalize for cosine similarity
        )
        
        self.logger.info(f"Generated embeddings with shape: {embeddings.shape}")
        return embeddings
    
    def add_documents(
        self,
        chunks: List[Dict[str, Any]],
        train_index: bool = True
    ) -> None:
        """
        Add document chunks to the vector store
        
        Args:
            chunks: List of chunks with 'text' and 'metadata'
            train_index: Whether to train the index (for IVF)
        """
        self.logger.info(f"Adding {len(chunks)} chunks to vector store")
        
        # Extract texts and metadata
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.generate_embeddings(texts)
        
        # Initialize index if not exists
        if self.index is None:
            self.index = self.create_index()
        
        # Add embeddings to index
        # For IVF index, need to train first
        if self.index_type == "ivf" and train_index:
            self.logger.info("Training IVF index...")
            self.index.train(embeddings)
        
        self.index.add(embeddings.astype('float32'))
        
        # Store documents and metadata
        self.documents.extend(texts)
        self.metadata.extend(metadatas)
        
        self.logger.info(f"Added {len(chunks)} chunks. Total documents: {self.index.ntotal}")
    
    def search(
        self,
        query: str,
        k: int = 5,
        return_scores: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic similarity search
        
        Args:
            query: Search query text
            k: Number of results to return
            return_scores: Whether to include similarity scores
            
        Returns:
            List of retrieved chunks with metadata and scores
        """
        if self.index is None or self.index.ntotal == 0:
            self.logger.warning("No documents in index")
            return []
        
        self.logger.info(f"Searching for: '{query}' (k={k})")
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        
        # Search in FAISS index
        # FAISS returns distances (L2 distance) and indices
        distances, indices = self.index.search(query_embedding.astype('float32'), k)
        
        # Convert L2 distance to similarity score (0-1)
        # Lower L2 distance = higher similarity
        results = []
        for idx, (distance, doc_idx) in enumerate(zip(distances[0], indices[0])):
            if doc_idx == -1:  # FAISS returns -1 for empty results
                continue
            
            # Convert L2 distance to similarity score
            # Using exponential decay: similarity = exp(-distance)
            similarity_score = float(np.exp(-distance))
            
            result = {
                "text": self.documents[doc_idx],
                "metadata": self.metadata[doc_idx],
                "rank": idx + 1
            }
            
            if return_scores:
                result["score"] = similarity_score
                result["distance"] = float(distance)
            
            results.append(result)
        
        self.logger.info(f"Found {len(results)} results")
        return results
    
    def save(self, filename: str = "faiss_index") -> None:
        """
        Save FAISS index and metadata to disk
        
        Args:
            filename: Base filename for saving
        """
        self.logger.info(f"Saving index to {self.persist_directory}")
        
        # Save FAISS index
        index_path = Path(self.persist_directory) / f"{filename}.index"
        faiss.write_index(self.index, str(index_path))
        
        # Save metadata
        metadata_path = Path(self.persist_directory) / f"{filename}_metadata.pkl"
        with open(metadata_path, 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'metadata': self.metadata,
                'model_name': self.model_name,
                'index_type': self.index_type,
                'saved_at': get_timestamp()
            }, f)
        
        self.logger.info("Index and metadata saved successfully")
    
    def load(self, filename: str = "faiss_index") -> None:
        """
        Load FAISS index and metadata from disk
        
        Args:
            filename: Base filename for loading
        """
        self.logger.info(f"Loading index from {self.persist_directory}")
        
        # Load FAISS index
        index_path = Path(self.persist_directory) / f"{filename}.index"
        if not index_path.exists():
            raise FileNotFoundError(f"Index file not found: {index_path}")
        
        self.index = faiss.read_index(str(index_path))
        
        # Load metadata
        metadata_path = Path(self.persist_directory) / f"{filename}_metadata.pkl"
        with open(metadata_path, 'rb') as f:
            data = pickle.load(f)
            self.documents = data['documents']
            self.metadata = data['metadata']
            self.model_name = data['model_name']
            self.index_type = data['index_type']
        
        self.logger.info(f"Loaded index with {self.index.ntotal} documents")
    
    def clear(self) -> None:
        """Clear all documents from the vector store"""
        self.logger.info("Clearing vector store")
        self.index = self.create_index()
        self.documents = []
        self.metadata = []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store
        
        Returns:
            Statistics dictionary
        """
        stats = {
            "total_documents": self.index.ntotal if self.index else 0,
            "model_name": self.model_name,
            "index_type": self.index_type,
            "vector_dimension": self.vector_dimension
        }
        return stats


class HybridSearch(VectorStore):
    """
    Hybrid search combining semantic and keyword search
    Uses both FAISS for semantic search and BM25 for keyword search
    """
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3
    ):
        """
        Initialize hybrid search with weights
        
        Args:
            model_name: Sentence transformer model name
            semantic_weight: Weight for semantic search results
            keyword_weight: Weight for keyword search results
        """
        super().__init__(model_name=model_name)
        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight
        self.logger.info(f"HybridSearch initialized (semantic: {semantic_weight}, keyword: {keyword_weight})")
    
    def keyword_search(
        self,
        query: str,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Simple keyword search using term frequency
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            List of results with keyword scores
        """
        query_terms = query.lower().split()
        results = []
        
        for idx, doc in enumerate(self.documents):
            doc_lower = doc.lower()
            score = 0
            
            # Count term matches
            for term in query_terms:
                score += doc_lower.count(term)
            
            if score > 0:
                results.append({
                    "text": doc,
                    "metadata": self.metadata[idx],
                    "keyword_score": score
                })
        
        # Sort by keyword score and return top-k
        results.sort(key=lambda x: x["keyword_score"], reverse=True)
        return results[:k]
    
    def hybrid_search(
        self,
        query: str,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Combine semantic and keyword search results
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            Combined and re-ranked results
        """
        # Get semantic results
        semantic_results = self.search(query, k=k*2)
        
        # Get keyword results
        keyword_results = self.keyword_search(query, k=k*2)
        
        # Combine and re-rank
        combined_scores = {}
        
        # Add semantic scores
        for result in semantic_results:
            doc_id = result["metadata"].get("document_id", "") + str(result["metadata"].get("chunk_index", ""))
            combined_scores[doc_id] = {
                "result": result,
                "semantic_score": result.get("score", 0),
                "keyword_score": 0
            }
        
        # Add keyword scores
        for result in keyword_results:
            doc_id = result["metadata"].get("document_id", "") + str(result["metadata"].get("chunk_index", ""))
            if doc_id in combined_scores:
                combined_scores[doc_id]["keyword_score"] = result["keyword_score"]
            else:
                combined_scores[doc_id] = {
                    "result": result,
                    "semantic_score": 0,
                    "keyword_score": result["keyword_score"]
                }
        
        # Calculate combined score
        for doc_id, data in combined_scores.items():
            # Normalize scores
            semantic_norm = data["semantic_score"]
            keyword_norm = data["keyword_score"] / max(1, max(r["keyword_score"] for r in keyword_results))
            
            # Weighted combination
            combined_score = (
                self.semantic_weight * semantic_norm +
                self.keyword_weight * keyword_norm
            )
            data["combined_score"] = combined_score
        
        # Sort by combined score
        sorted_results = sorted(
            combined_scores.values(),
            key=lambda x: x["combined_score"],
            reverse=True
        )
        
        # Return top-k
        final_results = []
        for item in sorted_results[:k]:
            result = item["result"].copy()
            result["combined_score"] = item["combined_score"]
            final_results.append(result)
        
        self.logger.info(f"Hybrid search returned {len(final_results)} results")
        return final_results
