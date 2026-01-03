"""
Custom exceptions for ReconVault backend application.

This module defines custom exception classes for handling specific
error scenarios in the ReconVault intelligence system.
"""

from typing import Any, Dict, Optional


class ReconVaultException(Exception):
    """Base exception class for ReconVault"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class EntityNotFoundError(ReconVaultException):
    """Raised when an entity is not found in the database"""

    def __init__(self, entity_id: str, details: Optional[Dict[str, Any]] = None):
        message = f"Entity with ID '{entity_id}' not found"
        super().__init__(message, details)
        self.entity_id = entity_id


class RelationshipNotFoundError(ReconVaultException):
    """Raised when a relationship is not found in the database"""

    def __init__(self, relationship_id: str, details: Optional[Dict[str, Any]] = None):
        message = f"Relationship with ID '{relationship_id}' not found"
        super().__init__(message, details)
        self.relationship_id = relationship_id


class DuplicateEntityError(ReconVaultException):
    """Raised when attempting to create a duplicate entity"""

    def __init__(
        self,
        entity_value: str,
        entity_type: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        message = f"Entity already exists: {entity_type}={entity_value}"
        super().__init__(message, details)
        self.entity_value = entity_value
        self.entity_type = entity_type


class InvalidRelationshipError(ReconVaultException):
    """Raised when a relationship is invalid"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class ValidationError(ReconVaultException):
    """Raised when data validation fails"""

    def __init__(
        self, field: str, message: str, details: Optional[Dict[str, Any]] = None
    ):
        full_message = f"Validation error for '{field}': {message}"
        super().__init__(full_message, details)
        self.field = field


class DatabaseError(ReconVaultException):
    """Raised when a database operation fails"""

    def __init__(
        self, operation: str, message: str, details: Optional[Dict[str, Any]] = None
    ):
        full_message = f"Database error during '{operation}': {message}"
        super().__init__(full_message, details)
        self.operation = operation


class Neo4jError(ReconVaultException):
    """Raised when a Neo4j operation fails"""

    def __init__(
        self, operation: str, message: str, details: Optional[Dict[str, Any]] = None
    ):
        full_message = f"Neo4j error during '{operation}': {message}"
        super().__init__(full_message, details)
        self.operation = operation


class CollectionTaskNotFoundError(ReconVaultException):
    """Raised when a collection task is not found"""

    def __init__(self, task_id: str, details: Optional[Dict[str, Any]] = None):
        message = f"Collection task with ID '{task_id}' not found"
        super().__init__(message, details)
        self.task_id = task_id


class RiskAssessmentError(ReconVaultException):
    """Raised when risk assessment fails"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class AuthenticationError(ReconVaultException):
    """Raised when authentication fails"""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, details)


class AuthorizationError(ReconVaultException):
    """Raised when authorization fails"""

    def __init__(
        self,
        message: str = "Authorization failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, details)


__all__ = [
    "ReconVaultException",
    "EntityNotFoundError",
    "RelationshipNotFoundError",
    "DuplicateEntityError",
    "InvalidRelationshipError",
    "ValidationError",
    "DatabaseError",
    "Neo4jError",
    "CollectionTaskNotFoundError",
    "RiskAssessmentError",
    "AuthenticationError",
    "AuthorizationError",
]
