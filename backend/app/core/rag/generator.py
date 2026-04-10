"""
LLM Client implementations with strategy pattern.

This module provides flexible LLM integration with multiple implementations:
- OpenAI API client
- Local LLM client (future)
- Template-based fallback (no LLM required)
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict
from dataclasses import dataclass

from app.core.rag.exceptions import LLMError, ResponseParsingError
from app.core.rag.prompts import extract_json_from_response, build_template_response
from app.config import settings
from app.models.schemas import PatientInput

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Response from LLM generation."""
    text: str
    parsed_json: Optional[Dict] = None
    model_name: str = ""
    tokens_used: int = 0
    error: Optional[str] = None


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.3
    ) -> LLMResponse:
        """
        Generate response from prompt.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            LLMResponse with generated text

        Raises:
            LLMError: If generation fails
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if LLM is available."""
        pass


class TemplateLLMClient(BaseLLMClient):
    """
    Template-based fallback LLM (no actual LLM).

    Provides a safe fallback by extracting medication names
    from retrieved DrugBank documents and formatting them
    as recommendations.
    """

    def __init__(self):
        """Initialize template client."""
        self.model_name = "template_fallback"
        logger.info("Initialized TemplateLLMClient (fallback mode)")

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.3
    ) -> LLMResponse:
        """
        Generate template-based response.

        Extracts context and patient info from prompt and builds
        a response tailored to the patient.

        Args:
            prompt: Input prompt (contains patient info and context)
            max_tokens: Ignored for template
            temperature: Ignored for template

        Returns:
            LLMResponse with template-generated recommendations
        """
        try:
            import re
            from app.models.schemas import PatientInput, SymptomInput

            # Extract patient info from prompt
            age_match = re.search(r'Age:\s*(\d+)', prompt)
            age = int(age_match.group(1)) if age_match else 30

            gender_match = re.search(r'Gender:\s*(\w+)', prompt)
            gender = gender_match.group(1) if gender_match else "unknown"

            # Extract primary symptom from prompt
            symptoms_match = re.search(r'Symptoms:\s*([^\n]+)', prompt)
            symptom_name = "general"
            if symptoms_match:
                symptoms_text = symptoms_match.group(1)
                # Extract first symptom name (before the parenthesis)
                first_symptom = re.match(r'([^(,]+)', symptoms_text)
                if first_symptom:
                    symptom_name = first_symptom.group(1).strip()

            # Extract chronic conditions
            conditions_match = re.search(r'Chronic Conditions:\s*([^\n]+)', prompt)
            conditions_text = conditions_match.group(1) if conditions_match else "None"

            # Extract current medications
            medications_match = re.search(r'Current Medications:\s*([^\n]+)', prompt)
            medications_text = medications_match.group(1) if medications_match else "None"

            # Extract allergies
            allergies_match = re.search(r'Allergies:\s*([^\n]+)', prompt)
            allergies_text = allergies_match.group(1) if allergies_match else "None"

            # Create minimal patient input object from extracted data
            patient_input = PatientInput(
                age=age,
                gender=gender,
                symptoms=[SymptomInput(name=symptom_name, severity=5, duration_days=1)],
                chronic_conditions=[c.strip() for c in conditions_text.split(',') if c.strip() and c.lower() != "none"],
                current_medications=[c.strip() for c in medications_text.split(',') if c.strip() and c.lower() != "none"],
                allergies=[a.strip() for a in allergies_text.split(',') if a.strip() and a.lower() != "none"]
            )

            # Build template response customized for this patient
            response_dict = build_template_response(prompt, patient_input)

            # Format as JSON string
            import json
            response_text = json.dumps(response_dict, indent=2)

            return LLMResponse(
                text=response_text,
                parsed_json=response_dict,
                model_name=self.model_name,
                tokens_used=0
            )

        except Exception as e:
            logger.error(f"Template generation failed: {e}")
            # Return safe default
            default_response = {
                "recommendations": [
                    {
                        "name": "Consult physician",
                        "dosage": "N/A",
                        "frequency": "N/A",
                        "duration": "N/A",
                        "evidence_ids": ["template_fallback"],
                        "reasoning": "Template fallback - please consult a healthcare provider"
                    }
                ],
                "warnings": ["Template-based response. Medical consultation required."],
                "confidence": "low"
            }
            import json
            return LLMResponse(
                text=json.dumps(default_response),
                parsed_json=default_response,
                model_name=self.model_name,
                error=str(e)
            )

    def is_available(self) -> bool:
        """Template is always available."""
        return True


