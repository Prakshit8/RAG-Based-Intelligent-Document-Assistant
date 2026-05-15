# RAG Interview Questions and Answers

Comprehensive interview questions and answers for RAG (Retrieval-Augmented Generation) systems.

## Basic Concepts

### Q1: What is RAG?

**Answer**: RAG (Retrieval-Augmented Generation) is an AI framework that enhances large language models by retrieving relevant information from external knowledge bases before generating responses. It combines:
- **Retrieval**: Finding relevant documents/chunks from a knowledge base
- **Augmentation**: Using retrieved information as context for the LLM
- **Generation**: Producing responses grounded in the retrieved context

**Key Benefits**:
- Reduces hallucinations by grounding responses
- Provides up-to-date information without retraining
- Offers transparency through source citations
- Enables domain-specific applications

### Q2: How does RAG differ from fine-tuning?

**Answer**:

| Aspect | RAG | Fine-Tuning |
|--------|-----|-------------|
| Knowledge Source | External documents | Model weights |
| Update Speed | Instant (add documents) | Slow (retrain model) |
| Cost | Lower | Higher |
| Transparency | High (source citations) | Low (black box) |
| Use Case | Dynamic knowledge | Static knowledge |
| Hallucination Risk | Lower | Higher |

### Q3: What are the main components of a RAG system?

**Answer**:
1. **Document Processor**: Extracts and cleans text from documents
2. **Text Splitter**: Divides documents into chunks
3. **Embedding Model**: Converts text to vector representations
4. **Vector Store**: Stores and searches embeddings efficiently
5. **Retriever**: Finds relevant chunks for queries
6. **LLM**: Generates answers using retrieved context
7. **Orchestrator**: Manages the entire pipeline

## Technical Implementation

### Q4: Why use RecursiveCharacterTextSplitter?

**Answer**: RecursiveCharacterTextSplitter is preferred because:

1. **Semantic Preservation**: Attempts to split on larger separators first (paragraphs, sentences)
2. **Context Continuity**: Falls back to smaller separators only when necessary
3. **Reduced Fragmentation**: Minimizes cutting sentences mid-word
4. **Flexibility**: Adapts to different document structures
5. **Better Retrieval**: Maintains semantic meaning within chunks

**Example**:
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""]
)
```

### Q5: What is chunk overlap and why is it important?

**Answer**: Chunk overlap is the number of characters shared between adjacent chunks.

**Importance**:
- **Context Preservation**: Ensures important information isn't split between chunks
- **Better Retrieval**: Increases chance of capturing relevant context
- **Continuity**: Maintains semantic flow across boundaries
- **Edge Cases**: Handles concepts that span chunk boundaries

**Typical Values**:
- Chunk size: 1000-2000 characters
- Overlap: 10-20% of chunk size (100-400 characters)

### Q6: Why is FAISS fast for vector similarity search?

**Answer**: FAISS (Facebook AI Similarity Search) is fast because:

1. **Optimized Indexing Structures**:
   - **Flat Index**: Exact search, O(n) complexity
   - **IVF (Inverted File)**: Approximate search, O(√n) complexity
   - **HNSW (Hierarchical Navigable Small World)**: Fast approximate search

2. **GPU Acceleration**: Supports CUDA for faster operations

3. **Memory Efficiency**: Compact storage and retrieval algorithms

4. **Approximate Search**: Trades slight accuracy for massive speed improvements

5. **Quantization**: Reduces memory usage with minimal accuracy loss

**Example**:
```python
import faiss

