"""
Modelo de Aplicación para CoreStream.
Define la estructura de las aplicaciones que son el nivel superior en la jerarquía
de organización de proyectos (Application > Epic > Ticket > Subtask).
"""

from datetime import datetime
from uuid import UUID as PyUUID
from sqlalchemy import String, Boolean, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import Base, BaseEntity


class Application(Base, BaseEntity):
    """
    Entidad que representa una Aplicación en CoreStream.
    
    Una Aplicación es el nivel superior en la jerarquía de organización de proyectos.
    Agrupa múltiples Épicos que contienen Tickets que a su vez contienen Subtareas.
    
    Atributos principales:
        name: Nombre identificativo de la aplicación
        description: Descripción detallada del propósito de la aplicación
        color: Código de color hexadecimal para identificación visual
        icon: Identificador o URL del icono representativo de la aplicación
        is_active: Indicador si la aplicación está activa en el sistema
        owner_id: Referencia al usuario propietario de la aplicación
    
    Relaciones:
        owner: Usuario propietario de la aplicación
        epics: Lista de épicos pertenecientes a esta aplicación
    
    Índices:
        owner_id: Índice para búsquedas rápidas por propietario
        is_active: Índice para filtrado de aplicaciones activas
    """
    
    __tablename__ = "applications"
    
    # Nombre de la aplicación utilizado para identificación visual
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Nombre único y descriptivo de la aplicación"
    )
    
    # Descripción detallada del propósito y alcance de la aplicación
    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
        doc="Descripción detallada del propósito y funcionalidad de la aplicación"
    )
    
    # Código de color hexadecimal para identificación visual en la interfaz
    color: Mapped[str | None] = mapped_column(
        String(7),
        nullable=True,
        doc="Código de color hexadecimal (ej: #FF5733) para identificación visual"
    )
    
    # Identificador del icono de la aplicación
    icon: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        doc="Identificador o nombre del icono que representa la aplicación"
    )
    
    # Indicador si la aplicación está activa
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        doc="Indicador si la aplicación está activa y visible en el sistema"
    )
    
    # Clave foránea al usuario propietario
    owner_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="Referencia al usuario propietario de la aplicación"
    )
    
    # Relaciones hacia otras entidades
    
    owner = relationship(
        "User",
        back_populates="owned_applications",
        foreign_keys=[owner_id],
        doc="Usuario propietario de esta aplicación"
    )
    
    epics = relationship(
        "Epic",
        back_populates="application",
        cascade="all, delete-orphan",
        doc="Lista de épicos pertenecientes a esta aplicación"
    )
    
    __table_args__ = (
        Index('ix_applications_owner_id', 'owner_id'),
        Index('ix_applications_is_active', 'is_active'),
    )
