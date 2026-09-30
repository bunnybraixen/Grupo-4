"""
Esquemas de Sprint (planificación temporal) para CoreStream.

Un Sprint es independiente de la Épica: agrupa TEMPORALMENTE tickets de
cualquier épica del proyecto. Los esquemas exponen, además del CRUD, las
métricas de avance, Velocity y SLA agregado que consumen el Builder, el
Workbench y el Command Center.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.sprint import SprintStatus
from app.schemas.sla import SLASummary
from app.schemas.ticket import TicketResponse


class SprintCreate(BaseModel):
    """
    Esquema para crear un Sprint.

    Atributos:
        name: Nombre del Sprint (ej: "Sprint 12")
        application_id: Proyecto al que pertenece el Sprint
        start_date: Fecha de inicio del período de trabajo
        end_date: Fecha de término del período de trabajo
        goal: Objetivo del Sprint (opcional)
        status: Estado inicial (por defecto PLANNED)
    """

    name: str
    application_id: UUID
    start_date: datetime
    end_date: datetime
    goal: Optional[str] = Field(None, max_length=1000)
    status: SprintStatus = SprintStatus.PLANNED

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """El nombre del Sprint no puede estar vacío."""
        if not value or not value.strip():
            raise ValueError("El nombre del Sprint no puede estar vacío")
        return value.strip()

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, value: datetime, info) -> datetime:
        """La fecha de término no puede ser anterior a la de inicio."""
        start = info.data.get("start_date")
        if start is not None and value < start:
            raise ValueError("La fecha de término no puede ser anterior a la de inicio")
        return value


class SprintUpdate(BaseModel):
    """Esquema para editar un Sprint (actualización parcial)."""

    name: Optional[str] = None
    goal: Optional[str] = Field(None, max_length=1000)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[SprintStatus] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        """Si se envía nombre, no puede estar vacío."""
        if value is not None and not value.strip():
            raise ValueError("El nombre del Sprint no puede estar vacío")
        return value.strip() if value else value


class SprintTicketAssignment(BaseModel):
    """Tickets EXISTENTES que se asocian a un Sprint (sprint_id)."""

    ticket_ids: list[UUID] = Field(..., min_length=1)

    @field_validator("ticket_ids")
    @classmethod
    def validate_ticket_ids(cls, value: list[UUID]) -> list[UUID]:
        """Sin duplicados."""
        return list(dict.fromkeys(value))


class SprintTicketStoryPoints(BaseModel):
    """Puntos de esfuerzo (story points) de un ticket, base de la Velocity."""

    story_points: int = Field(..., ge=0, le=1000)


class SprintBoardColumn(BaseModel):
    """Columna del tablero (reutiliza el Kanban existente) agrupada por estado."""

    status: str
    label: str
    tickets: list[TicketResponse] = []


class SprintResponse(BaseModel):
    """
    Sprint con sus métricas de avance, Velocity y SLA agregado.

    `tickets` solo se rellena en el detalle (`GET /sprints/{id}`).
    """

    id: UUID
    name: str
    goal: Optional[str] = None
    application_id: UUID
    application_name: Optional[str] = None
    start_date: datetime
    end_date: datetime
    status: str
    velocity: float = 0.0
    created_at: Optional[datetime] = None

    # Resumen de tickets
    total_tickets: int = 0
    pending_tickets: int = 0
    in_progress_tickets: int = 0
    completed_tickets: int = 0
    blocked_tickets: int = 0
    redirected_tickets: int = 0

    # Avance y esfuerzo
    progress: float = 0.0
    story_points_total: int = 0
    story_points_completed: int = 0

    # Ventana temporal
    duration_days: int = 0
    days_remaining: int = 0
    is_overdue: bool = False

    # SLA agregado del Sprint
    sla: SLASummary = Field(default_factory=SLASummary)

    # Detalle (opcional)
    tickets: list[TicketResponse] = []
    board: list[SprintBoardColumn] = []

    model_config = {"from_attributes": True}


class SprintSummaryResponse(BaseModel):
    """Resumen de un Sprint: conteos por estado, Velocity y SLA agregado."""

    sprint_id: UUID
    sprint_name: str
    status: str
    start_date: datetime
    end_date: datetime
    duration_days: int = 0
    days_remaining: int = 0
    is_overdue: bool = False
    progress: float = 0.0
    velocity: float = 0.0
    story_points_total: int = 0
    story_points_completed: int = 0
    total_tickets: int = 0
    pending_tickets: int = 0
    in_progress_tickets: int = 0
    completed_tickets: int = 0
    blocked_tickets: int = 0
    redirected_tickets: int = 0
    by_status: dict[str, int] = {}
    sla: SLASummary = Field(default_factory=SLASummary)


class SprintVelocityResponse(BaseModel):
    """Resultado del cierre de Sprint (cálculo automático de Velocity)."""

    sprint_id: UUID
    sprint_name: str
    status: str
    velocity: float
    story_points_completed: int
    completed_tickets: int
    message: str
