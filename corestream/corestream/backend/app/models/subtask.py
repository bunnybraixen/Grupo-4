"""
Modelo de Subtarea para CoreStream.
Define la estructura de las subtareas que descomponen tickets en unidades más pequeñas.
Las subtareas son el nivel más bajo en la jerarquía (Application > Epic > Ticket > Subtask).
"""

from datetime import datetime
from uuid import UUID as PyUUID
from sqlalchemy import String, Boolean, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import Base, BaseEntity


class Subtask(Base, BaseEntity):
    """
    Entidad que representa una Subtarea en CoreStream.
    
    Una Subtarea es una unidad de trabajo más pequeña dentro de un Ticket.
    Las subtareas permiten descomponer tickets complejos en pasos más manejables.
    
    Atributos principales:
        title: Título descriptivo de la subtarea
        is_completed: Indicador si la subtarea está completada
        order_index: Índice para reordenamiento mediante drag-and-drop
        ticket_id: Referencia al ticket contenedor
        completed_at: Marca de tiempo de completitud (nullable)
    
    Relaciones:
        ticket: Ticket contenedor de esta subtarea
    
    Índices:
        ticket_id: Búsqueda rápida de subtareas por ticket
        is_completed: Filtrado de subtareas completadas
    """
    
    __tablename__ = "subtasks"
    
    # Título descriptivo de la subtarea
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Título descriptivo que resume la acción de la subtarea"
    )
    
    # Indicador de completitud de la subtarea
    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        doc="Indicador si la subtarea ha sido completada exitosamente"
    )
    
    # Índice de orden para reordenamiento mediante drag-and-drop
    order_index: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Índice de orden de la subtarea para reordenamiento tipo drag-and-drop"
    )
    
    # Clave foránea al ticket contenedor
    ticket_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Referencia al ticket que contiene esta subtarea"
    )
    
    # Marca de tiempo de completitud (NULL si no está completada)
    completed_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
        doc="Marca de tiempo del momento en que fue completada la subtarea"
    )
    
    # Relaciones hacia otras entidades
    
    ticket = relationship(
        "Ticket",
        back_populates="subtasks",
        foreign_keys=[ticket_id],
        doc="Ticket contenedor de esta subtarea"
    )
    
    __table_args__ = (
        Index('ix_subtasks_ticket_id', 'ticket_id'),
        Index('ix_subtasks_is_completed', 'is_completed'),
    )
