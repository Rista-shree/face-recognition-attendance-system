# ─────────────────────────────────────────────
#  backend/api/dependencies.py
#  Reusable FastAPI dependency injectors:
#    - DB session
#    - JWT auth guard
#    - Admin-only guard
#    - Desktop API key guard
# ─────────────────────────────────────────────

from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from database.connection import get_db
from models.user import User


# ── OAuth2 token extractor ─────────────────────────────────────────────
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# ── Desktop static API key header ──────────────────────────────────────
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


# ── JWT current-user dependency ────────────────────────────────────────

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Decode JWT and return the authenticated User, or raise 401."""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        # Ensure payload is a dict and contains "sub"
        if not isinstance(payload, dict) or "sub" not in payload:
            raise credentials_exception

        username = str(payload["sub"])

    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise credentials_exception

    return user


# ── Admin-only dependency ─────────────────────────────────────────────

async def get_current_admin(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Restrict endpoint to admin users only."""

    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user


# ── Desktop API key dependency ─────────────────────────────────────────

async def verify_desktop_key(
    api_key: Annotated[str | None, Security(api_key_header)]
) -> bool:
    """
    Allow requests from the desktop app using a static API key.
    Used for the /api/attendance/bulk endpoint.
    """

    if api_key and api_key == settings.DESKTOP_API_KEY:
        return True

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid or missing API key",
    )


# ── Type aliases for cleaner route signatures ──────────────────────────

DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(get_current_admin)]
DesktopAuth = Annotated[bool, Depends(verify_desktop_key)]