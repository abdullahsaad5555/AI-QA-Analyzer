# app/models/_common.py

from app.core.config import settings

TABLE_ARGS = {"schema": settings.DB_SCHEMA} if settings.DB_SCHEMA else {}


def fk(table_name: str, column_name: str = "id") -> str:
    """
    Build a ForeignKey target string that works for both:
    - PostgreSQL with schema, e.g. "public.users.id"
    - SQLite without schema, e.g. "users.id"
    """
    if settings.DB_SCHEMA:
        return f"{settings.DB_SCHEMA}.{table_name}.{column_name}"
    return f"{table_name}.{column_name}"