# Create HNSW index for fast search
index = faiss.IndexHNSWFlat(dimension=384, M=16)
```

### Q7: What's the difference between semantic search and keyword search?

**Answer**:

| Aspect | Semantic Search | Keyword Search |
|--------|----------------|----------------|
| **Matching** | Vector similarity (meaning) | Exact term matching |
| **Understanding** | Context and intent | Literal words |
| **Flexibility** | Handles synonyms/paraphrases | Requires exact terms |
| **Example** | "automobile" matches "car" | "car" only matches "car" |
| **Technology** | Embeddings + Vector Search | BM25, TF-IDF |
| **Use Case** | Concept-based queries | Specific term queries |

**Hybrid Approach**: Combining both often yields best results:
```python
# Semantic: 70% weight
# Keyword: 30% weight
final_score = 0.7 * semantic_score + 0.3 * keyword_score
```

### Q8: How does RAG reduce hallucinations?

**Answer**: RAG reduces hallucinations through:

1. **Grounding**: LLM instructed to use ONLY provided context
2. **Source Citations**: Every answer includes source references
3. **Low Temperature**: Reduces creative/incorrect responses
4. **Explicit Instructions**: Clear directives to not use outside knowledge
5. **Context Limitation**: Model cannot access training data for answers
6. **Verification**: Users can verify answers against sources

**Prompt Engineering Example**:
```
Answer using ONLY the provided context. If information is not available,
say "I cannot find this information in the provided documents."
Do not make up information or use outside knowledge.
```

## Advanced Topics

### Q9: What are common RAG evaluation metrics?

**Answer**:

**Retrieval Metrics**:
- **Precision@k**: Percentage of retrieved chunks that are relevant
- **Recall@k**: Percentage of relevant chunks that were retrieved
- **MRR (Mean Reciprocal Rank)**: Average of reciprocal ranks of first relevant result
- **NDCG (Normalized Discounted Cumulative Gain)**: Ranking quality metric

**Generation Metrics**:
- **Faithfulness**: Does the answer match the retrieved context?
- **Answer Relevance**: Is the answer relevant to the question?
- **Context Precision**: Is the retrieved context relevant?
- **Context Recall**: Did we retrieve all necessary context?

**Example**:
```python
def calculate_precision_at_k(retrieved, relevant, k):
    relevant_retrieved = sum(1 for doc in retrieved[:k] if doc in relevant)
    return relevant_retrieved / k
```

### Q10: What is re-ranking in RAG?

**Answer**: Re-ranking is the process of improving retrieval results by:

1. **Initial Retrieval**: Get top-k results using vector similarity
2. **Re-ranking**: Use LLM or cross-encoder to re-score results
3. **Final Selection**: Select top results based on re-ranked scores

**Benefits**:
- Better relevance for complex queries
- Handles semantic nuances better
- Improves precision

**Implementation**:
```python
# Initial retrieval
results = vector_store.search(query, k=20)

# Re-rank using LLM
reranked = llm_service.re_rank_results(query, results, top_k=5)
```

### Q11: What are common challenges in RAG systems?

**Answer**:

**1. Chunking Strategy**:
- Too small: Insufficient context
- Too large: Noisy, less precise
- Solution: Tune chunk size and overlap

**2. Embedding Quality**:
- Poor embeddings = poor retrieval
- Solution: Use domain-specific models

**3. Vector Store Scaling**:
- Large datasets = slow search
- Solution: Use approximate indexes (HNSW, IVF)

**4. Context Window Limits**:
- Too many chunks exceed LLM context
- Solution: Limit retrieval, use compression

**5. Hallucination**:
- LLM still can hallucinate
- Solution: Strict prompting, verification

**6. Evaluation**:
- Hard to measure quality
- Solution: Use multiple metrics, human evaluation

### Q12: How do you handle multi-document queries?

**Answer**:

**Strategies**:

1. **Global Index**: All documents in single vector store
   - Simple, fast
   - May mix unrelated content

2. **Per-Document Index**: Separate index per document
   - Better context isolation
   - More complex to manage

3. **Metadata Filtering**: Tag chunks with document ID
   - Filter by document before search
   - Best of both worlds

**Implementation**:
```python
# Add document metadata
chunk["metadata"]["document_id"] = doc_id
chunk["metadata"]["source"] = filename

# Filter during retrieval
results = vector_store.search(query, filter={"document_id": doc_id})
```

### Q13: What is hybrid search?

**Answer**: Hybrid search combines semantic and keyword search:

**Components**:
- **Semantic Search**: Vector similarity for meaning
- **Keyword Search**: BM25 for exact term matching
- **Score Fusion**: Combine scores with weights

**Benefits**:
- Handles both conceptual and specific queries
- Better for technical terms, acronyms
- More robust to different query types

**Implementation**:
```python
semantic_score = vector_store.search(query)
keyword_score = bm25_search(query)

