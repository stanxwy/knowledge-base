"""Auth-related Pydantic schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)


class _UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    display_name: str
    email: str | None = None
    department_id: int | None = None
    is_superuser: bool = False


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_info: _UserSummary
    permissions: list[str] = []


class CurrentUserResponse(BaseModel):
    user_info: _UserSummary
    roles: list[str] = []
    permissions: list[str] = []
    department: dict | None = None