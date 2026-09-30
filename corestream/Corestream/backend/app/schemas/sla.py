"""
Esquemas de SLA (Service Level Agreement) a nivel de TICKET.

El SLA se configura por prioridad/severidad (solo ADMIN) y se calcula sobre
cada ticket: objetivos de respuesta y resolución, tiempo transcurrido/restante
y detección de incumplimientos y alertas.
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.ticket import TicketPriority


class SLAConfigUpdate(BaseModel):
    """
    Esquema para que un ADMIN ajuste los tiempos objetivo de una prioridad.

    Todos los campos son opcionales: solo se actualiza lo enviado.
    """

    response_minutes: Optional[int] = Field(
        None, ge=1, le=525600, description="Minutos objetivo para la primera respuesta"
    )
    resolution_minutes: Optional[int] = Field(
        None, ge=1, le=525600, description="Minutos objetivo para resolver el ticket"
    )
    warn_threshold_percent: Optional[int] = Field(
        None,
        ge=1,
        le=100,
        description="% del tiempo objetivo a partir del cual se alerta 'próximo a vencer'",
    )
    is_active: Optional[bool] = Field(None, description="Activa/desactiva la regla")


class SLAConfigResponse(BaseModel):
    """Regla de SLA configurada para una prioridad de ticket."""

    id: Optional[UUID] = None
    priority: str
    response_minutes: int
    resolution_minutes: int
    warn_threshold_percent: int = 80
    is_active: bool = True
    is_default: bool = False  # True si la fila se creó a partir de los valores por defecto
    updated_at: Optional[str] = None

    model_config = {"from_attributes": True}


class SLASummary(BaseModel):
    """Métricas agregadas de SLA (usadas por Sprint y por proyecto)."""

    total: int = 0
    on_track: int = 0
    at_risk: int = 0
    breached: int = 0
    met: int = 0
    compliance_rate: float = 0.0
    breach_rate: float = 0.0


class TicketSLAStatus(BaseModel):
    """
    Estado de SLA calculado de un ticket individual.

    `state`, `response_state` y `resolution_state` pueden ser:
        ON_TRACK (en plazo), AT_RISK (próximo a vencer), BREACHED (incumplido),
        MET (cumplido) o NOT_APPLICABLE.
    """

    ticket_id: str
    title: Optional[str] = None
    ticket_status: Optional[str] = None
    epic_title: Optional[str] = None
    sprint_id: Optional[str] = None
    sprint_name: Optional[str] = None
    assignee_id: Optional[str] = None
    due_date: Optional[str] = None

    priority: str
    response_target_minutes: int = 0
    resolution_target_minutes: int = 0
    warn_threshold_percent: int = 80

    created_at: Optional[str] = None
    first_response_at: Optional[str] = None
    response_due_at: Optional[str] = None
    resolution_due_at: Optional[str] = None

    response_elapsed_minutes: int = 0
    resolution_elapsed_minutes: int = 0
    response_remaining_minutes: int = 0
    resolution_remaining_minutes: int = 0

    response_state: str = "ON_TRACK"
    resolution_state: str = "ON_TRACK"
    state: str = "ON_TRACK"

    is_breached: bool = False
    is_at_risk: bool = False
    is_compliant: bool = True
    is_resolved: bool = False

    next_deadline_at: Optional[str] = None
    next_deadline_metric: Optional[str] = None
    minutes_to_next_deadline: Optional[int] = None

    model_config = {"from_attributes": True}


class SLAStatusListResponse(BaseModel):
    """Listado de estados de SLA junto con el resumen agregado."""

    summary: SLASummary
    statuses: list[TicketSLAStatus] = []


class SLAConfigListResponse(BaseModel):
    """Configuración completa de SLA (una regla por prioridad)."""

    configs: list[SLAConfigResponse] = []

    @field_validator("configs")
    @classmethod
    def validate_priorities(cls, value: list[SLAConfigResponse]) -> list[SLAConfigResponse]:
        """Documenta el orden esperado de prioridades en la respuesta."""
        order = {p.value: i for i, p in enumerate(TicketPriority)}
        return sorted(value, key=lambda item: order.get(item.priority, 99))
