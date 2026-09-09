from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID as PyUUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Importamos la base necesaria para SQLAlchemy
from .base import Base, BaseEntity

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.document import Document
    from app.models.ticket import Ticket

class Epic(Base, BaseEntity):
    """
    Modelo de Base de Datos para las Épicas (CoreStream).
    
    CAMBIOS DE REFACCIÓN (Sprint 3):
    - Se eliminaron los esquemas Pydantic y Routers que estaban dentro de la clase (provocaban errores).
    - El código de la API ahora reside en app/routers/epics.py.
    - Los esquemas de validación ahora residen en app/schemas/epic.py.
    - Se agregaron campos críticos para CS-010 y CS-012.
    """
    __tablename__ = "epics"

    # ===================================================================
    # INFORMACIÓN DE LA ÉPICA
    # ===================================================================
    # Título descriptivo de la épica (requerido)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Descripción detallada del objetivo de la épica (opcional)
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    
    # CS-012: Índice para el ordenamiento por Drag & Drop
    # Permite reordenar la prioridad visualmente en la interfaz
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)
    
    # Fecha límite para completar la épica (opcional)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # CS-010: Estado de colapso para los swimlanes tipo accordion
    # Define si la épica se muestra abierta o cerrada en la UI
    is_collapsed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # ===================================================================
    # RELACIONES Y CLAVES FORÁNEAS
    # ===================================================================
    # UUID de la aplicación a la que pertenece la épica
    application_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relación inversa con la aplicación propietaria
    application: Mapped["Application"] = relationship(lazy="raise_on_sql", back_populates="epics")
    
    # Una épica contiene tickets que son los elementos de trabajo reales
    # Se eliminan en cascada si la épica desaparece.
    # order_by explícito: sin esto, Postgres no garantiza el orden de la
    # colección (puede cambiar tras cualquier UPDATE sobre un ticket), lo que
    # hacía que un ticket pareciera "moverse" o desaparecer de donde el
    # usuario lo esperaba después de editarlo.
    tickets: Mapped[list["Ticket"]] = relationship(
        lazy="raise_on_sql",
        back_populates="epic",
        cascade="all, delete-orphan",
        order_by="Ticket.order_index, Ticket.created_at",
    )
    
    # Documentos técnicos asociados a esta épica
    documents: Mapped[list["Document"]] = relationship(
        lazy="raise_on_sql",
        back_populates="epic",
        cascade="all, delete-orphan",
        foreign_keys="Document.epic_id",
    )
# =====================================================================
# Los esquemas de validación (EpicCreate, EpicUpdate) y los 
# endpoints (GET, POST, PATCH) han sido movidos a sus respectivos 
# módulos en /schemas y /routers para cumplir con la arquitectura 
# de software del proyecto.
# =====================================================================