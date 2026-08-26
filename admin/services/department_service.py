"""Department service — tree CRUD."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from admin.core import exceptions as exc
from admin.domain.department import Department
from admin.domain.user import User
from admin.schemas.org import DepartmentCreate, DepartmentNode, DepartmentUpdate


async def _assert_user_exists(db: AsyncSession, user_id: int | None) -> None:
    if user_id is None:
        return
    exists = (await db.execute(select(User.id).where(User.id == user_id))).scalar_one_or_none()
    if exists is None:
        raise exc.NotFoundError(f"leader user {user_id} 不存在")


async def _assert_no_cycle(db: AsyncSession, dept_id: int, new_parent_id: int | None) -> None:
    if new_parent_id is None:
        return
    if dept_id == new_parent_id:
        raise exc.ValidationError("部门的 parent_id 不能是自己")
    # walk up the proposed chain — if we hit dept_id, that's a cycle.
    cursor = new_parent_id
    seen: set[int] = set()
    while cursor is not None:
        if cursor == dept_id:
            raise exc.ValidationError("parent_id 不能指向自己的子孙节点")
        if cursor in seen:
            break  # safety net against pre-existing cycles
        seen.add(cursor)
        row = (await db.execute(select(Department.parent_id).where(Department.id == cursor))).scalar_one_or_none()
        cursor = row


async def create_department(db: AsyncSession, payload: DepartmentCreate) -> Department:
    await _assert_user_exists(db, payload.leader_id)
    if payload.parent_id is not None:
        parent = (await db.execute(select(Department.id).where(Department.id == payload.parent_id))).scalar_one_or_none()
        if parent is None:
            raise exc.NotFoundError(f"parent department {payload.parent_id} 不存在")
    dept = Department(
        name=payload.name,
        parent_id=payload.parent_id,
        leader_id=payload.leader_id,
        sort_order=payload.sort_order,
    )
    db.add(dept)
    await db.commit()
    await db.refresh(dept)
    return dept


async def update_department(db: AsyncSession, dept_id: int, payload: DepartmentUpdate) -> Department:
    dept = (await db.execute(select(Department).where(Department.id == dept_id))).scalar_one_or_none()
    if dept is None:
        raise exc.NotFoundError(f"department {dept_id} 不存在")
    data = payload.model_dump(exclude_unset=True)
    if "parent_id" in data:
        await _assert_no_cycle(db, dept_id, data["parent_id"])
    if "leader_id" in data:
        await _assert_user_exists(db, data["leader_id"])
    for k, v in data.items():
        setattr(dept, k, v)
    await db.commit()
    await db.refresh(dept)
    return dept


async def delete_department(db: AsyncSession, dept_id: int) -> None:
    dept = (await db.execute(select(Department).where(Department.id == dept_id))).scalar_one_or_none()
    if dept is None:
        raise exc.NotFoundError(f"department {dept_id} 不存在")
    children = (await db.execute(select(Department.id).where(Department.parent_id == dept_id))).first()
    if children is not None:
        raise exc.ConflictError("该部门存在子部门,无法删除")
    members = (await db.execute(select(User.id).where(User.department_id == dept_id))).first()
    if members is not None:
        raise exc.ConflictError("该部门存在成员,无法删除")
    await db.delete(dept)
    await db.commit()


async def list_all_departments(db: AsyncSession) -> list[Department]:
    stmt = select(Department).order_by(Department.sort_order.asc(), Department.id.asc())
    return list((await db.execute(stmt)).scalars().all())


def build_tree(items: list[Department]) -> list[DepartmentNode]:
    """Materialize a flat list into a forest of DepartmentNode.

    Roots have ``parent_id = None`` (or refer to a missing parent — we tolerate).

    Builds dicts first to avoid triggering SQLAlchemy lazy loads when pydantic
    introspects ``children`` / relationships.
    """
    payload = [
        {
            "id": d.id,
            "name": d.name,
            "parent_id": d.parent_id,
            "leader_id": d.leader_id,
            "sort_order": d.sort_order,
            "created_at": d.created_at,
            "updated_at": d.updated_at,
        }
        for d in items
    ]
    by_id: dict[int, DepartmentNode] = {}
    for entry in payload:
        by_id[entry["id"]] = DepartmentNode.model_validate(entry)
    roots: list[DepartmentNode] = []
    for node in by_id.values():
        pid = node.parent_id
        if pid is None or pid not in by_id:
            roots.append(node)
        else:
            by_id[pid].children.append(node)
    return roots