class OpenAIClient(BaseLLMClient):
    """OpenAI API client for GPT models."""

    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        timeout: int = None
    ):
        """
        Initialize OpenAI client.

        Args:
            api_key: OpenAI API key (defaults to settings)
            model: Model name (defaults to settings)
            timeout: Request timeout (defaults to settings)

        Raises:
            LLMError: If API key is missing
        """
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_model
        self.timeout = timeout or settings.openai_timeout

        if not self.api_key:
            raise LLMError("OpenAI API key not provided")

        logger.info(f"Initialized OpenAIClient (model: {self.model})")

    async def generate(
        self,
        prompt: str,
        max_tokens: int = None,
        temperature: float = None
    ) -> LLMResponse:
        """
        Generate response using OpenAI API.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            LLMResponse with generated text

        Raises:
            LLMError: If API call fails
        """
        try:
            # Import openai library
            try:
                import openai
            except ImportError:
                raise LLMError("openai library not installed. Run: pip install openai")

            # Initialize client
            client = openai.AsyncOpenAI(api_key=self.api_key, timeout=self.timeout)

            # Make API call
            max_tokens = max_tokens or settings.openai_max_tokens
            temperature = temperature if temperature is not None else settings.llm_temperature

            logger.info(f"Calling OpenAI API: model={self.model}, max_tokens={max_tokens}")

            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                response_format={"type": "json_object"} if "gpt-4" in self.model or "gpt-3.5" in self.model else None
            )

            # Extract response
            response_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            logger.info(f"OpenAI response received: {tokens_used} tokens")

            # Parse JSON
            try:
                parsed_json = extract_json_from_response(response_text)
            except Exception as parse_error:
                logger.warning(f"Failed to parse JSON: {parse_error}")
                parsed_json = None

            return LLMResponse(
                text=response_text,
                parsed_json=parsed_json,
                model_name=self.model,
                tokens_used=tokens_used
            )

        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise LLMError(f"OpenAI API call failed: {e}")

    def is_available(self) -> bool:
        """Check if OpenAI client is available."""
        return bool(self.api_key)


class ClaudeClient(BaseLLMClient):
    """Anthropic Claude API client."""

    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        timeout: int = None
    ):
        """
        Initialize Claude client.

        Args:
            api_key: Claude API key (defaults to settings)
            model: Model name (defaults to settings)
            timeout: Request timeout (defaults to settings)

        Raises:
            LLMError: If API key is missing
        """
        self.api_key = api_key or settings.claude_api_key
        self.model = model or settings.claude_model
        self.timeout = timeout or settings.claude_timeout

        if not self.api_key:
            raise LLMError("Claude API key not provided")

        logger.info(f"Initialized ClaudeClient (model: {self.model})")

    async def generate(
        self,
        prompt: str,
        max_tokens: int = None,
        temperature: float = None
    ) -> LLMResponse:
        """
        Generate response using Claude API.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            LLMResponse with generated text

        Raises:
            LLMError: If API call fails
        """
        try:
            # Import anthropic library
            try:
                import anthropic
            except ImportError:
                raise LLMError("anthropic library not installed. Run: pip install anthropic")

            # Initialize client
            client = anthropic.AsyncAnthropic(api_key=self.api_key)

            # Make API call
            max_tokens = max_tokens or settings.claude_max_tokens
            temperature = temperature if temperature is not None else settings.llm_temperature

            logger.info(f"Calling Claude API: model={self.model}, max_tokens={max_tokens}")

            response = await client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system="You are a clinical decision support AI. Always respond with valid JSON only, no additional text or markdown formatting.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract response
            response_text = response.content[0].text
            tokens_used = response.usage.output_tokens

            logger.info(f"Claude response received: {tokens_used} tokens")

            # Parse JSON
            try:
                parsed_json = extract_json_from_response(response_text)
            except Exception as parse_error:
                logger.warning(f"Failed to parse JSON: {parse_error}")
                parsed_json = None

            return LLMResponse(
                text=response_text,
                parsed_json=parsed_json,
                model_name=self.model,
                tokens_used=tokens_used
            )

        except Exception as e:
            logger.error(f"Claude API call failed: {e}")
            raise LLMError(f"Claude API call failed: {e}")

    def is_available(self) -> bool:
        """Check if Claude client is available."""
        return bool(self.api_key)


