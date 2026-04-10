"""
Retriever for high-level document retrieval.

This module provides a high-level interface for retrieving relevant documents
from the vector store, including query building, MMR for diversity, and
context formatting for LLM prompts.
"""

import logging
from typing import List
from dataclasses import dataclass
import numpy as np

from app.core.rag.embedder import EmbedderService
from app.core.rag.vectorstore import VectorStore, SearchResult
from app.core.rag.exceptions import RetrievalError
from app.models.schemas import PatientInput, SymptomInput
from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """Result from retrieval process."""
    query: str
    results: List[SearchResult]
    formatted_context: str
    metadata: dict


class Retriever:
    """
    High-level retrieval interface.

    Handles query building from patient input, document retrieval,
    MMR for diversity, and context formatting.
    """

    def __init__(
        self,
        embedder: EmbedderService = None,
        vectorstore: VectorStore = None,
        top_k: int = None,
        min_score: float = None,
        use_mmr: bool = None,
        mmr_lambda: float = None
    ):
        """
        Initialize retriever.

        Args:
            embedder: Embedder service (defaults to singleton)
            vectorstore: Vector store (defaults to singleton)
            top_k: Number of results to retrieve
            min_score: Minimum similarity score
            use_mmr: Whether to use MMR for diversity
            mmr_lambda: MMR diversity parameter (0=diversity, 1=relevance)
        """
        self.embedder = embedder or EmbedderService.get_instance(settings.embedding_model)
        self.vectorstore = vectorstore or VectorStore.get_instance()
        self.top_k = top_k or settings.retrieval_top_k
        self.min_score = min_score or settings.retrieval_min_score
        self.use_mmr = use_mmr if use_mmr is not None else settings.retrieval_use_mmr
        self.mmr_lambda = mmr_lambda or settings.mmr_diversity_lambda

    async def retrieve(
        self,
        patient_input: PatientInput,
        top_k: int = None,
        use_mmr: bool = None
    ) -> RetrievalResult:
        """
        Main retrieval method.

        Args:
            patient_input: Patient information
            top_k: Override default top_k
            use_mmr: Override default use_mmr

        Returns:
            RetrievalResult with query, results, and formatted context

        Raises:
            RetrievalError: If retrieval fails
        """
        try:
            # Build query from patient input
            query = self._build_query(patient_input)
            logger.info(f"Built query: {query[:100]}...")

            # Encode query
            query_embedding = await self.embedder.encode_query(query)

            # Retrieve documents
            k = top_k or self.top_k
            results = await self.vectorstore.search(
                query_embedding=query_embedding,
                k=k * 2 if (use_mmr or self.use_mmr) else k,  # Get more for MMR
                min_score=self.min_score
            )

            logger.info(f"Retrieved {len(results)} initial results")

            # Apply MMR for diversity if enabled
            if (use_mmr or self.use_mmr) and len(results) > k:
                results = self._apply_mmr(results, query_embedding, k)
                logger.info(f"Applied MMR, kept {len(results)} diverse results")

            # Format context for LLM
            formatted_context = self._format_context(results)

            return RetrievalResult(
                query=query,
                results=results,
                formatted_context=formatted_context,
                metadata={
                    'num_results': len(results),
                    'query_length': len(query),
                    'top_k': k,
                    'mmr_applied': use_mmr or self.use_mmr
                }
            )

        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            raise RetrievalError(f"Retrieval failed: {e}")

    def _build_query(self, patient_input: PatientInput) -> str:
        """
        Convert patient input to search query.

        Args:
            patient_input: Patient information

        Returns:
            Query string
        """
        parts = []

        # Age and gender
        parts.append(f"{patient_input.age} year old {patient_input.gender} patient")

        # Symptoms
        if patient_input.symptoms:
            symptom_strs = []
            for symptom in patient_input.symptoms:
                symptom_str = f"{symptom.name}"
                if symptom.severity:
                    symptom_str += f" (severity {symptom.severity}/10)"
                if symptom.duration_days:
                    symptom_str += f" for {symptom.duration_days} days"
                symptom_strs.append(symptom_str)
            parts.append(f"with symptoms: {', '.join(symptom_strs)}")

        # Chronic conditions
        if patient_input.chronic_conditions:
            parts.append(f"Chronic conditions: {', '.join(patient_input.chronic_conditions)}")

        # Current medications
        if patient_input.current_medications:
            parts.append(f"Currently taking: {', '.join(patient_input.current_medications)}")

        # Allergies
        if patient_input.allergies:
            parts.append(f"Allergies: {', '.join(patient_input.allergies)}")

        return ". ".join(parts) + "."

    def _apply_mmr(
        self,
        results: List[SearchResult],
        query_embedding: np.ndarray,
        k: int
    ) -> List[SearchResult]:
        """
        Apply Maximal Marginal Relevance for diversity.

        MMR balances relevance and diversity by selecting documents that are
        relevant to the query but dissimilar to already selected documents.

        Args:
            results: Initial search results
            query_embedding: Query embedding vector
            k: Number of results to keep

        Returns:
            Diverse subset of results
        """
        if len(results) <= k:
            return results

        # Get embeddings for all result documents
        result_texts = [r.content for r in results]
        # For simplicity, we'll use the scores as a proxy for similarity
        # In a full implementation, we'd re-embed documents

        selected = []
        remaining = list(results)

        # Select first result (highest relevance)
        selected.append(remaining.pop(0))

        while len(selected) < k and remaining:
            best_score = -float('inf')
            best_idx = 0

            for idx, candidate in enumerate(remaining):
                # Relevance to query
                relevance = candidate.score

                # Diversity from selected (max similarity to any selected)
                if selected:
                    # Simple diversity: penalize if very similar to already selected
                    diversity_penalty = 0
                    for sel in selected:
                        if sel.doc_type == candidate.doc_type:
                            diversity_penalty += 0.1  # Same type penalty
                        if sel.doc_id == candidate.doc_id:
                            diversity_penalty = 999  # Duplicate
                    diversity = 1.0 - diversity_penalty
                else:
                    diversity = 1.0

                # MMR score
                mmr_score = self.mmr_lambda * relevance + (1 - self.mmr_lambda) * diversity

                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = idx

            selected.append(remaining.pop(best_idx))

        return selected

    def _format_context(self, results: List[SearchResult]) -> str:
        """
        Format retrieved documents for LLM context.

        Groups documents by type and formats them with clear structure.

        Args:
            results: Search results

        Returns:
            Formatted context string
        """
        if not results:
            return "No relevant medical information found."

        # Group by document type
        by_type = {
            'clinical_case': [],
            'drug_profile': [],
            'clinical_guideline': []
        }

        for result in results:
            doc_type = result.doc_type
            if doc_type in by_type:
                by_type[doc_type].append(result)

        context_parts = []

        # Format clinical cases
        if by_type['clinical_case']:
            context_parts.append("=== SIMILAR CLINICAL CASES ===\n")
            for i, result in enumerate(by_type['clinical_case'][:3], 1):
                context_parts.append(f"[Case {i}] {result.doc_id} (Relevance: {result.score:.2f})")
                context_parts.append(f"{result.content[:500]}...\n")

        # Format drug profiles
        if by_type['drug_profile']:
            context_parts.append("\n=== DRUG INFORMATION ===\n")
            for i, result in enumerate(by_type['drug_profile'][:5], 1):
                context_parts.append(f"[Drug {i}] {result.doc_id} (Relevance: {result.score:.2f})")
                # Extract drug name if available
                if result.structured and 'name' in result.structured:
                    context_parts.append(f"Name: {result.structured['name']}")
                context_parts.append(f"{result.content[:300]}...\n")

        # Format guidelines
        if by_type['clinical_guideline']:
            context_parts.append("\n=== CLINICAL GUIDELINES ===\n")
            for i, result in enumerate(by_type['clinical_guideline'][:2], 1):
                context_parts.append(f"[Guideline {i}] {result.doc_id} (Relevance: {result.score:.2f})")
                context_parts.append(f"{result.content[:400]}...\n")

        return "\n".join(context_parts)

    def __repr__(self) -> str:
        return f"<Retriever(top_k={self.top_k}, mmr={self.use_mmr})>"
