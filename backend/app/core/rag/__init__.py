"""
RAG (Retrieval-Augmented Generation) pipeline components.

This package provides the core RAG functionality for MediRAG including:
- Text embeddings
- Vector store search
- Document retrieval
- LLM generation
- End-to-end pipeline orchestration
"""

from app.core.rag.exceptions import (
    RAGError,
    EmbedderError,
    VectorStoreError,
    RetrievalError,
    LLMError,
    PromptError,
    ResponseParsingError
)
from app.core.rag.embedder import EmbedderService

__all__ = [
    "RAGError",
    "EmbedderError",
    "VectorStoreError",
    "RetrievalError",
    "LLMError",
    "PromptError",
    "ResponseParsingError",
    "EmbedderService",
]
