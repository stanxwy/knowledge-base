"""Pydantic request/response schemas for KBMS admin."""
from admin.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    CurrentUserResponse,
)
from admin.schemas.org import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentOut,
    DepartmentNode,
    RoleCreate,
    RoleUpdate,
    RoleOut,
    RoleWithPermissions,
    RolePermissionsUpdate,
    PermissionOut,
    UserCreate,
    UserUpdate,
    UserOut,
    UserDetail,
    UserPasswordResetResponse,
    UserListQuery,
    PageResult,
)

__all__ = [
    # auth
    "LoginRequest",
    "LoginResponse",
    "RefreshRequest",
    "CurrentUserResponse",
    # org
    "DepartmentCreate",
    "DepartmentUpdate",
    "DepartmentOut",
    "DepartmentNode",
    "RoleCreate",
    "RoleUpdate",
    "RoleOut",
    "RoleWithPermissions",
    "RolePermissionsUpdate",
    "PermissionOut",
    "UserCreate",
    "UserUpdate",
    "UserOut",
    "UserDetail",
    "UserPasswordResetResponse",
    "UserListQuery",
    "PageResult",
]