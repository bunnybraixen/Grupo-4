"""
Modelo de Sprint para CoreStream.

Un Sprint es un ELEMENTO DE PLANIFICACIÓN INDEPENDIENTE de la Épica:

    - Épica    -> área funcional / conjunto de trabajo del proyecto
    - Sprint   -> período de trabajo (fechas de inicio y término)
    - Ticket   -> unidad de trabajo que pertenece SIMULTÁNEAMENTE a una Épica
                  (`epic_id`) y, opcionalmente, a un Sprint (`sprint_id`).

Agregar `sprint_id` a Ticket NO modifica la relación existente Épica -> Ticket:
solo añade una segunda dimensión de agrupación temporal para planificar y medir
Velocity.
"""

from datetime import datetime
from enum import Enum
from uuid import UUID as PyUUID

from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM

from .base import Base, BaseEntity


class SprintStatus(str, Enum):
    """
    Enumeración de estados del ciclo de vida de un Sprint.

    Estados:
        PLANNED: Sprint creado pero todavía no iniciado
        ACTIVE: Sprint en curso (período de trabajo en ejecución)
        COMPLETED: Sprint cerrado; su Velocity ya fue calculada
    """

    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"


class Sprint(Base, BaseEntity):
    """
    Entidad que representa un Sprint en CoreStream.

    Atributos principales:
        name: Nombre identificatorio del Sprint (ej: "Sprint 12")
        goal: Objetivo/metas del Sprint (opcional)
        application_id: Proyecto (aplicación) al que pertenece el Sprint
        start_date: Fecha de inicio del período de trabajo
        end_date: Fecha de término del período de trabajo
        status: Estado del Sprint (PLANNED, ACTIVE, COMPLETED)
        velocity: Velocity calculada al finalizar (puntos de los tickets DONE)
        created_by_id: Usuario que creó el Sprint

    Relaciones:
        application: Proyecto contenedor del Sprint
        tickets: Tickets asociados al Sprint (relación adicional a epic_id)
    """

    __tablename__ = "sprints"

    # Nombre identificatorio del Sprint
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Nombre del Sprint, por ejemplo 'Sprint 12'",
    )

    # Objetivo o meta del Sprint
    goal: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
        doc="Objetivo/metas del período de trabajo",
    )

    # Proyecto (aplicación) al que pertenece el Sprint
    application_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Referencia al proyecto (aplicación) contenedor del Sprint",
    )

    # Fecha de inicio del período de trabajo
    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        doc="Fecha de inicio del Sprint",
    )

    # Fecha de término del período de trabajo
    end_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        doc="Fecha de término del Sprint",
    )

    # Estado del Sprint
    status: Mapped[SprintStatus] = mapped_column(
        ENUM(SprintStatus, name="sprint_status_enum"),
        default=SprintStatus.PLANNED,
        nullable=False,
        index=True,
        doc="Estado del Sprint: PLANNED, ACTIVE, COMPLETED",
    )

    # Velocity calculada automáticamente al finalizar el Sprint
    velocity: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
        doc="Velocity del Sprint: puntos/esfuerzo de los tickets completados al cierre",
    )

    # Autor del Sprint
    created_by_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="Referencia al usuario que creó el Sprint",
    )

    # Relaciones
    application = relationship(
        "Application",
        doc="Proyecto (aplicación) al que pertenece este Sprint",
    )

    tickets = relationship(
        "Ticket",
        back_populates="sprint",
        doc="Tickets asociados a este Sprint (planificación temporal)",
    )
