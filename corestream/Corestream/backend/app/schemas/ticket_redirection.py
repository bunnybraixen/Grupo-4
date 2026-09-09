"""
Schemas Pydantic para la redirección de tickets (CS-020).

Define los modelos de datos para las solicitudes y respuestas
de la API de redirección de tickets.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TicketRedirectionRequest(BaseModel):
    """Schema para la solicitud de redirección de ticket."""
    
    to_user_id: UUID = Field(..., description="ID del usuario que recibirá el ticket")
    justification: str = Field(
        ..., 
        min_length=10,
        max_length=1000,
        description="Justificación obligatoria del traspaso (mínimo 10 caracteres)"
    )


class TicketRedirectionResponse(BaseModel):
    """Schema para la respuesta de redirección de ticket."""
    
    ticket_id: UUID = Field(..., description="ID del ticket redirigido")
    from_user_id: UUID = Field(..., description="ID del usuario que redirigió el ticket")
    to_user_id: UUID = Field(..., description="ID del usuario que recibió el ticket")
    justification: str = Field(..., description="Justificación del traspaso")
    new_status: str = Field(..., description="Nuevo estado del ticket después de la redirección")
    redirected_at: datetime = Field(..., description="Fecha y hora de la redirección")


class TeamMemberResponse(BaseModel):
    """Schema para la respuesta de miembros del equipo."""
    
    id: UUID = Field(..., description="ID del usuario")
    full_name: str = Field(..., description="Nombre completo del usuario")
    email: str = Field(..., description="Email del usuario")
    role: str = Field(..., description="Rol del usuario en el sistema")


class TicketEventResponse(BaseModel):
    """Schema para la respuesta de eventos de ticket."""
    
    id: UUID = Field(..., description="ID del evento")
    ticket_id: UUID = Field(..., description="ID del ticket asociado")
    user_id: Optional[UUID] = Field(None, description="ID del usuario que realizó el evento")
    event_type: str = Field(..., description="Tipo de evento")
    detail: Optional[dict] = Field(None, description="Detalles adicionales del evento")
    from_user_id: Optional[UUID] = Field(None, description="ID del usuario origen (en redirecciones)")
    to_user_id: Optional[UUID] = Field(None, description="ID del usuario destino (en redirecciones)")
    created_at: datetime = Field(..., description="Fecha y hora del evento")


class WebSocketNotification(BaseModel):
    """Schema para notificaciones WebSocket."""
    
    type: str = Field(..., description="Tipo de notificación")
    data: dict = Field(..., description="Datos de la notificación")
    timestamp: datetime = Field(..., description="Timestamp de la notificación")


class TicketAssignedNotification(BaseModel):
    """Schema para notificación de ticket asignado."""
    
    ticket_id: UUID = Field(..., description="ID del ticket asignado")
    ticket_title: str = Field(..., description="Título del ticket")
    ticket_status: str = Field(..., description="Estado del ticket")
    epic_id: UUID = Field(..., description="ID de la épica")
    epic_title: Optional[str] = Field(None, description="Título de la épica")
    from_user_id: UUID = Field(..., description="ID del usuario que redirigió")
    justification: str = Field(..., description="Justificación del traspaso")
    redirected_at: datetime = Field(..., description="Fecha de redirección")
    highlight: bool = Field(True, description="Indica si debe resaltarse en el workbench")


class TicketStatusChangedNotification(BaseModel):
    """Schema para notificación de cambio de estado de ticket."""
    
    ticket_id: UUID = Field(..., description="ID del ticket")
    from_status: str = Field(..., description="Estado anterior")
    to_status: str = Field(..., description="Estado nuevo")
    reason: Optional[str] = Field(None, description="Razón del cambio")


class TimerSyncNotification(BaseModel):
    """Schema para notificación de sincronización de timer."""
    
    ticket_id: UUID = Field(..., description="ID del ticket")
    action: str = Field(..., description="Acción del timer (start, pause, sync)")
    time_spent_seconds: int = Field(..., description="Tiempo acumulado en segundos")
    timestamp: datetime = Field(..., description="Timestamp de la sincronización")
