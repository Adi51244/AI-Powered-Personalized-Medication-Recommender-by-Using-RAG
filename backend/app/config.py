from typing import Optional
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=str(ENV_FILE), case_sensitive=False)

    # Database
    database_url: str = "postgresql://medirag:changeme@localhost:5432/medirag"

    # BigQuery (MIMIC-III Data Access)
    google_cloud_project: Optional[str] = None
    google_application_credentials: Optional[str] = None
    mimic_dataset: str = "physionet-data.mimiciii_clinical"

    # Local LLM
    llm_model_path: str = "./data/models/llama-3-8b-instruct.gguf"
    llm_context_size: int = 4096
    llm_temperature: float = 0.3
    llm_gpu_layers: int = 35

    # Vector Store
    faiss_index_path: str = "./data/processed/faiss_index/faiss.index"
    corpus_metadata_path: str = "./data/processed/corpus_metadata.json"

    # ML Models
    ml_models_path: str = "./data/models/disease_models/"

    # Embedding Model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Drug Interaction Database
    drug_interactions_path: str = "./data/processed/drug_interactions.json"

    # Safety Layer
    safety_enabled: bool = True
    safety_max_warnings: int = 50
    safety_block_on_major_interaction: bool = True

    # RAG Retrieval Configuration
    # Optimized for performance: reduced top_k from 10 to 5
    retrieval_top_k: int = 5
    retrieval_min_score: float = 0.3
    retrieval_use_mmr: bool = True
    mmr_diversity_lambda: float = 0.5
    # Optimized FAISS nprobe: reduced from 32 to 16 for faster search
    faiss_nprobe: int = 16

    # LLM Strategy
    # Recommended: "gemini-fallback" (free Gemini with Claude backup)
    # - "gemini-fallback": Try Gemini first, fallback to Claude on rate limit (RECOMMENDED - FREE!)
    # - "auto": Try Claude → Gemini → OpenAI → Template
    # - "claude": Claude API only
    # - "gemini": Gemini API only
    # - "openai": OpenAI API only
    # - "template": Template-based (no LLM)
    llm_strategy: str = "gemini-fallback"  # Changed from "auto"
    allow_template_fallback: bool = False

    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    openai_max_tokens: int = 1000
    openai_timeout: int = 30

    # Gemini Configuration
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-1.5-flash-latest"  # or gemini-1.5-pro-latest
    gemini_max_tokens: int = 1000
    gemini_temperature: float = 0.3
    gemini_timeout: int = 30

    # Claude Configuration
    claude_api_key: Optional[str] = None
    claude_model: str = "claude-3-5-sonnet-20241022"
    claude_max_tokens: int = 1000
    claude_timeout: int = 30

    # Performance
    enable_response_caching: bool = True
    cache_ttl_seconds: int = 3600

    # API Settings
    api_v1_prefix: str = "/api/v1"
    project_name: str = "MediRAG"
    version: str = "1.0.0"
    debug: bool = True

    # CORS
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Supabase Configuration
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None

    # Logging
    log_level: str = "INFO"

    @property
    def cors_origins(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


# Global settings instance
settings = Settings()
