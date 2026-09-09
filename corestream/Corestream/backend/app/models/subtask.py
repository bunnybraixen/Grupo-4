from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID as PyUUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.ticket import Ticket

from .base import Base, BaseEntity


class Subtask(Base, BaseEntity):
    __tablename__ = "subtasks"

    # Campos básicos del checklist
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    # Para mantener el orden en el que se crearon o si el frontend hace drag & drop
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Llave foránea hacia el Ticket
    ticket_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    ticket: Mapped["Ticket"] = relationship(lazy="raise_on_sql", back_populates="subtasks")
