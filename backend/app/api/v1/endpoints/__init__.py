"""
API v1 endpoints for MediRAG.
"""

# Only import non-RAG endpoints
from . import patients

# RAG-dependent endpoints will be imported conditionally in main.py
__all__ = [
    "patients",
]

