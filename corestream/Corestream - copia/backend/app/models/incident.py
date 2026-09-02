"""
Módulo de modelos SQLAlchemy para el sistema de gestión de incidentes.

Este módulo define las estructuras de datos para tickets de incidentes, incluyendo
categorización, estado, severidad y seguimiento de comentarios. Implementa relaciones
con usuarios y aplicaciones, junto con índices de base de datos para optimización de consultas.

Autor: CoreStream Development Team
Fecha: 2026
"""

from datetime import datetime, date
from enum import Enum
from typing import Optional, List
from uuid import uuid4

from sqlalchemy import (
    Column, String, Text, ForeignKey, Integer, DateTime, Date,
    Enum as SQLEnum, Index, text, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, mapped_column, DeclarativeBase, Session

from app.core.database import Base


class IncidentCategory(str, Enum):
    """
    Enumeración de categorías de incidentes disponibles en el sistema.

    Categorías:
    - NEW_FEATURE: Solicitudes de nuevas funcionalidades
    - CRITICAL_ERROR: Errores que impiden el funcionamiento crítico
    - NON_CRITICAL_ERROR: Errores menores que no afectan funcionalidad esencial
    - USABILITY_ISSUE: Problemas relacionados con experiencia de usuario
    """
    NEW_FEATURE = "NEW_FEATURE"
    CRITICAL_ERROR = "CRITICAL_ERROR"
    NON_CRITICAL_ERROR = "NON_CRITICAL_ERROR"
    USABILITY_ISSUE = "USABILITY_ISSUE"


class IncidentStatus(str, Enum):
    """
    Enumeración de estados de incidentes durante su ciclo de vida.

    Estados:
    - OPEN: Incidente abierto y sin asignar
    - IN_PROGRESS: Activamente siendo tratado
    - UNDER_REVIEW: Pendiente de revisión antes de resolución
    - RESOLVED: Resuelto pero no cerrado definitivamente
    - CLOSED: Cerrado definitivamente
    - REOPENED: Reabierto después de cierre
    """
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    UNDER_REVIEW = "UNDER_REVIEW"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    REOPENED = "REOPENED"


class IncidentSeverity(str, Enum):
    """
    Enumeración de niveles de severidad para incidentes.

    Niveles:
    - CRITICAL: Afecta a producción, múltiples usuarios o datos críticos
    - HIGH: Afecta funcionalidad importante pero tiene alternativas
    - MEDIUM: Impacto moderado en funcionalidad o experiencia
    - LOW: Impacto mínimo, principalmente cosméticos o mejoras
    """
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Incident(Base):
    """
    Modelo SQLAlchemy que representa un ticket de incidente en el sistema.

    Almacena información completa sobre incidentes reportados, incluyendo:
    - Detalles del problema (título, descripción, categoría, severidad)
    - Seguimiento (estado, asignado a, prioridad)
    - Información técnica (versión afectada, pasos para reproducir, etc.)
    - Auditoría temporal (fechas de creación, actualización, resolución)

    Mantiene relaciones con:
    - usuarios (reportero, asignado)
    - aplicaciones (proyecto asociado)
    - comentarios (discusión del incidente)
    """

    __tablename__ = "incidents"

    # Campo identificador único
    id: str = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
        doc="Identificador único del incidente (UUID)"
    )

    # Información principal del incidente
    title: str = mapped_column(
        String(255),
        nullable=False,
        doc="Título descriptivo del incidente"
    )

    description: str = mapped_column(
        Text,
        nullable=False,
        doc="Descripción detallada del incidente y su contexto"
    )

    # Referencia a aplicación/proyecto
    application_id: str = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        doc="Identificador de la aplicación/proyecto afectado"
    )

    # Clasificación del incidente
    category: IncidentCategory = mapped_column(
        SQLEnum(IncidentCategory),
        nullable=False,
        doc="Categoría del incidente (NUEVA_FEATURE, ERROR_CRÍTICO, etc.)"
    )

    # Estado del incidente
    status: IncidentStatus = mapped_column(
        SQLEnum(IncidentStatus),
        nullable=False,
        default=IncidentStatus.OPEN,
        doc="Estado actual del incidente en su ciclo de vida"
    )

    # Nivel de severidad
    severity: IncidentSeverity = mapped_column(
        SQLEnum(IncidentSeverity),
        nullable=False,
        default=IncidentSeverity.MEDIUM,
        doc="Nivel de severidad del incidente (CRÍTICO, ALTO, MEDIO, BAJO)"
    )

    # Prioridad y asignación
    priority_order: int = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Orden de prioridad para ordenamiento visual (0=mayor prioridad)"
    )

    assignee_id: Optional[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        doc="ID del usuario asignado para resolver el incidente"
    )

    # Información del reportero
    reporter_id: str = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        doc="ID del usuario que reportó el incidente"
    )

    # Resolución y cierre
    resolution_notes: Optional[str] = mapped_column(
        Text,
        nullable=True,
        doc="Notas técnicas sobre cómo fue resuelto el incidente"
    )

    # Información del entorno afectado
    environment: Optional[str] = mapped_column(
        String(50),
        nullable=True,
        doc="Entorno afectado (PRODUCCIÓN, STAGING, DESARROLLO, etc.)"
    )

    # Información técnica para reproducción
    steps_to_reproduce: Optional[str] = mapped_column(
        Text,
        nullable=True,
        doc="Pasos detallados para reproducir el incidente"
    )

    expected_behavior: Optional[str] = mapped_column(
        Text,
        nullable=True,
        doc="Comportamiento esperado o deseado del sistema"
    )

    actual_behavior: Optional[str] = mapped_column(
        Text,
        nullable=True,
        doc="Comportamiento actual o incorrecto observado"
    )

    # Información de versiones
    affected_version: Optional[str] = mapped_column(
        String(50),
        nullable=True,
        doc="Versión de la aplicación afectada por el incidente"
    )

    fixed_in_version: Optional[str] = mapped_column(
        String(50),
        nullable=True,
        doc="Versión en la que se corrigió el incidente"
    )

    # Fechas importantes
    due_date: Optional[date] = mapped_column(
        Date,
        nullable=True,
        doc="Fecha de vencimiento para la resolución del incidente"
    )

    resolved_at: Optional[datetime] = mapped_column(
        DateTime,
        nullable=True,
        doc="Fecha y hora de resolución del incidente"
    )

    closed_at: Optional[datetime] = mapped_column(
        DateTime,
        nullable=True,
        doc="Fecha y hora de cierre definitivo del incidente"
    )

    # Auditoría temporal
    created_at: datetime = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        doc="Fecha y hora de creación del incidente"
    )

    updated_at: datetime = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        doc="Fecha y hora de última actualización del incidente"
    )

    # Relaciones con otras entidades
    assignee = relationship(
        "User",
        foreign_keys=[assignee_id],
        backref="assigned_incidents",
        doc="Relación con el usuario asignado al incidente"
    )

    reporter = relationship(
        "User",
        foreign_keys=[reporter_id],
        backref="reported_incidents",
        doc="Relación con el usuario que reportó el incidente"
    )

    application = relationship(
        "Application",
        backref="incidents",
        doc="Relación con la aplicación/proyecto afectado"
    )

    comments = relationship(
        "IncidentComment",
        backref="incident",
        cascade="all, delete-orphan",
        lazy="selectin",
        doc="Relación con los comentarios del incidente"
    )

    # Definición de índices para optimización de consultas
    __table_args__ = (
        # Índice compuesto para filtrado por categoría
        Index(
            "idx_incident_category",
            "category",
            doc="Índice para búsquedas rápidas por categoría"
        ),
        # Índice compuesto para filtrado por estado
        Index(
            "idx_incident_status",
            "status",
            doc="Índice para búsquedas rápidas por estado"
        ),
        # Índice compuesto para filtrado por severidad
        Index(
            "idx_incident_severity",
            "severity",
            doc="Índice para búsquedas rápidas por severidad"
        ),
        # Índice para búsquedas por asignado
        Index(
            "idx_incident_assignee_id",
            "assignee_id",
            doc="Índice para listar incidentes por persona asignada"
        ),
        # Índice para búsquedas por aplicación
        Index(
            "idx_incident_application_id",
            "application_id",
            doc="Índice para listar incidentes por aplicación"
        ),
        # Índice compuesto para listados típicos
        Index(
            "idx_incident_status_priority",
            "status",
            "priority_order",
            doc="Índice para listados ordenados por estado y prioridad"
        ),
        # Índice para búsquedas por reporter
        Index(
            "idx_incident_reporter_id",
            "reporter_id",
            doc="Índice para listar incidentes reportados por usuario"
        ),
    )

    def __repr__(self) -> str:
        """Representación en string del objeto Incident."""
        return f"<Incident(id={self.id}, title='{self.title}', status={self.status.value})>"

    def is_overdue(self) -> bool:
        """
        Determina si el incidente está vencido (pasó la fecha de vencimiento).

        Retorna:
            bool: True si tiene due_date y es menor a hoy, False en caso contrario
        """
        if self.due_date is None:
            return False
        return self.due_date < date.today()

    def days_open(self) -> int:
        """
        Calcula los días que el incidente ha estado abierto.

        Retorna:
            int: Número de días desde creación hasta hoy (o fecha de cierre)
        """
        end_date = self.closed_at or self.resolved_at or datetime.utcnow()
        return (end_date - self.created_at).days


