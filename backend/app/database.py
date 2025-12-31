"""
Database configuration and connection management for ReconVault.

This module handles SQLAlchemy engine setup, session management,
and database initialization for PostgreSQL.
"""

from sqlalchemy import create_engine, MetaData, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator
import logging
from .config import settings

# Configure logging
logger = logging.getLogger("reconvault.database")

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base for models
Base = declarative_base()

# Create metadata instance for table creation
metadata = MetaData()


def get_db() -> Generator[Session, None, None]:
    """
    Database dependency function for FastAPI endpoints.
    
    Yields:
        Session: SQLAlchemy database session
    
    Example:
        @app.get("/users/")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        logger.debug("Database session created")
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
        logger.debug("Database session closed")


def init_db() -> None:
    """
    Initialize database tables.
    
    Creates all tables defined in the models using SQLAlchemy metadata.
    Should be called during application startup.
    """
    try:
        logger.info("Initializing database tables...")
        
        # Import all models to ensure they are registered with Base
        from app.models import target, entity, relationship, intelligence, user, audit
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database tables initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def close_db_connections() -> None:
    """
    Close all database connections.
    
    Should be called during application shutdown.
    """
    try:
        logger.info("Closing database connections...")
        engine.dispose()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")
        raise


def test_db_connection() -> bool:
    """
    Test database connection.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


# Database event listeners
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Set SQLite-specific pragmas for PostgreSQL compatibility.
    This function is primarily for SQLite but can be extended for PostgreSQL optimizations.
    """
    pass


def get_db_info() -> dict:
    """
    Get database connection information.
    
    Returns:
        dict: Database connection details
    """
    return {
        "database_url": settings.SQLALCHEMY_DATABASE_URL.replace(
            settings.POSTGRES_PASSWORD, "***"
        ),  # Hide password in logs
        "pool_size": engine.pool.size(),
        "checked_in": engine.pool.checkedin(),
        "checked_out": engine.pool.checkedout(),
        "overflow": engine.pool.overflow(),
        "invalid": engine.pool.invalid()
    }