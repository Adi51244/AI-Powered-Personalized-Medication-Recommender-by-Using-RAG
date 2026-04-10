"""
Embedder Service for text embeddings using SentenceTransformers.

This module provides a singleton service for creating text embeddings
using the SentenceTransformer model. The singleton pattern ensures
the model is loaded only once and shared across requests.
"""

import threading
import logging
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.rag.exceptions import EmbedderError

logger = logging.getLogger(__name__)


class EmbedderService:
    """
    Singleton service for text embeddings.

    Uses SentenceTransformer to create embeddings for queries and documents.
    The singleton pattern ensures efficient resource usage by loading the model once.
    """

    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> 'EmbedderService':
        """
        Get singleton instance of EmbedderService (thread-safe).

        Args:
            model_name: SentenceTransformer model name

        Returns:
            Singleton EmbedderService instance
        """
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking pattern
                if cls._instance is None:
                    logger.info(f"Initializing EmbedderService with model: {model_name}")
                    cls._instance = cls(model_name)
                    logger.info("✓ EmbedderService initialized successfully")

        return cls._instance

    def __init__(self, model_name: str):
        """
        Initialize SentenceTransformer model.

        Args:
            model_name: Name of the SentenceTransformer model

        Raises:
            EmbedderError: If model fails to load
        """
        if EmbedderService._instance is not None:
            raise RuntimeError("Use get_instance() instead of direct instantiation")

        try:
            self.model_name = model_name
            self.model = SentenceTransformer(model_name)
            self._embedding_dim = self.model.get_sentence_embedding_dimension()

            logger.info(f"Loaded embedding model: {model_name}")
            logger.info(f"Embedding dimension: {self._embedding_dim}")

        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise EmbedderError(f"Failed to load embedding model '{model_name}': {e}")

    async def encode_query(self, query: str) -> np.ndarray:
        """
        Encode a single query string to embedding vector.

        Args:
            query: Query text to encode

        Returns:
            Normalized embedding vector

        Raises:
            EmbedderError: If encoding fails
        """
        try:
            if not query or not query.strip():
                raise EmbedderError("Query cannot be empty")

            # Encode with normalization (for cosine similarity)
            embedding = self.model.encode(
                query,
                normalize_embeddings=True,
                show_progress_bar=False
            )

            return embedding

        except Exception as e:
            logger.error(f"Failed to encode query: {e}")
            raise EmbedderError(f"Failed to encode query: {e}")

    async def encode_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Encode multiple texts in batch.

        Args:
            texts: List of texts to encode
            batch_size: Batch size for encoding

        Returns:
            Array of normalized embedding vectors

        Raises:
            EmbedderError: If encoding fails
        """
        try:
            if not texts:
                raise EmbedderError("Text list cannot be empty")

            # Filter out empty strings
            valid_texts = [t for t in texts if t and t.strip()]
            if not valid_texts:
                raise EmbedderError("No valid text to encode")

            # Batch encode with normalization
            embeddings = self.model.encode(
                valid_texts,
                batch_size=batch_size,
                normalize_embeddings=True,
                show_progress_bar=False
            )

            return embeddings

        except Exception as e:
            logger.error(f"Failed to encode batch: {e}")
            raise EmbedderError(f"Failed to encode batch: {e}")

    @property
    def embedding_dim(self) -> int:
        """Get embedding dimension."""
        return self._embedding_dim

    def __repr__(self) -> str:
        return f"<EmbedderService(model={self.model_name}, dim={self._embedding_dim})>"
