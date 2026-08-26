"""Data permission engine — see SPEC §5.1.

``check_permissions(user_id, unit_ids)`` is the single source of truth for
"can this user see this unit?" — invoked by the AI chat flow before answering,
and exposed publicly at ``POST /api/knowledge/check-permissions``.
"""
from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from admin.core import exceptions as exc
from admin.domain.department import Department
from admin.domain.knowledge_unit import KnowledgeUnit
from admin.domain.role import Role, UserRole
from admin.domain.unit_permission import (
    TARGET_DEPARTMENT,
    TARGET_GLOBAL,
    TARGET_ROLE,
    TARGET_USER,
    VALID_TARGET_TYPES,
    UnitPermission,
)
from admin.domain.user import User


async def _load_user_identity(db: AsyncSession, user_id: int) -> tuple[int | None, set[int], bool]:
    """Returns (department_id, set_of_role_ids, is_superuser)."""
    stmt = (
        select(User)
        .options(
            selectinload(User.department),
            selectinload(User.role_links).selectinload(UserRole.role),
        )
        .where(User.id == user_id)
    )
    user = (await db.execute(stmt)).scalar_one_or_none()
    if user is None:
        raise exc.NotFoundError(f"user {user_id} 不存在")
    role_ids = {link.role_id for link in user.role_links}
    return user.department_id, role_ids, user.is_superuser


async def _load_rules_for(db: AsyncSession, unit_ids: list[int]) -> dict[int, list[UnitPermission]]:
    if not unit_ids:
        return {}
    stmt = select(UnitPermission).where(UnitPermission.unit_id.in_(unit_ids))
    rows = list((await db.execute(stmt)).scalars().all())
    grouped: dict[int, list[UnitPermission]] = defaultdict(list)
    for r in rows:
        grouped[r.unit_id].append(r)
    return grouped


def _match(rule: UnitPermission, *, department_id: int | None, role_ids: set[int], user_id: int) -> bool:
    if rule.target_type == TARGET_GLOBAL:
        return True
    if rule.target_type == TARGET_DEPARTMENT:
        return department_id is not None and rule.target_id == department_id
    if rule.target_type == TARGET_ROLE:
        return rule.target_id is not None and rule.target_id in role_ids
    if rule.target_type == TARGET_USER:
        return rule.target_id == user_id
    return False


async def check_permissions(db: AsyncSession, user_id: int, unit_ids: list[int]) -> dict:
    """Returns ``{authorized_unit_ids, unauthorized_unit_ids}``.

    Superusers bypass all checks (full access).
    Units with NO rules are treated as denied — SPEC §5.1 default-deny.
    """
    department_id, role_ids, is_superuser = await _load_user_identity(db, user_id)
    if is_superuser:
        return {"authorized_unit_ids": list(unit_ids), "unauthorized_unit_ids": []}

    rules_by_unit = await _load_rules_for(db, unit_ids)

    authorized: list[int] = []
    unauthorized: list[int] = []
    for uid in unit_ids:
        rules = rules_by_unit.get(uid, [])
        if any(_match(r, department_id=department_id, role_ids=role_ids, user_id=user_id) for r in rules):
            authorized.append(uid)
        else:
            unauthorized.append(uid)
    return {"authorized_unit_ids": authorized, "unauthorized_unit_ids": unauthorized}


async def _validate_targets(db: AsyncSession, rules: list[dict]) -> list[dict]:
    """Normalize + validate a list of rule dicts before insertion.

    Returns the list of dicts ready to be turned into ``UnitPermission`` rows.
    """
    cleaned: list[dict] = []
    for r in rules:
        target_type = r["target_type"]
        target_id = r.get("target_id")
        if target_type not in VALID_TARGET_TYPES:
            raise exc.ValidationError(f"不支持的 target_type: {target_type}")
        if target_type == TARGET_GLOBAL:
            target_id = None
        elif target_id is None:
            raise exc.ValidationError(f"target_type={target_type} 必须指定 target_id")

        if target_type == TARGET_DEPARTMENT:
            exists = (await db.execute(select(Department.id).where(Department.id == target_id))).scalar_one_or_none()
            if exists is None:
                raise exc.NotFoundError(f"department {target_id} 不存在")
        elif target_type == TARGET_ROLE:
            exists = (await db.execute(select(Role.id).where(Role.id == target_id))).scalar_one_or_none()
            if exists is None:
                raise exc.NotFoundError(f"role {target_id} 不存在")
        elif target_type == TARGET_USER:
            exists = (await db.execute(select(User.id).where(User.id == target_id))).scalar_one_or_none()
            if exists is None:
                raise exc.NotFoundError(f"user {target_id} 不存在")

        cleaned.append({"target_type": target_type, "target_id": target_id})
    return cleaned


async def replace_unit_permissions(
    db: AsyncSession,
    unit_id: int,
    raw_rules: list[dict],
) -> list[UnitPermission]:
    """Atomically replace the full permission set for a unit.

    Validates target entities exist; de-duplicates by ``(target_type, target_id)``.
    """
    unit = (await db.execute(select(KnowledgeUnit.id).where(KnowledgeUnit.id == unit_id))).scalar_one_or_none()
    if unit is None:
        raise exc.NotFoundError(f"knowledge unit {unit_id} 不存在")

    cleaned = await _validate_targets(db, raw_rules)

    # Wipe existing — flush before bulk-insert so the unique index is free.
    existing = list((await db.execute(
        select(UnitPermission).where(UnitPermission.unit_id == unit_id)
    )).scalars().all())
    for row in existing:
        await db.delete(row)
    await db.flush()

    # Insert new
    seen: set[tuple[str, int | None]] = set()
    inserted: list[UnitPermission] = []
    for r in cleaned:
        key = (r["target_type"], r["target_id"])
        if key in seen:
            continue
        seen.add(key)
        perm = UnitPermission(unit_id=unit_id, target_type=r["target_type"], target_id=r["target_id"])
        db.add(perm)
        inserted.append(perm)

    await db.commit()
    # refresh from DB to read auto-generated ids / created_at
    for p in inserted:
        await db.refresh(p)
    return inserted


async def list_unit_permissions(db: AsyncSession, unit_id: int) -> list[UnitPermission]:
    stmt = select(UnitPermission).where(UnitPermission.unit_id == unit_id).order_by(UnitPermission.id.asc())
    return list((await db.execute(stmt)).scalars().all())