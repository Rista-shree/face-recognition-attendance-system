# ─────────────────────────────────────────────
#  backend/api/routes/auth.py
# ─────────────────────────────────────────────

from fastapi  import APIRouter, HTTPException, status, Depends
from fastapi.security import  OAuth2PasswordRequestForm
from sqlalchemy import select


from api.dependencies   import DBSession, CurrentUser
from models.user        import User
from schemas.auth       import LoginRequest, TokenResponse, RefreshRequest, UserCreate, UserOut
from services.auth_service import (
    verify_password, hash_password,
    create_access_token, create_refresh_token, decode_token,
)

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    db: DBSession,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    result = await db.execute(
        select(User).where(User.username == form_data.username)
    )

    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    return TokenResponse(
        access_token=create_access_token(user.username),
        refresh_token=create_refresh_token(user.username),
    )
@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest, db: DBSession):
    """Exchange a valid refresh token for a new token pair."""
    data = decode_token(payload.refresh_token)

    if not data or data.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    username = data.get("sub")
    result   = await db.execute(select(User).where(User.username == username))
    user     = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User not found")

    return TokenResponse(
        access_token=create_access_token(user.username),
        refresh_token=create_refresh_token(user.username),
    )


@router.get("/me", response_model=UserOut)
async def me(current_user: CurrentUser):
    """Return the currently authenticated user's profile."""
    return current_user


@router.post("/register", response_model=UserOut, status_code=201)
async def register(payload: UserCreate, db: DBSession):
    """
    Create a new dashboard user.
    In production, restrict this to admins only.
    """
    # Check for duplicate username/email
    existing = await db.execute(
        select(User).where(User.username == payload.username)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Username already taken")

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user