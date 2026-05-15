"""
LLM Service Module
Handles integration with Groq/OpenAI API for answer generation
"""

import os
from typing import List, Dict, Any, Optional, Generator
from dataclasses import dataclass
import logging
import time

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from utils import setup_logger, validate_api_key, calculate_token_count


@dataclass
class LLMConfig:
    """Configuration for LLM service"""
    api_key: str
    model: str = "llama3-8b-8192"  # Default Groq model
    temperature: float = 0.1  # Low temperature for factual answers
    max_tokens: int = 1024
    provider: str = "groq"  # 'groq' or 'openai'
    streaming: bool = True


class LLMService:
    """
    Service for generating answers using LLM with retrieved context
    
    How RAG reduces hallucinations:
    - Grounds answers in retrieved document chunks
    - Provides explicit source citations
    - Instructs model to only use provided context
    - Low temperature reduces creative/incorrect responses
    """
    
    def __init__(self, config: LLMConfig):
        """
        Initialize LLM service with configuration
        
        Args:
            config: LLMConfig object with API settings
        """
        self.logger = setup_logger("llm_service")
        self.config = config
        self.client = None
        
        # Validate API key
        if not validate_api_key(config.api_key):
            raise ValueError("Invalid API key provided")
        
        # Initialize client based on provider
        if config.provider == "groq":
            if not GROQ_AVAILABLE:
                raise ImportError("Groq library not installed. Install with: pip install groq")
            self.client = Groq(api_key=config.api_key)
            self.logger.info(f"Initialized Groq client with model: {config.model}")
            
        elif config.provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI library not installed. Install with: pip install openai")
            self.client = OpenAI(api_key=config.api_key)
            self.logger.info(f"Initialized OpenAI client with model: {config.model}")
            
        else:
            raise ValueError(f"Unknown provider: {config.provider}")
    
    def _build_prompt(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Build prompt with retrieved context and conversation history
        
        Args:
            query: User question
            context_chunks: Retrieved document chunks
            conversation_history: Previous conversation messages
            
        Returns:
            Formatted prompt string
        """
        # Combine context chunks
        context_text = "\n\n---\n\n".join([
            f"Source: {chunk['metadata'].get('source', 'Unknown')} (Page {chunk['metadata'].get('page', 'N/A')})\n{chunk['text']}"
            for chunk in context_chunks
        ])
        
        # Build conversation history context
        history_context = ""
        if conversation_history:
            history_context = "\n\nPrevious conversation:\n"
            for msg in conversation_history[-3:]:  # Last 3 messages
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                history_context += f"{role.capitalize()}: {content}\n"
        
        # Build main prompt
        prompt = f"""You are an intelligent document assistant. Answer questions based ONLY on the provided context from documents.

Context from documents:
{context_text}

{history_context}

User Question: {query}

Instructions:
1. Answer the question using ONLY the information provided in the context above.
2. If the answer is not in the context, say "I cannot find this information in the provided documents."
3. Be specific and cite the sources used in your answer.
4. Do not make up information or use outside knowledge.
5. Provide a clear, concise answer.
6. If multiple sources provide relevant information, synthesize them.

Answer:"""
        
        return prompt
    
    def generate_answer(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        conversation_history: List[Dict[str, str]] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Generate answer using LLM with retrieved context
        
        Args:
            query: User question
            context_chunks: Retrieved document chunks
            conversation_history: Previous conversation messages
            max_retries: Maximum number of retry attempts for API failures
            
        Returns:
            Dictionary with answer and metadata
        """
        self.logger.info(f"Generating answer for query: {query[:50]}...")
        
        # Build prompt
        prompt = self._build_prompt(query, context_chunks, conversation_history)
        
        # Retry logic with exponential backoff
        for attempt in range(max_retries):
            try:
                # Generate response
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful document assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens
                )
                
                answer = response.choices[0].message.content
                
                # Calculate token usage
                prompt_tokens = calculate_token_count(prompt)
                completion_tokens = calculate_token_count(answer)
                
                result = {
                    "answer": answer,
                    "sources": [chunk["metadata"] for chunk in context_chunks],
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                    "model": self.config.model
                }
                
                self.logger.info(f"Generated answer with {completion_tokens} tokens")
                return result
                
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    # Exponential backoff: 2^attempt seconds
                    wait_time = 2 ** attempt
                    self.logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Error generating answer after {max_retries} attempts: {e}")
                    raise
    
    def generate_answer_stream(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        conversation_history: List[Dict[str, str]] = None
    ) -> Generator[str, None, None]:
        """
        Generate streaming answer using LLM
        
        Args:
            query: User question
            context_chunks: Retrieved document chunks
            conversation_history: Previous conversation messages
            
        Yields:
            Streaming text chunks
        """
        self.logger.info(f"Generating streaming answer for query: {query[:50]}...")
        
        # Build prompt
        prompt = self._build_prompt(query, context_chunks, conversation_history)
        
        try:
            # Generate streaming response
            stream = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "You are a helpful document assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            self.logger.error(f"Error in streaming generation: {e}")
            raise
    
    def re_rank_results(
        self,
        query: str,
        results: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Re-rank search results using LLM for better relevance
        
        Args:
            query: User query
            results: Initial search results
            top_k: Number of top results to return
            
        Returns:
            Re-ranked results
        """
        self.logger.info(f"Re-ranking {len(results)} results")
        
        # Build re-ranking prompt
        results_text = "\n\n".join([
            f"Result {i+1}: {result['text'][:200]}..."
            for i, result in enumerate(results)
        ])
        
        prompt = f"""Given the query: "{query}"

Rank the following results by relevance (1 = most relevant, {len(results)} = least relevant):

{results_text}

Return only the ranking numbers in order, separated by commas."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=100
            )
            
            # Parse ranking
            ranking_str = response.choices[0].message.content.strip()
            rankings = [int(x.strip()) for x in ranking_str.split(',')]
            
            # Re-rank results
            ranked_results = [results[i-1] for i in rankings]
            
            self.logger.info(f"Re-ranking complete, returning top {top_k}")
            return ranked_results[:top_k]
            
        except Exception as e:
            self.logger.error(f"Error in re-ranking: {e}")
            # Return original results if re-ranking fails
            return results[:top_k]
