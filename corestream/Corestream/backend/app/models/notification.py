from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID as PyUUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, BaseEntity

if TYPE_CHECKING:
    # Solo para anotaciones: en runtime SQLAlchemy resuelve estas relaciones
    # desde su registro, por eso van como cadenas.
    from .ticket import Ticket
    from .user import User


class NotificationType(str, Enum):
    TICKET_ASSIGNED   = "TICKET_ASSIGNED"
    STATUS_CHANGED    = "STATUS_CHANGED"
    TICKET_REDIRECTED = "TICKET_REDIRECTED"
    TICKET_COMPLETED  = "TICKET_COMPLETED"
    QUESTION_RAISED   = "QUESTION_RAISED"
    SYSTEM            = "SYSTEM"


class Notification(Base, BaseEntity):
    __tablename__ = "notifications"

    user_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ticket_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tickets.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    type: Mapped[NotificationType] = mapped_column(
        SQLEnum(NotificationType, name="notification_type_enum"),
        nullable=False,
    )
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    user: Mapped["User"] = relationship(lazy="raise_on_sql", back_populates="notifications")  # type: ignore[name-defined]
    ticket: Mapped["Ticket | None"] = relationship(lazy="raise_on_sql")  # type: ignore[name-defined]
