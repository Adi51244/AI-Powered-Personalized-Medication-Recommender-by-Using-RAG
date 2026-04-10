"""
Pytest configuration and fixtures for MediRAG tests.
"""
import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.db.base import Base


# Test database URL (use in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_engine():
    """Create a test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def sample_patient_input():
    """Sample patient input for testing."""
    return {
        "age": 55,
        "gender": "male",
        "weight_kg": 75.0,
        "height_cm": 175.0,
        "symptoms": [
            {"name": "chest pain", "severity": 7, "duration_days": 2},
            {"name": "shortness of breath", "severity": 6, "duration_days": 3}
        ],
        "chronic_conditions": ["hypertension"],
        "allergies": [],
        "current_medications": ["lisinopril"]
    }


@pytest.fixture
def sample_medications():
    """Sample medication list for safety testing."""
    return ["aspirin", "lisinopril", "metformin"]


@pytest.fixture
def patient_with_allergies():
    """Patient with known allergies for testing."""
    return {
        "age": 45,
        "gender": "female",
        "allergies": ["penicillin", "sulfa"],
        "chronic_conditions": ["diabetes_type2"],
        "current_medications": ["metformin"]
    }


# TODO: Add more fixtures as we implement components
# - mock_llm_generator
# - mock_embedder
# - mock_vector_store
# - sample_corpus
# - sample_faiss_index