class IncidentComment(Base):
    """
    Modelo SQLAlchemy que representa un comentario en un incidente.

    Permite a los usuarios participantes en la resolución del incidente
    agregar comentarios, notas y actualizaciones sobre el progreso.
    Mantiene relación con el incidente y el usuario que comenta.
    """

    __tablename__ = "incident_comments"

    # Campo identificador único
    id: str = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
        doc="Identificador único del comentario (UUID)"
    )

    # Referencia al incidente
    incident_id: str = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        doc="Identificador del incidente al que pertenece el comentario"
    )

    # Referencia al usuario comentarista
    user_id: str = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        doc="Identificador del usuario que escribió el comentario"
    )

    # Contenido del comentario
    content: str = mapped_column(
        Text,
        nullable=False,
        doc="Contenido del comentario o nota sobre el incidente"
    )

    # Auditoría temporal
    created_at: datetime = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        doc="Fecha y hora de creación del comentario"
    )

    # Relación con usuario comentarista
    user = relationship(
        "User",
        backref="incident_comments",
        doc="Relación con el usuario que escribió el comentario"
    )

    # Índices para optimización
    __table_args__ = (
        # Índice para búsquedas rápidas por incidente
        Index(
            "idx_incident_comment_incident_id",
            "incident_id",
            doc="Índice para obtener comentarios de un incidente"
        ),
        # Índice para listar comentarios por usuario
        Index(
            "idx_incident_comment_user_id",
            "user_id",
            doc="Índice para listar comentarios de un usuario"
        ),
        # Índice temporal para ordenamiento
        Index(
            "idx_incident_comment_created_at",
            "created_at",
            doc="Índice para ordenar comentarios cronológicamente"
        ),
    )

    def __repr__(self) -> str:
        """Representación en string del objeto IncidentComment."""
        return f"<IncidentComment(id={self.id}, incident_id={self.incident_id})>"
