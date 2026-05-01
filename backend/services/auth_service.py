"""
Authentication service — JWT tokens + password hashing.
"""
import os
import hashlib
import secrets
import json
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.schemas import User

# Simple JWT-like token system (no external dependency needed)
SECRET_KEY = os.environ.get("EDUPILOT_SECRET_KEY", "change-me-in-production")
TOKEN_EXPIRY_HOURS = 24

# In-memory token store (simple approach for academic project)
_active_tokens = {}


def hash_password(password: str) -> str:
    """Hash password with salt using SHA-256."""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(password: str, stored: str) -> bool:
    """Verify password against stored hash."""
    salt, hashed = stored.split(":")
    return hashlib.sha256((salt + password).encode()).hexdigest() == hashed


def create_token(user_id: int, username: str) -> str:
    """Create a simple session token."""
    token = secrets.token_urlsafe(32)
    _active_tokens[token] = {
        "user_id": user_id,
        "username": username,
        "created": datetime.utcnow().isoformat(),
        "expires": (datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)).isoformat(),
    }
    return token


def validate_token(token: str) -> dict:
    """Validate a token and return user info."""
    if token not in _active_tokens:
        return None
    info = _active_tokens[token]
    if datetime.fromisoformat(info["expires"]) < datetime.utcnow():
        del _active_tokens[token]
        return None
    return info


def revoke_token(token: str):
    """Revoke/logout a token."""
    _active_tokens.pop(token, None)


async def register_user(db: AsyncSession, username: str, password: str,
                        full_name: str, email: str = None) -> dict:
    """Register a new user."""
    # Check if username exists
    result = await db.execute(select(User).where(User.username == username))
    if result.scalar_one_or_none():
        raise ValueError("Username already exists")

    user = User(
        username=username,
        password_hash=hash_password(password),
        full_name=full_name,
        email=email,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    token = create_token(user.id, user.username)
    return {
        "user_id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "token": token,
    }


async def login_user(db: AsyncSession, username: str, password: str) -> dict:
    """Authenticate a user."""
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        raise ValueError("Invalid username or password")

    token = create_token(user.id, user.username)
    return {
        "user_id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "token": token,
    }
