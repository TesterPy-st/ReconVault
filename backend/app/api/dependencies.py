"""
FastAPI dependencies for ReconVault backend application.

This module provides dependency injection functions for database sessions,
Neo4j connections, and authentication.
"""

import logging
from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from neo4j import Session as Neo4jSession
from sqlalchemy.orm import Session

from app.database import get_db
from app.intelligence_graph.neo4j_client import Neo4jClient, get_neo4j_client

# Configure logging
logger = logging.getLogger("reconvault.dependencies")

# Security scheme for Bearer token authentication
security = HTTPBearer(auto_error=False)


def get_database() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.

    Yields:
        Session: SQLAlchemy database session

    Example:
        @app.get("/entities/")
        def get_entities(db: Session = Depends(get_database)):
            return db.query(Entity).all()
    """
    yield from get_db()


def get_neo4j_session() -> Neo4jClient:
    """
    Dependency function to get Neo4j client.

    Returns:
        Neo4jClient: Neo4j database client

    Example:
        @app.get("/graph/")
        def get_graph(neo4j: Neo4jClient = Depends(get_neo4j_session)):
            return neo4j.get_graph_stats()
    """
    client = get_neo4j_client()
    if not client.driver:
        logger.error("Neo4j client not initialized")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Neo4j service unavailable",
        )
    return client


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[dict]:
    """
    Dependency function to get current authenticated user.

    This is a placeholder for future authentication implementation.
    Currently returns None to allow unauthenticated access.

    Args:
        credentials: HTTP Bearer token credentials

    Returns:
        Optional[dict]: User information if authenticated, None otherwise

    Example:
        @app.get("/protected/")
        def protected_route(user: dict = Depends(get_current_user)):
            return {"user": user}
    """
    # TODO: Implement JWT token validation and user retrieval
    # For now, allow unauthenticated access
    if credentials is None:
        return None

    # Placeholder for token validation
    token = credentials.credentials
    logger.debug(f"Authentication token received: {token[:10]}...")

    # Return placeholder user
    return {"id": "placeholder", "username": "anonymous", "role": "user"}


async def require_authenticated_user(
    user: Optional[dict] = Depends(get_current_user),
) -> dict:
    """
    Dependency function to require authenticated user.

    Raises HTTPException if user is not authenticated.

    Args:
        user: Current user from get_current_user dependency

    Returns:
        dict: User information

    Raises:
        HTTPException: If user is not authenticated

    Example:
        @app.delete("/entities/{entity_id}")
        def delete_entity(
            entity_id: UUID,
            user: dict = Depends(require_authenticated_user)
        ):
            # Only authenticated users can delete
            ...
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_pagination_params(limit: int = 50, offset: int = 0) -> dict:
    """
    Dependency function to get pagination parameters.

    Args:
        limit: Maximum number of items to return (default: 50)
        offset: Number of items to skip (default: 0)

    Returns:
        dict: Pagination parameters

    Raises:
        HTTPException: If pagination parameters are invalid

    Example:
        @app.get("/entities/")
        def get_entities(
            pagination: dict = Depends(get_pagination_params)
        ):
            limit = pagination["limit"]
            offset = pagination["offset"]
            ...
    """
    if limit < 1 or limit > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be between 1 and 1000",
        )

    if offset < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Offset must be non-negative",
        )

    return {"limit": limit, "offset": offset}


__all__ = [
    "get_database",
    "get_neo4j_session",
    "get_current_user",
    "require_authenticated_user",
    "get_pagination_params",
]
