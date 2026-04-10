"""
Database session and connection management.
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.db.base import Base

logger = logging.getLogger(__name__)

# Database engine and session factory
engine = None
SessionLocal = None


def init_db():
    """Initialize database connection and create tables."""
    global engine, SessionLocal

    try:
        # Create database engine
        engine = create_engine(
            settings.database_url,
            echo=settings.debug,
            pool_pre_ping=True,
            pool_recycle=3600,
        )

        # Create session factory
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # Create tables (idempotent)
        Base.metadata.create_all(bind=engine)

        logger.info("✓ Database initialized successfully")
        return True

    except Exception as e:
        logger.error(f"✗ Failed to initialize database: {e}")
        return False


def get_session() -> Session:
    """Get a database session for dependency injection."""
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def close_db():
    """Close the database connection pool."""
    global engine

    if engine:
        engine.dispose()
        logger.info("✓ Database connection pool closed")
