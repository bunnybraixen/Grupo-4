"""
Schema de respuesta del historial de eventos de un ticket
(GET /tickets/{id}/events).
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.user import UserResponse


class TicketEventResponse(BaseModel):
    """Schema para la respuesta de eventos de ticket."""
    
    id: UUID = Field(..., description="ID del evento")
    ticket_id: UUID = Field(..., description="ID del ticket asociado")
    user_id: Optional[UUID] = Field(None, description="ID del usuario que realizó el evento")
    # WEB-11: autor del evento. Se incluye para que el historial pueda mostrar
    # quién hizo cada acción sin que el frontend tenga que cruzar ids (un
    # DEVELOPER no puede listar todos los usuarios).
    user: Optional[UserResponse] = Field(None, description="Usuario autor del evento")
    event_type: str = Field(..., description="Tipo de evento")
    detail: Optional[dict] = Field(None, description="Detalles adicionales del evento")
    from_user_id: Optional[UUID] = Field(None, description="ID del usuario origen (en redirecciones)")
    to_user_id: Optional[UUID] = Field(None, description="ID del usuario destino (en redirecciones)")
    created_at: datetime = Field(..., description="Fecha y hora del evento")

    # Sin `from_attributes`, `TicketEventResponse.from_orm(...)` revienta en
    # Pydantic v2 (PydanticUserError) y el endpoint de historial devolvía 500.
    model_config = {"from_attributes": True}
