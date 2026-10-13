"""
Esquemas Pydantic para los tickets operacionales de Soporte.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class OperationalTicketCreate(BaseModel):
    """Alta de ticket operacional: título + problema (obligatorios)."""

    title: str = Field(..., min_length=3, max_length=255)
    problem: str = Field(..., min_length=10)


class OperationalTicketResolve(BaseModel):
    """Resolución (solo ADMIN/GROUP_LEADER): bloque de cambios realizados."""

    resolution_notes: str = Field(..., min_length=10)


class OperationalTicketUser(BaseModel):
    """Autor o resolutor del ticket (resumen mínimo para la lista)."""

    id: UUID
    full_name: str
    email: str


class OperationalTicketResponse(BaseModel):
    id: UUID
    title: str
    problem: str
    status: str
    timer_started_at: datetime
    resolved_at: Optional[datetime] = None
    elapsed_seconds: int
    current_elapsed_seconds: int
    resolution_notes: Optional[str] = None
    created_by: Optional[OperationalTicketUser] = None
    resolved_by: Optional[OperationalTicketUser] = None
    created_at: datetime

    class Config:
        from_attributes = True
