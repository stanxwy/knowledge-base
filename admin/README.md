# KBMS Admin Backend

FastAPI service for the Knowledge Base Management System (KBMS). Lives next to the
existing RAG engine in `../app/` and talks to it over HTTP.

## Phase 1 scope (this commit)
- JWT auth (`/api/auth/{login,refresh,logout,me}`)
- Postgres + SQLAlchemy async + Alembic migrations
- Built-in roles & permissions seeded by `0002_seed`
- Initial superuser created by `python -m admin.scripts.create_superuser`

## Quick start
```bash
# 1. Install
pip install -e .            # or uv sync

# 2. Configure
cp .env.example .env        # then edit DATABASE_URL / JWT_SECRET

# 3. Migrate
cd ..
alembic upgrade head

# 4. Create superuser
python -m admin.scripts.create_superuser

# 5. Run
uvicorn admin.main:app --port 8002 --reload
```

## Endpoints (Phase 1)
| Method | Path             | Auth | Purpose                       |
|--------|------------------|------|-------------------------------|
| GET    | `/health`        | no   | Liveness probe                |
| POST   | `/api/auth/login`| no   | Username + password → tokens  |
| POST   | `/api/auth/refresh` | no | Exchange refresh_token → tokens |
| POST   | `/api/auth/logout` | no  | Stateless logout (client-side) |
| GET    | `/api/auth/me`   | yes  | Current user + roles + perms  |
```

## Directory layout
```
admin/
├── api/             FastAPI routers + deps
├── core/            settings, security, exceptions, logging
├── db/              SQLAlchemy base + Alembic
├── domain/          ORM models
├── schemas/         Pydantic request/response
├── services/        Business logic
├── scripts/         Operational scripts (create_superuser, …)
└── main.py          FastAPI entrypoint
```