"""Compat layer for legacy app.core imports.

This project exposes database and auth utilities under app.database and
app.middleware. Some older modules still import from app.core.*, so we expose
minimal compatibility shims here instead of duplicating logic.
"""

from app.database import Base, async_session_maker, engine, get_db, get_session_maker
from app.middleware.auth import get_current_user, require_role

__all__ = [
    "Base",
    "async_session_maker",
    "engine",
    "get_db",
    "get_session_maker",
    "get_current_user",
    "require_role",
]
