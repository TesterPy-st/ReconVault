"""
User authentication model for ReconVault intelligence system.

This module defines the User SQLAlchemy model for authentication
and user management.
"""

import enum
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class UserRole(str, enum.Enum):
    """Enumeration of user roles"""

    ADMIN = "admin"
    ANALYST = "analyst"
    INVESTIGATOR = "investigator"
    VIEWER = "viewer"
    AUDITOR = "auditor"


class UserStatus(str, enum.Enum):
    """Enumeration of user status values"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class User(Base):
    """
    User model for authentication and authorization.

    Attributes:
        id (int): Primary key
        username (str): Unique username
        email (str): Unique email address
        hashed_password (str): Hashed password
        full_name (str): User's full name
        role (UserRole): User role for authorization
        status (UserStatus): Account status
        is_active (bool): Whether user account is active
        is_superuser (bool): Whether user is a superuser
        is_verified (bool): Whether email has been verified
        last_login (datetime): Last login timestamp
        login_count (int): Number of successful logins
        failed_login_attempts (int): Number of failed login attempts
        password_changed_at (datetime): When password was last changed
        preferences (str): JSON string for user preferences
        profile_data (str): JSON string for profile information
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
    """

    __tablename__ = "users"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Authentication fields
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    # User information
    full_name = Column(String(100), nullable=True)
    role = Column(String(20), default=UserRole.VIEWER, nullable=False, index=True)
    status = Column(
        String(30), default=UserStatus.PENDING_VERIFICATION, nullable=False, index=True
    )

    # Security and status flags
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Login tracking
    last_login = Column(DateTime(timezone=True), nullable=True)
    login_count = Column(Integer, default=0, nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)

    # Password management
    password_changed_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Preferences and profile
    preferences = Column(Text, nullable=True)  # JSON string for user preferences
    profile_data = Column(Text, nullable=True)  # JSON string for profile information

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    audit_logs = relationship("AuditLog", back_populates="user")

    def __repr__(self) -> str:
        """String representation of User instance"""
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', role='{self.role}')>"

    @property
    def is_authenticated(self) -> bool:
        """
        Check if user is authenticated (always True for existing user records).

        Returns:
            bool: True if user is authenticated
        """
        return self.is_active and self.status == UserStatus.ACTIVE

    @property
    def display_name(self) -> str:
        """
        Get user's display name.

        Returns:
            str: Display name (full name or username)
        """
        return self.full_name or self.username

    @property
    def risk_level(self) -> str:
        """
        Get risk level based on user properties.

        Returns:
            str: Risk level category
        """
        if self.is_superuser:
            return "high"
        elif self.failed_login_attempts > 5:
            return "medium"
        elif self.status == UserStatus.SUSPENDED:
            return "high"
        elif not self.is_verified:
            return "medium"
        else:
            return "low"

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        Convert User instance to dictionary.

        Args:
            include_sensitive (bool): Whether to include sensitive fields

        Returns:
            dict: Dictionary representation of user
        """
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "status": self.status,
            "display_name": self.display_name,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "is_verified": self.is_verified,
            "is_authenticated": self.is_authenticated,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "login_count": self.login_count,
            "failed_login_attempts": self.failed_login_attempts,
            "password_changed_at": self.password_changed_at.isoformat()
            if self.password_changed_at
            else None,
            "preferences": self.preferences,
            "profile_data": self.profile_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "risk_level": self.risk_level,
        }

        if include_sensitive:
            data["hashed_password"] = self.hashed_password

        return data

    def increment_login_count(self) -> None:
        """
        Increment login count and update last login timestamp.
        """
        from datetime import datetime, timezone

        self.login_count += 1
        self.last_login = datetime.now(timezone.utc)
        self.failed_login_attempts = 0

    def increment_failed_login(self) -> None:
        """
        Increment failed login attempts.
        """
        from datetime import datetime, timezone

        self.failed_login_attempts += 1

        # Auto-suspend after too many failed attempts
        if self.failed_login_attempts >= 10:
            self.status = UserStatus.SUSPENDED

    def reset_failed_login_attempts(self) -> None:
        """
        Reset failed login attempts (on successful login).
        """
        self.failed_login_attempts = 0

    def activate(self) -> None:
        """
        Activate user account.
        """
        self.is_active = True
        self.status = UserStatus.ACTIVE

    def deactivate(self) -> None:
        """
        Deactivate user account.
        """
        self.is_active = False
        self.status = UserStatus.INACTIVE

    def verify_email(self) -> None:
        """
        Mark user email as verified.
        """
        self.is_verified = True
        if self.status == UserStatus.PENDING_VERIFICATION:
            self.status = UserStatus.ACTIVE

    def suspend(self) -> None:
        """
        Suspend user account.
        """
        self.status = UserStatus.SUSPENDED
        self.is_active = False

    def change_password(self, new_hashed_password: str) -> None:
        """
        Change user password.

        Args:
            new_hashed_password (str): New hashed password
        """
        from datetime import datetime, timezone

        self.hashed_password = new_hashed_password
        self.password_changed_at = datetime.now(timezone.utc)
        self.failed_login_attempts = 0


# Indexes for performance optimization
User.__table__.append_column(Column("idx_user_username_email", String(150), index=True))

User.__table__.append_column(Column("idx_user_role_status", String(50), index=True))
