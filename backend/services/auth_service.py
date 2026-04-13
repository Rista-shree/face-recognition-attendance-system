# ─────────────────────────────────────────────
#  backend/services/auth_service.py
#  Password hashing and JWT creation/decoding.
# ─────────────────────────────────────────────

from datetime import datetime, timedelta, timezone
from typing   import Optional

from jose       import jwt, JWTError
from passlib.context import CryptContext

from config.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Password helpers ──────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ── Token helpers ─────────────────────────────────────────────────────────────

def create_access_token(subject: str) -> str:
    """Create a short-lived JWT access token."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return _encode({"sub": subject, "type": "access", "exp": expire})


def create_refresh_token(subject: str) -> str:
    """Create a long-lived JWT refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    return _encode({"sub": subject, "type": "refresh", "exp": expire})


def decode_token(token: str) -> Optional[dict]:
    """
    Decode a JWT and return its payload, or None if invalid/expired.
    """
    try:
        return jwt.decode(token, settings.SECRET_KEY,
                          algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


# ── Internal ──────────────────────────────────────────────────────────────────

def _encode(payload: dict) -> str:
    return jwt.encode(payload, settings.SECRET_KEY,
                      algorithm=settings.ALGORITHM)