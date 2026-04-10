"""
MediRAG FastAPI Application

Clinical Decision Support System with RAG-based recommendations and safety validation.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.models.schemas import HealthResponse

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True,
)
logger = logging.getLogger(__name__)
logging.getLogger("app").setLevel(settings.log_level)

# Global RAG pipeline instance (initialized at startup)
_global_rag_pipeline = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager.

    Handles startup and shutdown events:
    - Startup: Initialize RAG pipeline and all heavy components
    - Shutdown: Clean up resources
    """
    # Startup event
    startup_start = __import__('time').time()
    logger.info("=" * 60)
    logger.info("🚀 MediRAG Starting up...")
    logger.info(
        "Runtime LLM config: strategy=%s, allow_template_fallback=%s",
        settings.llm_strategy,
        settings.allow_template_fallback,
    )
    logger.info("=" * 60)

    try:
        # Initialize RAG pipeline (this loads embedder, vectorstore, models, etc.)
        logger.info("Initializing RAG Pipeline and components...")
        try:
            from app.core.rag.pipeline import RAGPipeline
            from app.core.safety.validator import SafetyValidator
            global _global_rag_pipeline
            _global_rag_pipeline = RAGPipeline()

            # Pre-load safety validator data (2.8M interactions) at startup
            # This prevents 30+ second delay on first request
            logger.info("Pre-loading safety validator drug interactions...")
            safety_validator = SafetyValidator.get_instance()
            safety_validator._load_interactions()
            logger.info(f"✓ Loaded safety data: {len(safety_validator._interaction_index)} drug pairs")
        except Exception as rag_error:
            logger.warning(f"⚠️  RAG Pipeline initialization failed: {str(rag_error)[:100]}")
            logger.warning("⚠️  Authentication and API endpoints will still work, but RAG features disabled")
            _global_rag_pipeline = None

        startup_duration = __import__('time').time() - startup_start
        logger.info("=" * 60)
        logger.info(f"✅ MediRAG initialized successfully in {startup_duration:.2f}s")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ Failed to initialize RAG Pipeline: {e}")
        raise

    yield

    # Shutdown event
    logger.info("Shutting down MediRAG...")
    _global_rag_pipeline = None


def get_global_pipeline():
    """
    Get the global RAG pipeline instance.

    This is initialized at startup, so requests should never see None.
    """
    if _global_rag_pipeline is None:
        raise RuntimeError(
            "RAG Pipeline not initialized. This should not happen if lifespan startup succeeded."
        )
    return _global_rag_pipeline


# Initialize FastAPI app with lifespan
app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="Clinical Decision Support System with AI-powered medication recommendations",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Check API health status and RAG components."""
    components = {
        "database": "not_initialized",
        "llm": "unknown",
        "vector_store": "unknown"
    }

    try:
        # Check RAG pipeline (initialized at startup)
        pipeline = get_global_pipeline()
        components["vector_store"] = f"healthy ({pipeline.vectorstore.num_documents} documents)"
        components["llm"] = f"{pipeline.llm_client.__class__.__name__} (available)"
        components["database"] = "ready"
    except Exception as e:
        components["vector_store"] = f"error: {str(e)[:50]}"
        logger.error(f"Pipeline health check failed: {e}")

    return HealthResponse(
        status="healthy",
        version=settings.version,
        components=components
    )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "MediRAG API",
        "version": settings.version,
        "docs": "/docs",
        "health": "/health"
    }


# Include API routers
from app.api.v1.endpoints import auth, diagnoses_api, patients

# Try to load RAG-related endpoints, but don't fail if they have dependency issues
try:
    from app.api.v1.endpoints import diagnosis, explainability, safety, diagnoses_crud, recommendations
    rag_available = True
except ImportError as e:
    logger.warning(f"RAG endpoints not available: {str(e)[:100]}")
    rag_available = False

app.include_router(
    auth.router,
    prefix=settings.api_v1_prefix,
    tags=["Auth"]
)

app.include_router(
    diagnoses_api.router,
    prefix=settings.api_v1_prefix,
    tags=["Diagnoses API"]
)

app.include_router(
    patients.router,
    prefix=settings.api_v1_prefix,
    tags=["Patients"]
)

if rag_available:
    app.include_router(
        diagnosis.router,
        prefix=settings.api_v1_prefix,
        tags=["Diagnosis"]
    )

    app.include_router(
        safety.router,
        prefix=settings.api_v1_prefix,
        tags=["Safety"]
    )

    app.include_router(
        explainability.router,
        prefix=settings.api_v1_prefix,
        tags=["Explainability"]
    )

    app.include_router(
        diagnoses_crud.router,
        prefix=settings.api_v1_prefix,
        tags=["Diagnoses"]
    )

    app.include_router(
        recommendations.router,
        prefix=settings.api_v1_prefix,
        tags=["Recommendations"]
    )
    logger.info("✓ RAG endpoints loaded successfully")
else:
    logger.warning("⚠️  RAG endpoints disabled due to dependency issues")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
