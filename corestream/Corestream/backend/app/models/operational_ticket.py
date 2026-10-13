"""
Tickets operacionales de Soporte.

Los levanta cualquier rol autenticado (ADMIN, GROUP_LEADER, DEVELOPER) con un
título y un problema. Al crearse arrancan con el timer corriendo
(`timer_started_at`); solo ADMIN/GROUP_LEADER pueden resolverlos, y para eso
deben indicar qué cambios se hicieron (`resolution_notes`). Al resolverse el
timer se congela en `elapsed_seconds` y el ticket pasa a la categoría de
archivados (status=RESOLVED), donde se pueden revisar sus detalles.
"""

from datetime import datetime, timezone
from enum import Enum
from uuid import UUID as PyUUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, BaseEntity


class OperationalTicketStatus(str, Enum):
    """OPEN = activo con timer corriendo. RESOLVED = resuelto y archivado."""

    OPEN = "OPEN"
    RESOLVED = "RESOLVED"


class OperationalTicket(Base, BaseEntity):
    __tablename__ = "operational_support_tickets"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    problem: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[OperationalTicketStatus] = mapped_column(
        ENUM(OperationalTicketStatus, name="operational_ticket_status"),
        default=OperationalTicketStatus.OPEN,
        nullable=False,
        index=True,
    )

    # Inicio del timer (siempre en la creación; se congela al resolver).
    timer_started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
    )
    # Momento en que se marcó como resuelto (NULL mientras está abierto).
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Duración congelada al resolver; mientras está abierto se calcula en vivo.
    # `server_default` cubre filas creadas por SQL directo (p. ej. la migración).
    elapsed_seconds: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )

    # Bloque de texto con los cambios que se hicieron para resolverlo.
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    resolved_by_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_by = relationship("User", foreign_keys=[created_by_id])
    resolved_by = relationship("User", foreign_keys=[resolved_by_id])

    @property
    def current_elapsed_seconds(self) -> int:
        """Segundos del timer: congelados si está resuelto, en vivo si no."""
        if self.status == OperationalTicketStatus.RESOLVED:
            return self.elapsed_seconds
        start = self.timer_started_at
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        return max(0, int((datetime.now(timezone.utc) - start).total_seconds()))

    def resolve(self, notes: str, user_id: PyUUID, now: datetime | None = None) -> None:
        """Marca el ticket como resuelto/archivado y detiene el timer."""
        now = now or datetime.now(timezone.utc)
        self.status = OperationalTicketStatus.RESOLVED
        self.resolution_notes = notes
        self.resolved_by_id = user_id
        self.resolved_at = now
        start = self.timer_started_at
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        self.elapsed_seconds = max(0, int((now - start).total_seconds()))
