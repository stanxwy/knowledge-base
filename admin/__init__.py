"""KBMS admin — Python package.

Independent FastAPI service that lives next to ``app/`` (the existing RAG engine)
and shares the repository but not the process. Run with::

    cd admin
    alembic upgrade head
    python -m admin.scripts.create_superuser
    uvicorn admin.main:app --port 8002
"""
__version__ = "0.1.0"