class GeminiClient(BaseLLMClient):
    """Google Gemini API client."""

    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        timeout: int = None
    ):
        """
        Initialize Gemini client.

        Args:
            api_key: Gemini API key (defaults to settings)
            model: Model name (defaults to settings)
            timeout: Request timeout (defaults to settings)

        Raises:
            LLMError: If API key is missing
        """
        self.api_key = api_key or settings.gemini_api_key
        self.model = model or settings.gemini_model
        self.timeout = timeout or settings.gemini_timeout

        if not self.api_key:
            raise LLMError("Gemini API key not provided")

        logger.info(f"Initialized GeminiClient (model: {self.model})")

    async def generate(
        self,
        prompt: str,
        max_tokens: int = None,
        temperature: float = None
    ) -> LLMResponse:
        """
        Generate response using Gemini API.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            LLMResponse with generated text

        Raises:
            LLMError: If API call fails
        """
        try:
            # Import google-generativeai library
            try:
                import google.generativeai as genai
            except ImportError:
                raise LLMError("google-generativeai library not installed. Run: pip install google-generativeai")

            # Configure API key
            genai.configure(api_key=self.api_key)

            # Set generation config
            max_tokens = max_tokens or settings.gemini_max_tokens
            temperature = temperature if temperature is not None else settings.gemini_temperature

            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }

            logger.info(f"Calling Gemini API: model={self.model}, max_tokens={max_tokens}")

            # Initialize model
            model = genai.GenerativeModel(
                model_name=self.model,
                generation_config=generation_config
            )

            # Add strict JSON formatting instruction to prompt
            enhanced_prompt = (
                f"{prompt}\n\n"
                "IMPORTANT: Return ONLY valid JSON. "
                "No markdown, no prose, no code fences, no extra keys."
            )

            # Generate response (sync API wrapped in async)
            import asyncio
            response = await asyncio.to_thread(model.generate_content, enhanced_prompt)

            # Extract response text
            response_text = getattr(response, "text", "") or ""

            # Estimate tokens (rough approximation: 1 token ≈ 4 chars)
            tokens_used = len(response_text) // 4

            logger.info(f"Gemini response received: ~{tokens_used} tokens")

            # Parse JSON
            try:
                parsed_json = extract_json_from_response(response_text)
            except Exception as parse_error:
                logger.warning(f"Failed to parse JSON: {parse_error}")
                retry_config = {
                    "temperature": 0,
                    "max_output_tokens": max_tokens,
                }
                retry_prompt = (
                    f"{prompt}\n\n"
                    "Return ONLY this JSON object schema exactly: "
                    "{\"recommendations\":[],\"warnings\":[],\"confidence\":\"low\"}."
                )
                logger.info("Retrying Gemini call with strict JSON-only prompt")
                retry_model = genai.GenerativeModel(
                    model_name=self.model,
                    generation_config=retry_config,
                )
                retry_response = await asyncio.to_thread(retry_model.generate_content, retry_prompt)
                response_text = getattr(retry_response, "text", "") or ""
                try:
                    parsed_json = extract_json_from_response(response_text)
                except Exception as retry_parse_error:
                    logger.error(
                        "Gemini JSON parse failed after retry: %s | response=%s",
                        retry_parse_error,
                        response_text[:500],
                    )
                    raise LLMError(f"Gemini returned non-JSON response after retry: {retry_parse_error}")

            return LLMResponse(
                text=response_text,
                parsed_json=parsed_json,
                model_name=self.model,
                tokens_used=tokens_used
            )

        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise LLMError(f"Gemini API call failed: {e}")

    def is_available(self) -> bool:
        """Check if Gemini client is available."""
        return bool(self.api_key)


