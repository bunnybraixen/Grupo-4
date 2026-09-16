"""
Modelo de Épico para CoreStream.
Define la estructura de los épicos que agrupan tickets dentro de una aplicación.
Los épicos son el segundo nivel en la jerarquía (Application > Epic > Ticket > Subtask).
"""

from datetime import datetime
from uuid import UUID as PyUUID
from sqlalchemy import String, Boolean, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import Base, BaseEntity


class Epic(Base, BaseEntity):
    """
    Entidad que representa un Épico en CoreStream.
    
    Un Épico agrupa un conjunto de Tickets relacionados dentro de una Aplicación.
    Los épicos ayudan a organizar el trabajo en features o capas lógicas.
    
    Atributos principales:
        title: Título descriptivo del épico
        description: Descripción detallada del alcance del épico
        application_id: Referencia a la aplicación contenedora
        order_index: Índice de orden para soportar drag-and-drop
        due_date: Fecha límite de entrega del épico
        is_collapsed: Indicador si el épico está colapsado en la interfaz
    
    Relaciones:
        application: Aplicación contenedora del épico
        tickets: Lista de tickets pertenecientes al épico
        documents: Lista de documentos asociados al épico
    
    Índices:
        application_id: Índice para búsquedas rápidas de épicos por aplicación
        order_index: Índice para ordenamiento y paginación
    """
    
    __tablename__ = "epics"
    
    # Título descriptivo del épico
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Título descriptivo que identifica el propósito del épico"
    )
    
    # Descripción detallada del alcance y objetivos del épico
    description: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
        doc="Descripción detallada del alcance, objetivos y requisitos del épico"
    )
    
    # Clave foránea a la aplicación contenedora
    application_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Referencia a la aplicación contenedora de este épico"
    )
    
    # Índice de orden para soportar reordenamiento mediante drag-and-drop
    order_index: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        index=True,
        doc="Índice de orden del épico para reordenamiento tipo drag-and-drop"
    )
    
    # Fecha límite de entrega del épico
    due_date: Mapped[datetime | None] = mapped_column(
        nullable=True,
        doc="Fecha límite de entrega/completitud del épico"
    )
    
    # Indicador de colapso de la vista del épico en la interfaz
    is_collapsed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Indicador si el épico está colapsado en la vista de la interfaz"
    )
    
    # Relaciones hacia otras entidades
    
    application = relationship(
        "Application",
        back_populates="epics",
        foreign_keys=[application_id],
        doc="Aplicación contenedora de este épico"
    )
    
    tickets = relationship(
        "Ticket",
        back_populates="epic",
        cascade="all, delete-orphan",
        doc="Lista de tickets pertenecientes a este épico"
    )
    
    documents = relationship(
        "Document",
        back_populates="epic",
        cascade="all, delete-orphan",
        primaryjoin="Epic.id == Document.epic_id",
        foreign_keys="Document.epic_id",
        doc="Lista de documentos asociados a este épico"
    )
    
    __table_args__ = (
        Index('ix_epics_application_id', 'application_id'),
        Index('ix_epics_order_index', 'order_index'),
    )
