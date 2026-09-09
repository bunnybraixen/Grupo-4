"""
Routers del módulo de CoreStream.

Este paquete contiene todos los routers para los endpoints REST de CoreStream.
"""

from . import (
    analytics,
    applications,
    auth,
    documents,
    epics,
    incidents,
    meetings,
    notifications,
    subtasks,
    support_tickets,
    ticket_redirection,
    tickets,
    uploads,
    users,
    websocket,
)

__all__ = [
    "auth",
    "users",
    "applications",
    "epics",
    "tickets",
    "subtasks",
    "analytics",
    "documents",
    "notifications",
    "websocket",
    "ticket_redirection",
    "uploads",
    "support_tickets",
    "incidents",
    "meetings",
]
