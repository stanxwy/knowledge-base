"""Department router."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from admin.api.deps import require_permission
from admin.db.base import get_db
from admin.domain.user import User
from admin.schemas.org import (
    DepartmentCreate,
    DepartmentNode,
    DepartmentOut,
    DepartmentUpdate,
)
from admin.services import department_service

router = APIRouter(prefix="/api/org/departments", tags=["org-departments"])


@router.get("", response_model=list[DepartmentNode])
async def list_departments(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("org:read")),
) -> list[DepartmentNode]:
    flat = await department_service.list_all_departments(db)
    return department_service.build_tree(flat)


@router.post("", response_model=DepartmentOut, status_code=201)
async def create_department(
    payload: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("org:write")),
) -> DepartmentOut:
    dept = await department_service.create_department(db, payload)
    return DepartmentOut.model_validate(dept)


@router.put("/{dept_id}", response_model=DepartmentOut)
async def update_department(
    dept_id: int,
    payload: DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("org:write")),
) -> DepartmentOut:
    dept = await department_service.update_department(db, dept_id, payload)
    return DepartmentOut.model_validate(dept)


@router.delete("/{dept_id}", status_code=204)
async def delete_department(
    dept_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_permission("org:write")),
) -> None:
    await department_service.delete_department(db, dept_id)