# Weighted combination
final_score = 0.7 * semantic_score + 0.3 * keyword_score
```

## System Design

### Q14: Design a scalable RAG architecture

**Answer**:

**Components**:

1. **API Gateway**: Handle requests, rate limiting
2. **Document Service**: Process and store documents
3. **Embedding Service**: Generate embeddings asynchronously
4. **Vector Store**: Distributed FAISS cluster
5. **Retrieval Service**: Fast similarity search
6. **LLM Service**: Generate answers with streaming
7. **Cache Layer**: Redis for frequent queries
8. **Database**: PostgreSQL for metadata
9. **Message Queue**: Kafka for async processing

**Scalability**:
- Horizontal scaling for microservices
- Load balancing for high traffic
- CDN for static assets
- Database sharding for large datasets

### Q15: How do you handle real-time document updates?

**Answer**:

**Strategies**:

1. **Incremental Updates**:
   - Process only changed documents
   - Update vector store incrementally
   - Maintain versioning

2. **Background Processing**:
   - Queue updates in message broker
   - Process asynchronously
   - Notify when complete

3. **Version Control**:
   - Track document versions
   - Support rollbacks
   - Maintain history

**Implementation**:
```python
# Detect changes
if document_hash != stored_hash:
    # Queue for processing
    queue.enqueue(process_document, document_id)
    
# Update vector store
vector_store.delete(document_id)
vector_store.add(new_chunks)
```

## Practical Implementation

### Q16: How do you optimize RAG for production?

**Answer**:

**Performance**:
- Use approximate indexes (HNSW)
- Enable caching for frequent queries
- Implement request batching
- Use streaming for responses

**Reliability**:
- Add retry logic for API calls
- Implement circuit breakers
- Monitor and alert on errors
- Backup vector stores regularly

**Cost**:
- Use efficient embedding models
- Implement request throttling
- Cache embeddings
- Use spot instances for batch processing

**Security**:
- Encrypt sensitive data
- Implement authentication
- Rate limit API calls
- Audit access logs

### Q17: How do you evaluate RAG system quality?

**Answer**:

**Automated Metrics**:
- Retrieval: Precision@k, Recall@k, MRR
- Generation: Faithfulness, Relevance
- Latency: Response time, throughput
- Cost: Token usage, API costs

**Human Evaluation**:
- Answer quality rating
- Source relevance
- User satisfaction surveys
- A/B testing

**Monitoring**:
- Track metrics over time
- Set up alerts for degradation
- Regular quality audits
- Continuous improvement

### Q18: What are best practices for RAG prompt engineering?

**Answer**:

**Best Practices**:

1. **Clear Instructions**:
   ```
   Answer using ONLY the provided context.
   If information is not available, state that clearly.
   ```

2. **Context Formatting**:
   ```
   Context:
   [Source: doc1.pdf, Page 3]
   [Content]
   ```

3. **Few-Shot Examples**:
   ```
   Example:
   Q: What is X?
   A: According to the context, X is...
   ```

4. **Chain of Thought**:
   ```
   Think step by step:
   1. Identify relevant information
   2. Synthesize the answer
   3. Cite sources
   ```

5. **Temperature Control**:
   - Use low temperature (0.1-0.3) for factual answers
   - Higher temperature (0.5-0.7) for creative tasks

## Scenario-Based Questions

### Q19: A user uploads a 1000-page PDF. How do you handle it?

**Answer**:

**Strategy**:
1. **Chunking**: Split into manageable chunks (1000 chars)
2. **Async Processing**: Process in background to avoid timeout
3. **Progress Tracking**: Show progress to user
4. **Memory Management**: Process in batches
5. **Error Handling**: Handle corrupted pages gracefully

**Implementation**:
```python
# Process in batches
for i in range(0, len(pages), batch_size):
    batch = pages[i:i+batch_size]
    chunks = process_batch(batch)
    vector_store.add(chunks)
    update_progress(i / len(pages))
```

### Q20: How do you handle queries about information not in documents?

**Answer**:

**Strategy**:
1. **Clear Instructions**: Tell LLM to say "not found"
2. **Confidence Scoring**: Check retrieval confidence
3. **Fallback**: Offer to search web if appropriate
4. **User Feedback**: Ask user to upload relevant documents

**Prompt**:
```
If the answer is not in the provided context, say:
"I cannot find this information in the provided documents.
Please upload relevant documents or rephrase your question."
```

---

These questions cover the essential aspects of RAG systems from basic concepts to advanced implementation and production considerations.
