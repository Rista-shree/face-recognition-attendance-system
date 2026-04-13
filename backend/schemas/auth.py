# ─────────────────────────────────────────────
#  backend/schemas/auth.py
# ─────────────────────────────────────────────

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token:  str
    refresh_token: str
    token_type:    str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserCreate(BaseModel):
    username: str
    email:    EmailStr
    password: str
    role:     str = "staff"


class UserOut(BaseModel):
    id:       int
    username: str
    email:    str
    role:     str
    is_active: bool

    class Config:
        from_attributes = True