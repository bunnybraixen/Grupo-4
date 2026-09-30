"""
Modelo de Ticket para CoreStream.
Define la estructura de los tickets que representan tareas dentro de un épico.
Los tickets incluyen seguimiento de estado, asignaciones, prioridades y tiempo.
"""

from datetime import datetime
from enum import Enum
from uuid import UUID as PyUUID
from sqlalchemy import String, Integer, DateTime, ForeignKey, Index, inspect as sa_inspect
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM

from .base import Base, BaseEntity


class TicketStatus(str, Enum):
    """
    Enumeración de estados posibles de un ticket en CoreStream.
    
    Estados:
        TODO: Ticket no iniciado, pendiente de asignación o inicio
        IN_PROGRESS: Ticket actualmente en desarrollo/resolución
        BLOCKED: Ticket bloqueado por dependencias o restricciones externas
        REDIRECTED: Ticket redirigido a otro usuario o equipo
        DONE: Ticket completado y listo para revisión/despliegue
    """
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    REDIRECTED = "REDIRECTED"
    DONE = "DONE"


class TicketPriority(str, Enum):
    """
    Enumeración de niveles de prioridad para tickets en CoreStream.
    
    Prioridades:
        LOW: Prioridad baja, trabajo no urgente
        MEDIUM: Prioridad media, trabajo regular
        HIGH: Prioridad alta, trabajo importante
        URGENT: Prioridad urgente, requiere atención inmediata
    """
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class Ticket(Base, BaseEntity):
    """
    Entidad que representa un Ticket en CoreStream.
    
    Un Ticket es una unidad de trabajo dentro de un Épico.
    Puede tener Subtareas, seguimiento de tiempo, y eventos de cambio de estado.
    
    Atributos principales:
        title: Título descriptivo del ticket
        description: Descripción detallada de los requisitos y alcance
        epic_id: Referencia al épico contenedor
        assignee_id: Usuario asignado al ticket (puede estar sin asignar)
        status: Estado actual del ticket (máquina de estados)
        priority: Nivel de prioridad del ticket
        order_index: Índice para reordenamiento mediante drag-and-drop
        due_date: Fecha límite de completitud
        pr_link: Enlace al pull request/merge request asociado
        time_spent_seconds: Tiempo total gastado en el ticket
        blocked_time_seconds: Tiempo que el ticket ha estado bloqueado
        created_by_id: Usuario que creó el ticket
    
    Relaciones:
        epic: Épico contenedor del ticket
        assignee: Usuario asignado al ticket
        created_by: Usuario que creó el ticket
        subtasks: Lista de subtareas del ticket
        events: Lista de eventos de auditoría del ticket
    
    Índices:
        epic_id: Búsqueda rápida de tickets por épico
        assignee_id: Búsqueda de tickets asignados a usuario
        status: Filtrado por estado
        created_by_id: Búsqueda de tickets creados por usuario
    """
    
    __tablename__ = "tickets"
    
    # Título descriptivo del ticket
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Título descriptivo que resume la tarea del ticket"
    )
    
    # Descripción detallada de requisitos, contexto y aceptación
    description: Mapped[str | None] = mapped_column(
        String(3000),
        nullable=True,
        doc="Descripción detallada de requisitos, criterios de aceptación y contexto"
    )
    
    # Clave foránea al épico contenedor
    epic_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("epics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Referencia al épico contenedor de este ticket"
    )
    
    # Clave foránea al usuario asignado (puede ser NULL)
    assignee_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="Referencia al usuario asignado para resolver este ticket"
    )
    
    # Estado actual del ticket en la máquina de estados
    status: Mapped[TicketStatus] = mapped_column(
        ENUM(TicketStatus, name="ticket_status_enum"),
        default=TicketStatus.TODO,
        nullable=False,
        index=True,
        doc="Estado actual del ticket: TODO, IN_PROGRESS, BLOCKED, REDIRECTED, DONE"
    )
    
    # Nivel de prioridad del ticket
    priority: Mapped[TicketPriority] = mapped_column(
        ENUM(TicketPriority, name="ticket_priority_enum"),
        default=TicketPriority.MEDIUM,
        nullable=False,
        doc="Nivel de prioridad: LOW, MEDIUM, HIGH, URGENT"
    )
    
    # Índice de orden para reordenamiento mediante drag-and-drop
    order_index: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Índice de orden del ticket para reordenamiento tipo drag-and-drop"
    )
    
    # Fecha límite de completitud del ticket
    due_date: Mapped[datetime | None] = mapped_column(
        nullable=True,
        doc="Fecha límite de completitud del ticket"
    )
    
    # Enlace al pull request o merge request asociado
    pr_link: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        doc="URL del pull request o merge request asociado con este ticket"
    )
    
    # Tiempo total gastado en el ticket en segundos
    time_spent_seconds: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Tiempo total gastado en el ticket, acumulado en segundos"
    )
    
    # Tiempo que el ticket ha estado bloqueado en segundos
    blocked_time_seconds: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Tiempo acumulado que el ticket ha estado en estado BLOCKED, en segundos"
    )
    
    # Clave foránea al usuario que creó el ticket
    created_by_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="Referencia al usuario que creó originalmente este ticket"
    )

    # PLANIFICACIÓN: Sprint al que está asociado el ticket (dimensión temporal).
    # Es INDEPENDIENTE de `epic_id` (dimensión funcional): un ticket puede
    # pertenecer a la vez a una Épica y a un Sprint, o solo a la Épica.
    sprint_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sprints.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="Referencia al Sprint en el que se planificó el ticket (opcional)"
    )

    # Esfuerzo del ticket en puntos de historia (alimenta la Velocity del Sprint)
    story_points: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Puntos de historia/esfuerzo del ticket, usados para calcular Velocity"
    )

    # SLA: momento en que se dio la primera respuesta (salida de TODO, comentario
    # o redirección). Con esto el SLA de respuesta se puede medir y cerrar; si es
    # NULL, el ticket sigue esperando su primera respuesta.
    first_response_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Momento de la primera respuesta al ticket (base del SLA de respuesta)"
    )

    # Relaciones hacia otras entidades
    
    epic = relationship(
        "Epic",
        back_populates="tickets",
        foreign_keys=[epic_id],
        doc="Épico contenedor de este ticket"
    )

    sprint = relationship(
        "Sprint",
        back_populates="tickets",
        foreign_keys=[sprint_id],
        doc="Sprint (período de trabajo) en el que se planificó este ticket"
    )
    
    assignee = relationship(
        "User",
        back_populates="assigned_tickets",
        foreign_keys=[assignee_id],
        doc="Usuario asignado a este ticket"
    )
    
    created_by = relationship(
        "User",
        back_populates="created_tickets",
        foreign_keys=[created_by_id],
        doc="Usuario que creó este ticket"
    )
    
    subtasks = relationship(
        "Subtask",
        back_populates="ticket",
        cascade="all, delete-orphan",
        doc="Lista de subtareas pertenecientes a este ticket"
    )
    
    events = relationship(
        "TicketEvent",
        back_populates="ticket",
        cascade="all, delete-orphan",
        doc="Lista de eventos de auditoría del ticket"
    )

    comments = relationship(
        "TicketComment",
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="TicketComment.created_at",
        doc="Lista de comentarios realizados sobre este ticket",
    )

    tags = relationship("Tag", secondary="ticket_tags", back_populates="tickets")

    def _loaded_relation(self, name: str):
        """
        Devuelve una relación SOLO si ya fue precargada (selectinload).

        Acceder a una relación lazy en un contexto async dispara un lazy-load
        fuera de greenlet (MissingGreenlet -> HTTP 500). Estos helpers prefieren
        devolver None antes que provocar esa carga implícita.
        """
        try:
            state = sa_inspect(self)
        except Exception:  # pragma: no cover - objeto transitorio
            return None
        if name in state.unloaded:
            return None
        return self.__dict__.get(name)

    @property
    def epic_title(self) -> str | None:
        """Título de la Épica (dimensión funcional del ticket), si está cargada."""
        epic = self._loaded_relation("epic")
        return getattr(epic, "title", None)

    @property
    def sprint_name(self) -> str | None:
        """Nombre del Sprint (dimensión temporal del ticket), si está cargado."""
        sprint = self._loaded_relation("sprint")
        return getattr(sprint, "name", None)

    __table_args__ = (
    )
