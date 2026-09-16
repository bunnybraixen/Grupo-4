"""
Modelo de Notificación para CoreStream.
Define la estructura de las notificaciones que comunican eventos importantes a los usuarios.
Las notificaciones permiten mantener a los usuarios informados sin sobrecargarlos.
"""

from datetime import datetime
from enum import Enum
from uuid import UUID as PyUUID
from sqlalchemy import String, Boolean, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM

from .base import Base, BaseEntity


class NotificationType(str, Enum):
    """
    Enumeración de tipos de notificaciones en CoreStream.
    
    Tipos:
        ASSIGNMENT: Notificación de asignación de ticket
        QUESTION: Notificación de pregunta en ticket
        REDIRECT: Notificación de redirección de ticket
        COMPLETION: Notificación de completitud de ticket
        SYSTEM: Notificación del sistema general
    """
    ASSIGNMENT = "ASSIGNMENT"
    QUESTION = "QUESTION"
    REDIRECT = "REDIRECT"
    COMPLETION = "COMPLETION"
    SYSTEM = "SYSTEM"


class Notification(Base, BaseEntity):
    """
    Entidad que representa una Notificación en CoreStream.
    
    Las notificaciones informan a los usuarios sobre eventos importantes en tickets,
    cambios de estado, asignaciones y redirecciones de manera centralizada.
    
    Atributos principales:
        user_id: Usuario destinatario de la notificación
        title: Título corto de la notificación
        message: Contenido detallado de la notificación
        type: Tipo de notificación
        is_read: Indicador si la notificación ha sido leída
        ticket_id: Referencia al ticket relacionado (puede estar ausente)
    
    Relaciones:
        user: Usuario destinatario de la notificación
        ticket: Ticket asociado con la notificación (opcional)
    
    Índices:
        user_id: Búsqueda rápida de notificaciones por usuario
        is_read: Filtrado de notificaciones leídas/no leídas
        ticket_id: Búsqueda de notificaciones por ticket
    
    Notas:
        El campo is_read permite implementar funcionalidad de "marcar como leído"
        para mejorar la experiencia del usuario y no bombardearlo con notificaciones.
    """
    
    __tablename__ = "notifications"
    
    # Clave foránea al usuario destinatario
    user_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Referencia al usuario destinatario de esta notificación"
    )
    
    # Título corto de la notificación
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Título corto y descriptivo de la notificación para vista rápida"
    )
    
    # Contenido detallado de la notificación
    message: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
        doc="Mensaje detallado con contexto e información sobre la notificación"
    )
    
    # Tipo de notificación
    type: Mapped[NotificationType] = mapped_column(
        ENUM(NotificationType, name="notification_type_enum"),
        nullable=False,
        doc="Tipo de notificación: ASSIGNMENT, QUESTION, REDIRECT, COMPLETION, SYSTEM"
    )
    
    # Indicador si la notificación ha sido leída
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        doc="Indicador si el usuario ha leído esta notificación"
    )
    
    # Clave foránea al ticket asociado (opcional)
    ticket_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tickets.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="Referencia al ticket relacionado con esta notificación (puede no existir)"
    )
    
    # Relaciones hacia otras entidades
    
    user = relationship(
        "User",
        back_populates="notifications",
        foreign_keys=[user_id],
        doc="Usuario destinatario de esta notificación"
    )
    
    ticket = relationship(
        "Ticket",
        foreign_keys=[ticket_id],
        doc="Ticket asociado con esta notificación"
    )
    
    __table_args__ = (
        Index('ix_notifications_user_id', 'user_id'),
        Index('ix_notifications_is_read', 'is_read'),
        Index('ix_notifications_ticket_id', 'ticket_id'),
    )
