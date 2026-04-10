"""
Vector Store for FAISS-based semantic search.

This module provides a singleton vector store that loads the FAISS index
and corpus metadata to perform semantic search over medical documents.
"""

import json
import threading
import logging
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass

import numpy as np
import faiss

from app.core.rag.exceptions import VectorStoreError
from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Result from vector search."""
    doc_id: str
    doc_type: str  # clinical_case, drug_profile, guideline
    content: str
    score: float
    metadata: Dict
    structured: Optional[Dict] = None


class VectorStore:
    """
    FAISS-based vector store for semantic search.

    Singleton that loads the FAISS index and corpus metadata once
    and provides fast similarity search.
    """

    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> 'VectorStore':
        """
        Get singleton instance of VectorStore (thread-safe).

        Returns:
            Singleton VectorStore instance

        Raises:
            VectorStoreError: If index fails to load
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    logger.info("Initializing VectorStore...")
                    cls._instance = cls()
                    logger.info("✓ VectorStore initialized successfully")

        return cls._instance

    def __init__(self):
        """
        Load FAISS index and corpus metadata.

        Raises:
            VectorStoreError: If files cannot be loaded
        """
        if VectorStore._instance is not None:
            raise RuntimeError("Use get_instance() instead of direct instantiation")

        try:
            # Load FAISS index
            index_path = Path(settings.faiss_index_path)
            if not index_path.exists():
                raise VectorStoreError(f"FAISS index not found: {index_path}")

            logger.info(f"Loading FAISS index from {index_path}")
            self.index = faiss.read_index(str(index_path))
            logger.info(f"✓ Loaded FAISS index: {self.index.ntotal} vectors")

            # Load corpus metadata
            corpus_path = Path(settings.corpus_metadata_path)
            if not corpus_path.exists():
                raise VectorStoreError(f"Corpus metadata not found: {corpus_path}")

            logger.info(f"Loading corpus metadata from {corpus_path}")
            with open(corpus_path, 'r', encoding='utf-8') as f:
                self.corpus = json.load(f)
            logger.info(f"✓ Loaded corpus: {len(self.corpus)} documents")

            # Create document ID to index mapping
            self.doc_id_to_idx = {doc['id']: idx for idx, doc in enumerate(self.corpus)}

            # Configure search parameters for IVF indexes
            if hasattr(self.index, 'nprobe'):
                self.index.nprobe = settings.faiss_nprobe
                logger.info(f"Set nprobe={self.index.nprobe} for IVF index (optimized for performance)")

            # Load metadata file for statistics
            metadata_path = index_path.parent / 'metadata.json'
            if metadata_path.exists():
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    self.index_metadata = json.load(f)
            else:
                self.index_metadata = {}

            logger.info("Vector store ready")

        except Exception as e:
            logger.error(f"Failed to load vector store: {e}")
            raise VectorStoreError(f"Failed to load vector store: {e}")

    async def search(
        self,
        query_embedding: np.ndarray,
        k: int = 10,
        filter_types: Optional[List[str]] = None,
        min_score: float = 0.0
    ) -> List[SearchResult]:
        """
        Search for similar documents.

        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            filter_types: Filter by document types (clinical_case, drug_profile, guideline)
            min_score: Minimum similarity score threshold

        Returns:
            List of SearchResult objects

        Raises:
            VectorStoreError: If search fails
        """
        try:
            # Ensure query embedding is 2D array
            if query_embedding.ndim == 1:
                query_embedding = query_embedding.reshape(1, -1)

            # Search FAISS index (returns inner product scores for normalized vectors)
            # Higher scores = more similar
            distances, indices = self.index.search(query_embedding.astype('float32'), k * 3)  # Get more for filtering

            results = []
            for dist, idx in zip(distances[0], indices[0]):
                # Skip invalid indices
                if idx < 0 or idx >= len(self.corpus):
                    continue

                doc = self.corpus[idx]

                # Filter by document type if specified
                if filter_types and doc['type'] not in filter_types:
                    continue

                # Filter by minimum score
                if dist < min_score:
                    continue

                # Create search result
                result = SearchResult(
                    doc_id=doc['id'],
                    doc_type=doc['type'],
                    content=doc['content'],
                    score=float(dist),
                    metadata=doc.get('metadata', {}),
                    structured=doc.get('structured')
                )
                results.append(result)

                # Stop when we have enough results
                if len(results) >= k:
                    break

            logger.debug(f"Search returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise VectorStoreError(f"Search failed: {e}")

    def get_document(self, doc_id: str) -> Optional[Dict]:
        """
        Retrieve document by ID.

        Args:
            doc_id: Document ID

        Returns:
            Document dictionary or None if not found
        """
        idx = self.doc_id_to_idx.get(doc_id)
        if idx is not None and 0 <= idx < len(self.corpus):
            return self.corpus[idx]
        return None

    @property
    def num_documents(self) -> int:
        """Total number of indexed documents."""
        return len(self.corpus)

    @property
    def index_info(self) -> Dict:
        """Index metadata and statistics."""
        return {
            'total_vectors': self.index.ntotal,
            'embedding_dim': self.index.d,
            'index_type': self.index.__class__.__name__,
            'num_documents': len(self.corpus),
            'document_types': self.index_metadata.get('document_types', {}),
            **self.index_metadata
        }

    def __repr__(self) -> str:
        return f"<VectorStore(documents={self.num_documents}, index_type={self.index.__class__.__name__})>"
