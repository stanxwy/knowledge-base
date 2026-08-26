"""Org-module Pydantic schemas (users, departments, roles, permissions)."""
from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints


# =========================
# Common / pagination
# =========================


class Page(BaseModel):
    page: int = 1
    page_size: int = 20


class PageResult(BaseModel):
    items: list
    total: int
    page: int
    page_size: int


# =========================
# Departments
# =========================


class DepartmentBase(BaseModel):
    name: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    parent_id: int | None = None
    leader_id: int | None = None
    sort_order: int = 0


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Annotated[str, StringConstraints(min_length=1, max_length=128)] | None = None
    parent_id: int | None = None
    leader_id: int | None = None
    sort_order: int | None = None


class DepartmentOut(DepartmentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


class DepartmentNode(DepartmentOut):
    """Tree node with children list."""
    children: list["DepartmentNode"] = []


# =========================
# Roles
# =========================


class RoleBase(BaseModel):
    role_name: Annotated[str, StringConstraints(min_length=1, max_length=64)]
    role_code: Annotated[str, StringConstraints(min_length=1, max_length=64)]
    description: str | None = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    role_name: str | None = None
    description: str | None = None


class RoleOut(RoleBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_builtin: bool
    created_at: datetime
    updated_at: datetime


class PermissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    permission_code: str
    permission_type: str
    resource: str
    action: str
    description: str | None = None


class RolePermissionsUpdate(BaseModel):
    """Replace all permission codes for a role."""
    permission_codes: list[str]


class RoleWithPermissions(RoleOut):
    permissions: list[str] = []


# =========================
# Users
# =========================


class UserBase(BaseModel):
    username: Annotated[str, StringConstraints(min_length=1, max_length=64)]
    display_name: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    email: str | None = None
    department_id: int | None = None
    role_ids: list[int] = []
    status: int = 1  # 1 active, 0 disabled


class UserCreate(UserBase):
    password: Annotated[str, StringConstraints(min_length=6, max_length=128)]


class UserUpdate(BaseModel):
    display_name: str | None = None
    email: str | None = None
    department_id: int | None = None
    role_ids: list[int] | None = None
    status: int | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    display_name: str
    email: str | None
    department_id: int | None
    status: int
    is_superuser: bool
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime


class UserDetail(UserOut):
    roles: list[RoleOut] = []
    department: DepartmentOut | None = None


class UserPasswordResetResponse(BaseModel):
    new_password: str


class UserListQuery(Page):
    keyword: str | None = None
    department_id: int | None = None
    role_id: int | None = None
    status: int | None = None


DepartmentNode.model_rebuild()