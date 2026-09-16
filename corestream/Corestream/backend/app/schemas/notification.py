# Esquemas de validación para operaciones relacionadas con notificaciones
# Las notificaciones informan a los usuarios sobre cambios relevantes en el sistema

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator


class NotificationResponse(BaseModel):
    """
    Esquema de respuesta al consultar una notificación.
    Contiene información sobre eventos importantes del sistema.
    
    Atributos:
        id: Identificador único en formato UUID
        user_id: UUID del usuario destinatario de la notificación
        title: Título breve de la notificación
        message: Mensaje detallado de la notificación
        type: Tipo de notificación (TICKET_ASSIGNED, TICKET_COMPLETED, QUESTION_ASKED, REDIRECTED, etc.)
        is_read: Indica si la notificación ha sido leída
        ticket_id: UUID del ticket relacionado (opcional)
        created_at: Fecha y hora de creación de la notificación
    """
    id: UUID
    user_id: UUID
    title: str
    message: str
    type: str
    is_read: bool
    ticket_id: Optional[UUID] = None
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("type")
    @classmethod
    def validate_notification_type(cls, v: str) -> str:
        """
        Valida que el tipo de notificación sea válido.
        
        Args:
            v: Tipo de notificación a validar
            
        Returns:
            El tipo validado
            
        Raises:
            ValueError: Si el tipo no es válido
        """
        valid_types = {
            "TICKET_ASSIGNED",
            "TICKET_COMPLETED",
            "TICKET_BLOCKED",
            "QUESTION_ASKED",
            "REDIRECTED",
            "COMMENT_ADDED",
            "DEADLINE_APPROACHING",
            "APPLICATION_UPDATED",
        }
        if v.upper() not in valid_types:
            raise ValueError(f"El tipo de notificación debe ser uno de: {', '.join(valid_types)}")
        return v.upper()


class NotificationMarkRead(BaseModel):
    """
    Esquema para marcar múltiples notificaciones como leídas.
    Permite actualizaciones eficientes en lote.
    
    Atributos:
        notification_ids: Lista de UUIDs de notificaciones a marcar como leídas
    """
    notification_ids: list[UUID]

    @field_validator("notification_ids")
    @classmethod
    def validate_notification_ids_not_empty(cls, v: list[UUID]) -> list[UUID]:
        """
        Valida que la lista de IDs de notificaciones no esté vacía.
        
        Args:
            v: Lista de IDs a validar
            
        Returns:
            La lista validada
            
        Raises:
            ValueError: Si la lista está vacía
        """
        if not v or len(v) == 0:
            raise ValueError("Debe proporcionar al menos una notificación para marcar como leída")
        return v