class AdaptiveGeminiClient(BaseLLMClient):
    """
    Adaptive Gemini client with Claude fallback and final template fallback.

    Tries Gemini first (free tier), automatically falls back to Claude
    on rate limit errors (429), and finally uses template mode if both fail.
    Caches preference for efficiency.
    """

    def __init__(
        self,
        gemini_api_key: str = None,
        gemini_model: str = None,
        claude_api_key: str = None,
        claude_model: str = None,
        timeout: int = None
    ):
        """
        Initialize adaptive client.

        Args:
            gemini_api_key: Gemini API key (defaults to settings)
            gemini_model: Gemini model (defaults to settings)
            claude_api_key: Claude API key (defaults to settings)
            claude_model: Claude model (defaults to settings)
            timeout: Request timeout (defaults to settings)
        """
        self.gemini_api_key = gemini_api_key or settings.gemini_api_key
        self.gemini_model = gemini_model or settings.gemini_model
        self.claude_api_key = claude_api_key or settings.claude_api_key
        self.claude_model = claude_model or settings.claude_model
        self.timeout = timeout or settings.gemini_timeout

        # Track which service to use
        self._prefer_claude = False  # Start with Gemini
        self._fallback_reason = None
        self.allow_template_fallback = settings.allow_template_fallback
        
        # Template fallback for when all APIs fail
        self._template_client = TemplateLLMClient()

        logger.info(
            f"Initialized AdaptiveGeminiClient "
            f"(primary: Gemini {self.gemini_model}, "
            f"fallback: Claude {self.claude_model}, "
            f"final: {'Template' if self.allow_template_fallback else 'LLMError'})"
        )

    async def generate(
        self,
        prompt: str,
        max_tokens: int = None,
        temperature: float = None
    ) -> LLMResponse:
        """
        Generate response, trying Gemini first, falling back to Claude.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            LLMResponse with generated text

        Raises:
            LLMError: If all services fail
        """
        last_error = None

        # Try Gemini first (unless we've already determined Claude is better)
        if not self._prefer_claude and self.gemini_api_key:
            try:
                logger.info("🤖 AdaptiveGeminiClient: Attempting Gemini API call...")
                gemini = GeminiClient(
                    api_key=self.gemini_api_key,
                    model=self.gemini_model,
                    timeout=self.timeout
                )
                response = await gemini.generate(prompt, max_tokens, temperature)

                # Success! Reset fallback flag if it was set
                if self._prefer_claude:
                    logger.info("✅ AdaptiveGeminiClient: Gemini working again, resuming as primary")
                    self._prefer_claude = False
                    self._fallback_reason = None
                else:
                    logger.info("✅ AdaptiveGeminiClient: Gemini API call succeeded")

                return response

            except Exception as e:
                error_str = str(e).lower()

                # Check for rate limit error (429)
                if "429" in error_str or "rate limit" in error_str or "quota" in error_str:
                    logger.warning(
                        f"⚠️  AdaptiveGeminiClient: Gemini rate limited - {e}. "
                        f"Falling back to Claude. "
                        f"(Free tier: 20 req/min limit)"
                    )
                    self._prefer_claude = True
                    self._fallback_reason = "Gemini rate limited (429)"
                    last_error = e
                    # Fall through to try Claude
                else:
                    logger.warning(f"⚠️  AdaptiveGeminiClient: Gemini error (not rate limit) - {e}. Trying Claude fallback.")
                    self._prefer_claude = True
                    self._fallback_reason = f"Gemini error: {str(e)[:100]}"
                    last_error = e
                    # Fall through to try Claude

        # Try Claude as primary or fallback
        if self.claude_api_key:
            try:
                if self._prefer_claude:
                    logger.info(f"🤖 AdaptiveGeminiClient: Using Claude fallback (reason: {self._fallback_reason})")
                else:
                    logger.info("🤖 AdaptiveGeminiClient: Using Claude (Gemini unavailable)")

                claude = ClaudeClient(
                    api_key=self.claude_api_key,
                    model=self.claude_model,
                    timeout=self.timeout
                )
                response = await claude.generate(prompt, max_tokens, temperature)
                logger.info("✅ AdaptiveGeminiClient: Claude API call succeeded")
                return response

            except Exception as e:
                logger.error(f"❌ AdaptiveGeminiClient: Claude fallback also failed - {e}")
                last_error = e

        if not self.allow_template_fallback:
            error_msg = (
                "All LLM providers failed and template fallback is disabled. "
                f"Last error: {last_error}"
            )
            logger.error("❌ AdaptiveGeminiClient: %s", error_msg)
            raise LLMError(error_msg)

        # Final fallback: Use template mode (optional)
        logger.warning(
            "⚠️  All LLM APIs failed (Gemini + Claude). "
            "Using template fallback mode for safe responses."
        )
        logger.info("🤖 AdaptiveGeminiClient: Using template fallback (final fallback)")

        try:
            response = await self._template_client.generate(prompt, max_tokens, temperature)
            logger.info("✅ AdaptiveGeminiClient: Template fallback succeeded")
            return response
        except Exception as template_error:
            error_msg = (
                f"AdaptiveGeminiClient: All services failed including template fallback. "
                f"Last LLM error: {last_error}, Template error: {template_error}"
            )
            logger.error(f"❌ {error_msg}")
            raise LLMError(error_msg)

    def is_available(self) -> bool:
        """
        Check if service is available.
        
        Returns True if at least one configured provider can be used.
        """
        return bool(self.gemini_api_key or self.claude_api_key or self.allow_template_fallback)

    def get_status(self) -> Dict:
        """Get status of all services."""
        return {
            "primary": "Gemini" if not self._prefer_claude else "Claude",
            "fallback_reason": self._fallback_reason,
            "gemini_available": bool(self.gemini_api_key),
            "claude_available": bool(self.claude_api_key),
            "template_fallback": self.allow_template_fallback
        }


