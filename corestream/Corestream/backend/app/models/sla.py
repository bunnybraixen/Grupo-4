"""
Modelo de configuración de SLA para CoreStream.

El SLA se define A NIVEL DE TICKET (no de Sprint): según la prioridad/severidad
del ticket y la configuración definida por el ADMIN, se determinan los tiempos
objetivo de:

    - Respuesta   (response_minutes): desde la creación hasta la primera acción
    - Resolución  (resolution_minutes): desde la creación hasta completarlo

El cálculo del tiempo transcurrido/restante y la detección de incumplimientos
vive en `app/services/sla_service.py`; este modelo solo persiste los objetivos.
"""

from uuid import UUID as PyUUID

from sqlalchemy import Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, ENUM

from .base import Base, BaseEntity
from .ticket import TicketPriority


class SLAConfig(Base, BaseEntity):
    """
    Configuración de tiempos objetivo de SLA para una prioridad de ticket.

    Atributos:
        priority: Prioridad/severidad del ticket (LOW, MEDIUM, HIGH, URGENT)
        response_minutes: Minutos objetivo para la primera respuesta
        resolution_minutes: Minutos objetivo para la resolución del ticket
        warn_threshold_percent: % del tiempo objetivo a partir del cual el
            ticket se considera "próximo a vencer" (alerta preventiva)
        is_active: Permite desactivar la regla sin borrarla
        updated_by_id: Último ADMIN que modificó la configuración
    """

    __tablename__ = "sla_configs"

    priority: Mapped[TicketPriority] = mapped_column(
        ENUM(TicketPriority, name="ticket_priority_enum"),
        nullable=False,
        unique=True,
        index=True,
        doc="Prioridad/severidad del ticket a la que aplica esta configuración",
    )

    response_minutes: Mapped[int] = mapped_column(
        Integer,
        default=240,
        nullable=False,
        doc="Minutos objetivo para dar la primera respuesta al ticket",
    )

    resolution_minutes: Mapped[int] = mapped_column(
        Integer,
        default=1440,
        nullable=False,
        doc="Minutos objetivo para resolver (completar) el ticket",
    )

    warn_threshold_percent: Mapped[int] = mapped_column(
        Integer,
        default=80,
        nullable=False,
        doc="Porcentaje del tiempo objetivo a partir del cual se alerta 'próximo a vencer'",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Indica si la regla de SLA está activa",
    )

    updated_by_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        doc="Último administrador que modificó esta configuración",
    )
