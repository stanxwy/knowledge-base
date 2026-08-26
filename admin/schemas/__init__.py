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
from admin.schemas.knowledge import (
    KnowledgeUnitCreate,
    KnowledgeUnitUpdate,
    KnowledgeUnitOut,
    KnowledgeUnitDetail,
    KnowledgeUnitListQuery,
    BatchDeleteRequest,
    UnitPermissionOut,
    UnitPermissionSpec,
    UnitPermissionsReplace,
    CheckPermissionsRequest,
    CheckPermissionsResponse,
)
from admin.schemas.import_task import ImportTaskStatus, ImportTaskFileResult
from admin.schemas.ai import ChatRequest, ChatMessage, SessionSummary
from admin.schemas.dashboard import (
    DashboardMetrics,
    QuestionRank,
    UnitRank,
    DailyTrendPoint,
)
from admin.schemas.settlement import (
    FAQRecommendation,
    FAQPublished,
    FAQReviewRequest,
    FAQManualCreate,
    KnowledgeGapOut,
    KnowledgeGapUpdate,
    KnowledgeGapCreateUnitRequest,
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
    # knowledge
    "KnowledgeUnitCreate",
    "KnowledgeUnitUpdate",
    "KnowledgeUnitOut",
    "KnowledgeUnitDetail",
    "KnowledgeUnitListQuery",
    "BatchDeleteRequest",
    "UnitPermissionOut",
    "UnitPermissionSpec",
    "UnitPermissionsReplace",
    "CheckPermissionsRequest",
    "CheckPermissionsResponse",
    "ImportTaskStatus",
    "ImportTaskFileResult",
    # ai
    "ChatRequest",
    "ChatMessage",
    "SessionSummary",
    # dashboard
    "DashboardMetrics",
    "QuestionRank",
    "UnitRank",
    "DailyTrendPoint",
    # settlement
    "FAQRecommendation",
    "FAQPublished",
    "FAQReviewRequest",
    "FAQManualCreate",
    "KnowledgeGapOut",
    "KnowledgeGapUpdate",
    "KnowledgeGapCreateUnitRequest",
]