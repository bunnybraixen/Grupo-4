from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any
from uuid import UUID as PyUUID

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.ticket import Ticket
    from app.models.user import User


from .base import Base, BaseEntity


class TicketEventType(str, Enum):
    CREATED = "CREATED"
    ASSIGNED = "ASSIGNED"
    TICKET_ASSIGNED = "TICKET_ASSIGNED"
    STATUS_CHANGED = "STATUS_CHANGED"
    QUESTION_RAISED = "QUESTION_RAISED"
    QUESTION_RESOLVED = "QUESTION_RESOLVED"
    REDIRECTED = "REDIRECTED"
    COMPLETED = "COMPLETED"
    COMMENT = "COMMENT"
    TIMER_START = "TIMER_START"
    TIMER_PAUSE = "TIMER_PAUSE"
    TIMER_SYNC = "TIMER_SYNC"
    SUBTASK_CREATED = "SUBTASK_CREATED"
    SUBTASK_COMPLETED = "SUBTASK_COMPLETED"
    SUBTASK_DELETED = "SUBTASK_DELETED"
    UPDATED = "UPDATED"
    MOVED = "MOVED"


class TicketEvent(Base, BaseEntity):
    __tablename__ = "ticket_events"

    ticket_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    event_type: Mapped[TicketEventType] = mapped_column(
        SQLEnum(TicketEventType, name="ticket_event_type_enum"),
        nullable=False,
        index=True,
    )
    detail: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    from_user_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    to_user_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    ticket: Mapped["Ticket"] = relationship(lazy="raise_on_sql", back_populates="events")
    user: Mapped["User | None"] = relationship(
        lazy="raise_on_sql",
        back_populates="events",
        foreign_keys=[user_id],
    )
    from_user: Mapped["User | None"] = relationship(lazy="raise_on_sql", foreign_keys=[from_user_id])
    to_user: Mapped["User | None"] = relationship(lazy="raise_on_sql", foreign_keys=[to_user_id])
