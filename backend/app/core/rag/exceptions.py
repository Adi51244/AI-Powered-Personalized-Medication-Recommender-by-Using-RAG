"""
Custom exceptions for RAG pipeline.

This module defines the exception hierarchy for all RAG-related errors,
providing clear error types for different failure scenarios.
"""


class RAGError(Exception):
    """Base exception for all RAG pipeline errors."""
    pass


class EmbedderError(RAGError):
    """Raised when embedding model fails to load or encode text."""
    pass


class VectorStoreError(RAGError):
    """Raised when FAISS index fails to load or search."""
    pass


class RetrievalError(RAGError):
    """Raised when retrieval process fails."""
    pass


class LLMError(RAGError):
    """Raised when LLM generation fails."""
    pass


class PromptError(RAGError):
    """Raised when prompt building fails."""
    pass


class ResponseParsingError(RAGError):
    """Raised when LLM response cannot be parsed."""
    pass
