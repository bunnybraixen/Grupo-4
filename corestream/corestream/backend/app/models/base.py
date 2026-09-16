"""
Modelo base para todas las entidades de CoreStream.
Define la configuración común y tipos de datos base para los modelos SQLAlchemy.
"""

from datetime import datetime
from uuid import uuid4
from sqlalchemy import func
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from typing import UUID as PyUUID

# Base declarativa para todos los modelos
Base = declarative_base()


class BaseEntity:
    """
    Clase base que proporciona campos comunes a todas las entidades del sistema.
    
    Atributos:
        id: Identificador único en formato UUID para cada entidad
        created_at: Marca de tiempo de creación de la entidad
        updated_at: Marca de tiempo de última actualización de la entidad
    """
    
    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False,
        doc="Identificador único universal (UUID) de la entidad"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        nullable=False,
        index=True,
        doc="Fecha y hora de creación de la entidad en formato UTC"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Fecha y hora de la última actualización de la entidad en formato UTC"
    )
