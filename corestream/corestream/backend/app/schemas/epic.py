"""
Esquemas de validación para operaciones relacionadas con épicas.
Una épica es un conjunto de tickets relacionados dentro de una aplicación.

CAMBIOS REALIZADOS:
- Se integraron validadores de campo (field_validators) para asegurar datos limpios.
- Se añadió EpicReorder para la persistencia del Drag & Drop (CS-012).
- Se incluyeron campos de progreso y estadísticas en EpicResponse (CS-010).
- Se utiliza ConfigDict para la compatibilidad con SQLAlchemy (from_attributes).
"""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.ticket import TicketResponse


class EpicCreate(BaseModel):
    """
    Esquema para crear una nueva épica en el sistema.
    Una épica agrupa múltiples tickets relacionados por un objetivo común.
    """
    title: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=10_000)
    application_id: UUID
    due_date: Optional[datetime] = None

    @field_validator("title")
    @classmethod
    def validate_title_not_empty(cls, v: str) -> str:
        """Valida que el título de la épica no esté vacío o solo contenga espacios."""
        if not v or not v.strip():
            raise ValueError("El título de la épica no puede estar vacío")
        return v.strip()

    @field_validator("due_date", mode="after")
    @classmethod
    def ensure_due_date_utc(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v


class EpicUpdate(BaseModel):
    """
    Esquema para actualizar datos de una épica existente.
    Todos los campos son opcionales para permitir actualizaciones parciales.
    NOTA: application_id no se permite modificar para mantener integridad referencial.
    """
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=10_000)
    order_index: Optional[int] = None
    due_date: Optional[datetime] = None
    is_collapsed: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def validate_title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Valida que el título, si se proporciona, no esté vacío."""
        if v is not None and not v.strip():
            raise ValueError("El título de la épica no puede estar vacío")
        return v.strip() if v else v

    @field_validator("order_index")
    @classmethod
    def validate_order_index(cls, v: Optional[int]) -> Optional[int]:
        """Valida que el índice de orden sea un número no negativo."""
        if v is not None and v < 0:
            raise ValueError("El índice de orden no puede ser negativo")
        return v

    @field_validator("due_date", mode="after")
    @classmethod
    def ensure_due_date_utc(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v


class EpicReorder(BaseModel):
    """
    Esquema para reordenar épicas dentro de una aplicación (CS-012).
    """
    new_index: int

    @field_validator("new_index")
    @classmethod
    def validate_new_index(cls, v: int) -> int:
        """Valida que el nuevo índice sea no negativo."""
        if v < 0:
            raise ValueError("El nuevo índice no puede ser negativo")
        return v


class EpicResponse(BaseModel):
    """
    Esquema de respuesta al consultar datos de una épica.
    Incluye información de progreso y estadísticas de tickets (CS-010).
    """
    id: UUID
    title: str
    description: Optional[str] = None
    application_id: UUID
    order_index: int
    due_date: Optional[datetime] = None
    is_collapsed: bool
    created_at: datetime
    
    # Campos calculados para la UI (CS-010)
    progress: float = 0.0
    total_tickets: int = 0
    completed_tickets: int = 0

    tickets: List[TicketResponse] = []

    # Configuración para permitir la lectura desde modelos de SQLAlchemy
    model_config = ConfigDict(from_attributes=True)

    @field_validator("progress")
    @classmethod
    def validate_progress_range(cls, v: float) -> float:
        """Valida que el progreso esté en el rango de 0 a 100."""
        if not 0 <= v <= 100:
            raise ValueError("El progreso debe estar entre 0 y 100")
        return v