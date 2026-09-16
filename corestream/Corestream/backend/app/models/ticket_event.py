"""
Modelo de Evento de Ticket para CoreStream.
Define la estructura de los eventos que registran cambios, interacciones y auditoría de tickets.
Este modelo es crítico para análisis, seguimiento de historial y trazabilidad de cambios.
"""

from datetime import datetime
from enum import Enum
from uuid import UUID as PyUUID
from sqlalchemy import String, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSON

from .base import Base, BaseEntity


class TicketEventType(str, Enum):
    """
    Enumeración de tipos de eventos que pueden ocurrir en un ticket.
    
    Tipos de eventos:
        CREATED: Evento de creación del ticket
        ASSIGNED: Evento de asignación del ticket a un usuario
        STATUS_CHANGED: Evento de cambio de estado del ticket
        QUESTION_RAISED: Evento de pregunta formulada sobre el ticket
        QUESTION_RESOLVED: Evento de resolución de una pregunta
        REDIRECTED: Evento de redirección a otro usuario
        COMPLETED: Evento de completitud del ticket
        COMMENT: Evento de comentario en el ticket
        TIMER_START: Evento de inicio de seguimiento de tiempo
        TIMER_PAUSE: Evento de pausa de seguimiento de tiempo
    """
    CREATED = "CREATED"
    ASSIGNED = "ASSIGNED"
    STATUS_CHANGED = "STATUS_CHANGED"
    QUESTION_RAISED = "QUESTION_RAISED"
    QUESTION_RESOLVED = "QUESTION_RESOLVED"
    REDIRECTED = "REDIRECTED"
    COMPLETED = "COMPLETED"
    COMMENT = "COMMENT"
    TIMER_START = "TIMER_START"
    TIMER_PAUSE = "TIMER_PAUSE"


class TicketEvent(Base, BaseEntity):
    """
    Entidad que representa un Evento de Ticket en CoreStream.
    
    Los eventos registran todos los cambios, comentarios e interacciones en un ticket.
    Este modelo es fundamental para auditoría, análisis y reconstrucción del historial.
    
    Atributos principales:
        ticket_id: Referencia al ticket asociado
        user_id: Usuario que generó el evento
        event_type: Tipo de evento que ocurrió
        detail: Información JSON/texto adicional sobre el evento
        from_user_id: Usuario origen en redirecciones (opcional)
        to_user_id: Usuario destino en redirecciones (opcional)
    
    Relaciones:
        ticket: Ticket al que pertenece el evento
        user: Usuario que generó el evento
        from_user: Usuario origen en evento de redirección
        to_user: Usuario destino en evento de redirección
    
    Índices:
        ticket_id: Búsqueda rápida de eventos por ticket
        user_id: Búsqueda de eventos por usuario
        event_type: Filtrado por tipo de evento
        created_at: Ordenamiento por fecha
    
    Notas:
        Este modelo es crítico para análisis de velocidad, métricas de equipo
        y generación de reportes analíticos sobre rendimiento del proyecto.
    """
    
    __tablename__ = "ticket_events"
    
    # Clave foránea al ticket asociado
    ticket_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Referencia al ticket en el que ocurrió el evento"
    )
    
    # Clave foránea al usuario que generó el evento
    user_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Referencia al usuario que generó o causó el evento"
    )
    
    # Tipo de evento que ocurrió
    event_type: Mapped[TicketEventType] = mapped_column(
        ENUM(TicketEventType, name="ticket_event_type_enum"),
        nullable=False,
        index=True,
        doc="Tipo de evento: CREATED, ASSIGNED, STATUS_CHANGED, COMMENT, etc."
    )
    
    # Información adicional sobre el evento en formato JSON
    detail: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        doc="Datos JSON adicionales del evento, como: valores anteriores/nuevos, contenido de comentario"
    )
    
    # Usuario origen en eventos de redirección
    from_user_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        doc="Usuario origen en eventos de redirección o transferencia de responsabilidad"
    )
    
    # Usuario destino en eventos de redirección
    to_user_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        doc="Usuario destino en eventos de redirección o transferencia de responsabilidad"
    )
    
    # Relaciones hacia otras entidades
    
    ticket = relationship(
        "Ticket",
        back_populates="events",
        foreign_keys=[ticket_id],
        doc="Ticket al que pertenece este evento"
    )
    
    user = relationship(
        "User",
        back_populates="events",
        foreign_keys=[user_id],
        doc="Usuario que generó este evento"
    )
    
    from_user = relationship(
        "User",
        foreign_keys=[from_user_id],
        doc="Usuario origen en evento de redirección"
    )
    
    to_user = relationship(
        "User",
        foreign_keys=[to_user_id],
        doc="Usuario destino en evento de redirección"
    )
    
    __table_args__ = (
        Index('ix_ticket_events_ticket_id', 'ticket_id'),
        Index('ix_ticket_events_user_id', 'user_id'),
        Index('ix_ticket_events_event_type', 'event_type'),
        Index('ix_ticket_events_created_at', 'created_at'),
    )
