from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID as PyUUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.epic import Epic
    from app.models.subtask import Subtask
    from app.models.ticket_event import TicketEvent
    from app.models.user import User


from .base import Base, BaseEntity


class TicketStatus(str, Enum):
    # Workflow de desarrollo
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    BLOCKED_QUESTION = "BLOCKED_QUESTION"
    REDIRECTED = "REDIRECTED"
    COMPLETED = "COMPLETED"
    # Workflow de soporte
    REPORTED = "REPORTED"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"


class TicketPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class TicketType(str, Enum):
    DEVELOPMENT = "DEVELOPMENT"
    SUPPORT = "SUPPORT"


class SupportSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Ticket(Base, BaseEntity):
    __tablename__ = "tickets"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(3000), nullable=True)
    status: Mapped[TicketStatus] = mapped_column(
        SQLEnum(TicketStatus, name="ticket_status_enum"),
        default=TicketStatus.TODO,
        nullable=False,
        index=True,
    )
    priority: Mapped[TicketPriority] = mapped_column(
        SQLEnum(TicketPriority, name="ticket_priority_enum"),
        default=TicketPriority.MEDIUM,
        nullable=False,
        index=True,
    )
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    pr_link: Mapped[str | None] = mapped_column(String(512), nullable=True)
    time_spent_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    blocked_time_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Nuevos campos para soportar el Wireframe del Frontend
    block_reason: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    blocked_question: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    blocked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    estimated_time_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    timer_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Campos específicos de tickets de soporte (null para tickets de desarrollo)
    ticket_type: Mapped[TicketType] = mapped_column(
        SQLEnum(TicketType, name="ticket_type_enum"),
        default=TicketType.DEVELOPMENT,
        nullable=False,
        index=True,
    )
    stack_trace: Mapped[str | None] = mapped_column(Text, nullable=True)
    reproduction_steps: Mapped[str | None] = mapped_column(Text, nullable=True)
    browser: Mapped[str | None] = mapped_column(String(100), nullable=True)
    operating_system: Mapped[str | None] = mapped_column(String(100), nullable=True)
    severity: Mapped[SupportSeverity | None] = mapped_column(
        SQLEnum(SupportSeverity, name="support_severity_enum"),
        nullable=True,
    )
    linked_ticket_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tickets.id", ondelete="SET NULL"),
        nullable=True,
    )

    epic_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("epics.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    assignee_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_by_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    epic: Mapped["Epic | None"] = relationship(lazy="raise_on_sql", back_populates="tickets")
    linked_ticket: Mapped["Ticket | None"] = relationship(
        "Ticket",
        foreign_keys=[linked_ticket_id],
        remote_side="Ticket.id",
        lazy="raise_on_sql",
    )
    assignee: Mapped["User | None"] = relationship(
        lazy="raise_on_sql",
        back_populates="assigned_tickets",
        foreign_keys=[assignee_id],
    )
    created_by: Mapped["User | None"] = relationship(
        lazy="raise_on_sql",
        back_populates="created_tickets",
        foreign_keys=[created_by_id],
    )

    subtasks: Mapped[list["Subtask"]] = relationship(
        lazy="raise_on_sql",
        back_populates="ticket",
        cascade="all, delete-orphan",
    )
    events: Mapped[list["TicketEvent"]] = relationship(
        lazy="raise_on_sql",
        back_populates="ticket",
        cascade="all, delete-orphan",
    )
    documents: Mapped[list["Document"]] = relationship(
        lazy="raise_on_sql",
        back_populates="ticket",
        cascade="all, delete-orphan",
        foreign_keys="Document.ticket_id",
    )

    @property
    def epic_title(self) -> str | None:
        return self.epic.title if self.epic else None

    @property
    def app_name(self) -> str | None:
        if self.epic and self.epic.application:
            return self.epic.application.name
        return None

    @property
    def linked_ticket_title(self) -> str | None:
        return self.linked_ticket.title if self.linked_ticket else None

    @property
    def origin_epic_title(self) -> str | None:
        if self.linked_ticket and self.linked_ticket.epic:
            return self.linked_ticket.epic.title
        return None
