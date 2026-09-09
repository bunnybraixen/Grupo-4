from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID as PyUUID

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.user import User

from .base import Base, BaseEntity


class MeetingType(str, Enum):
    DAILY = "DAILY"
    PLANNING = "PLANNING"
    RETROSPECTIVE = "RETROSPECTIVE"
    OTHER = "OTHER"

class AttendanceStatus(str, Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    JUSTIFIED = "JUSTIFIED"

class Meeting(Base, BaseEntity):
    __tablename__ = "meetings"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    meeting_type: Mapped[MeetingType] = mapped_column(
        SQLEnum(MeetingType, name="meeting_type_enum"),
        default=MeetingType.OTHER,
        nullable=False,
        index=True,
    )
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    summary_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)

    application_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    created_by_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    application: Mapped["Application | None"] = relationship(lazy="raise_on_sql", foreign_keys=[application_id])
    created_by: Mapped["User | None"] = relationship(lazy="raise_on_sql", foreign_keys=[created_by_id])
    
    attendances: Mapped[list["MeetingAttendance"]] = relationship(
        lazy="raise_on_sql",
        back_populates="meeting",
        cascade="all, delete-orphan",
    )


class MeetingAttendance(Base, BaseEntity):
    __tablename__ = "meeting_attendances"

    meeting_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[AttendanceStatus] = mapped_column(
        SQLEnum(AttendanceStatus, name="attendance_status_enum"),
        default=AttendanceStatus.PRESENT,
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    meeting: Mapped["Meeting"] = relationship(lazy="raise_on_sql", back_populates="attendances")
    user: Mapped["User"] = relationship(lazy="raise_on_sql")
