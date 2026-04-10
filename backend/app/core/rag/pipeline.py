"""
RAG Pipeline orchestrator.

This module coordinates the entire RAG workflow from patient input
to medication recommendations with evidence citations.
"""

import logging
import time
from typing import List

from app.core.rag.embedder import EmbedderService
from app.core.rag.vectorstore import VectorStore
from app.core.rag.retriever import Retriever
from app.core.rag.generator import LLMClientFactory, LLMResponse
from app.core.rag.prompts import build_medication_recommendation_prompt, extract_json_from_response
from app.core.rag.exceptions import RAGError, ResponseParsingError, LLMError
from app.core.safety.validator import SafetyValidator
from app.ml.predictor import MLPredictor
from app.models.schemas import (
    PatientInput,
    DiagnosisResponse,
    DiseasePrediction,
    MedicationRecommendation,
    Evidence
)
from app.config import settings

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    End-to-end RAG pipeline orchestrator.

    Coordinates retrieval and generation to produce evidence-based
    medication recommendations.
    """

    def __init__(self):
        """Initialize pipeline components."""
        logger.info("Initializing RAG Pipeline...")

        # Initialize components (singletons)
        self.embedder = EmbedderService.get_instance(settings.embedding_model)
        self.vectorstore = VectorStore.get_instance()
        self.retriever = Retriever(self.embedder, self.vectorstore)
        self.llm_client = LLMClientFactory.create(settings.llm_strategy)

        self.ml_predictor = MLPredictor.get_instance()
        self.ml_enabled = False
        try:
            self.ml_predictor.load_models(
                models_path=settings.ml_models_path,
                artifacts_path="./data/ml",
            )
            self.ml_enabled = True
            logger.info("✓ ML predictor enabled")
        except Exception as exc:
            logger.warning("ML predictor unavailable, using retrieval fallback: %s", exc)

        self.safety_validator = SafetyValidator.get_instance()

        logger.info(f"✓ RAG Pipeline initialized with LLM: {self.llm_client.__class__.__name__}")

    async def run(self, patient_input: PatientInput) -> DiagnosisResponse:
        """
        Run full RAG pipeline.

        Args:
            patient_input: Patient information

        Returns:
            DiagnosisResponse with recommendations and evidence

        Raises:
            RAGError: If pipeline fails
        """
        start_time = time.time()

        try:
            logger.info(f"Starting RAG pipeline for patient: age={patient_input.age}, symptoms={len(patient_input.symptoms)}")

            # Step 1: Retrieve relevant evidence
            retrieval_result = await self.retriever.retrieve(patient_input)
            logger.info(f"Retrieved {len(retrieval_result.results)} relevant documents")

            # Step 2: Generate recommendations with LLM
            recommendations = await self._generate_recommendations(
                patient_input,
                retrieval_result.formatted_context
            )
            logger.info(f"Generated {len(recommendations)} recommendations")

            # Step 3: Create evidence objects from retrieval results
            evidence = self._extract_evidence(retrieval_result.results)
            logger.info(f"Extracted {len(evidence)} evidence citations")

            # Step 4: Predictions disabled - using template-only mode for now
            # ML models and LLM APIs disabled due to quota limits
            predictions = []
            logger.info("Predictions disabled - using template-only mode")

            # Step 5: Run Phase 5 safety validation over recommendations
            if settings.safety_enabled:
                recommendations, safety_result = self.safety_validator.validate_recommendations(
                    patient_input=patient_input,
                    recommendations=recommendations,
                )
                logger.info(
                    "Safety validation: safe=%s blocked=%s warnings=%s",
                    safety_result.safe,
                    len(safety_result.blocked_medications),
                    len(safety_result.warnings),
                )
            else:
                logger.info("Safety validation disabled via configuration")

            # Step 6: Create response
            response = DiagnosisResponse(
                diagnosis_id=f"diag_{int(time.time() * 1000)}",  # Temporary ID
                predictions=predictions,
                recommendations=recommendations,
                evidence=evidence
            )

            duration = time.time() - start_time
            logger.info(f"✓ RAG pipeline completed in {duration:.2f}s")

            return response

        except LLMError:
            raise

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"RAG pipeline failed after {duration:.2f}s: {e}")
            raise RAGError(f"RAG pipeline failed: {e}")

    async def _generate_recommendations(
        self,
        patient_input: PatientInput,
        context: str
    ) -> List[MedicationRecommendation]:
        """
        Generate medication recommendations using LLM.

        Args:
            patient_input: Patient information
            context: Formatted retrieval context

        Returns:
            List of MedicationRecommendation objects

        Raises:
            RAGError: If generation fails
        """
        try:
            # Build prompt
            prompt = build_medication_recommendation_prompt(patient_input, context)

            # Generate with LLM
            llm_response: LLMResponse = await self.llm_client.generate(
                prompt=prompt,
                max_tokens=settings.openai_max_tokens,
                temperature=settings.llm_temperature
            )
            logger.info("LLM response model: %s", llm_response.model_name or "unknown")

            if llm_response.model_name == "template_fallback" and not settings.allow_template_fallback:
                logger.error("Template fallback response blocked by configuration")
                raise LLMError(
                    "Template fallback response blocked (ALLOW_TEMPLATE_FALLBACK=false)."
                )

            # Parse response
            if llm_response.parsed_json:
                response_dict = llm_response.parsed_json
            else:
                try:
                    response_dict = extract_json_from_response(llm_response.text)
                except Exception as e:
                    logger.error(f"Failed to parse LLM response: {e}")
                    raise ResponseParsingError(f"Failed to parse LLM response: {e}")

            # Extract recommendations
            recommendations = []
            rec_list = response_dict.get('recommendations', [])

            for rec in rec_list:
                # Build dosage string
                dosage_str = f"{rec.get('dosage', 'as directed')}"
                if rec.get('frequency'):
                    dosage_str += f" {rec['frequency']}"

                # Create recommendation object
                recommendation = MedicationRecommendation(
                    name=rec.get('name', 'Unknown'),
                    dosage=dosage_str,
                    duration=rec.get('duration', 'consult physician'),
                    evidence=rec.get('evidence_ids', []),
                    safety_status="safe",  # Placeholder - will be determined by safety layer
                    warnings=[]
                )
                recommendations.append(recommendation)

            # Add global warnings if any
            if response_dict.get('warnings'):
                # Add warnings to first recommendation for now
                if recommendations:
                    recommendations[0].warnings.extend(response_dict['warnings'])

            uses_template_evidence = any(
                "template_based" in (rec.get("evidence_ids") or [])
                for rec in rec_list
                if isinstance(rec, dict)
            )
            if uses_template_evidence:
                if not settings.allow_template_fallback:
                    logger.error("Template-based evidence blocked by configuration")
                    raise LLMError(
                        "Template-based recommendation payload blocked (ALLOW_TEMPLATE_FALLBACK=false)."
                    )
                logger.warning(
                    "Template-based recommendation evidence detected in generated response"
                )

            return recommendations

        except LLMError:
            raise

        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            raise RAGError(f"Failed to generate recommendations: {e}")

    def _extract_evidence(self, search_results) -> List[Evidence]:
        """
        Extract evidence citations from search results.

        Args:
            search_results: List of SearchResult objects

        Returns:
            List of Evidence objects
        """
        evidence = []

        for result in search_results[:10]:  # Limit to top 10
            evidence_obj = Evidence(
                source=result.doc_id,
                type=result.doc_type,
                text=result.content[:500] if len(result.content) > 500 else result.content,
                relevance_score=result.score
            )
            evidence.append(evidence_obj)

        return evidence

    def _create_placeholder_predictions(self, search_results) -> List[DiseasePrediction]:
        """
        Create placeholder disease predictions.

        This will be replaced with actual ML model predictions in Phase 4.

        Args:
            search_results: List of SearchResult objects

        Returns:
            List of DiseasePrediction objects
        """
        predictions = []

        # Extract potential diseases from clinical cases
        clinical_cases = [r for r in search_results if r.doc_type == 'clinical_case']

        for i, case in enumerate(clinical_cases[:3], 1):
            # Try to extract diagnosis from structured data
            disease_name = "Unknown"
            if case.structured and 'diagnoses' in case.structured:
                diagnoses = case.structured['diagnoses']
                if diagnoses and len(diagnoses) > 0:
                    disease_name = diagnoses[0]

            # Create prediction
            prediction = DiseasePrediction(
                disease=disease_name,
                confidence=case.score * 0.8,  # Scale score to confidence
                source="rag_retrieval",
                explanation=f"Based on similar clinical case: {case.doc_id}"
            )
            predictions.append(prediction)

        # If no predictions, add a generic one
        if not predictions:
            predictions.append(DiseasePrediction(
                disease="Undetermined",
                confidence=0.5,
                source="rag_retrieval",
                explanation="Insufficient evidence for specific diagnosis"
            ))

        return predictions

    def __repr__(self) -> str:
        return f"<RAGPipeline(llm={self.llm_client.__class__.__name__}, vectorstore={self.vectorstore.num_documents} docs)>"