class LLMClientFactory:
    """Factory for creating appropriate LLM client."""

    @staticmethod
    def create(strategy: str = None) -> BaseLLMClient:
        """
        Create LLM client based on strategy.

        Strategies:
        - "auto": Try Claude → Gemini → OpenAI → Template fallback
        - "claude": Use Claude API
        - "gemini": Use Google Gemini API
        - "gemini-fallback": Use Gemini with Claude fallback (recommended!)
        - "openai": Use OpenAI API
        - "template": Use template fallback
        - "local": Use local LLM (future)

        Args:
            strategy: LLM strategy (defaults to settings.llm_strategy)

        Returns:
            Appropriate LLM client

        Raises:
            LLMError: If requested strategy unavailable
        """
        strategy = strategy or settings.llm_strategy

        logger.info(f"Creating LLM client with strategy: {strategy}")

        if strategy == "gemini-fallback":
            # Gemini first, Claude fallback, optional template final fallback.
            fallback_label = "Template" if settings.allow_template_fallback else "LLMError"
            logger.info("Using adaptive client with Gemini → Claude → %s chain", fallback_label)
            return AdaptiveGeminiClient()

        elif strategy == "auto":
            # Auto-select based on availability
            # Priority: Claude → Gemini → OpenAI → Local → Template

            # Try Claude
            if settings.claude_api_key:
                try:
                    return ClaudeClient()
                except Exception as e:
                    logger.warning(f"Claude client unavailable: {e}, trying Gemini")

            # Try Gemini (FREE!)
            if settings.gemini_api_key:
                try:
                    return GeminiClient()
                except Exception as e:
                    logger.warning(f"Gemini client unavailable: {e}, trying OpenAI")

            # Try OpenAI
            if settings.openai_api_key:
                try:
                    return OpenAIClient()
                except Exception as e:
                    logger.warning(f"OpenAI client unavailable: {e}, falling back to template")

            # Try Local LLM
            if os.path.exists(settings.llm_model_path):
                # Future: return LocalLLMClient()
                logger.info("Local LLM model found but not implemented yet, using template")

            # Fallback to template
            logger.info("Using template fallback (no LLM available)")
            return TemplateLLMClient()

        elif strategy == "claude":
            return ClaudeClient()

        elif strategy == "gemini":
            return GeminiClient()

        elif strategy == "openai":
            return OpenAIClient()

        elif strategy == "template":
            return TemplateLLMClient()

        elif strategy == "local":
            # Future implementation
            logger.warning("Local LLM not implemented yet, using template")
            return TemplateLLMClient()

        else:
            raise LLMError(f"Unknown LLM strategy: {strategy}")
