from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID as PyUUID

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.epic import Epic
    from app.models.ticket import Ticket
    from app.models.user import User

from .base import Base, BaseEntity


class DocumentType(str, Enum):
    CODE = "CODE"
    DOCUMENTATION = "DOCUMENTATION"


class Document(Base, BaseEntity):
    __tablename__ = "documents"

    __table_args__ = (
        CheckConstraint(
            "(epic_id IS NOT NULL) OR (ticket_id IS NOT NULL)",
            name="ck_documents_has_target",
        ),
    )

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    doc_type: Mapped[DocumentType] = mapped_column(
        SQLEnum(DocumentType, name="document_type_enum"),
        default=DocumentType.DOCUMENTATION,
        nullable=False,
    )

    epic_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("epics.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    ticket_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    uploaded_by_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    epic: Mapped["Epic | None"] = relationship(lazy="raise_on_sql", back_populates="documents", foreign_keys=[epic_id])
    ticket: Mapped["Ticket | None"] = relationship(lazy="raise_on_sql", back_populates="documents", foreign_keys=[ticket_id])
    uploaded_by: Mapped["User | None"] = relationship(lazy="raise_on_sql", back_populates="uploaded_documents")
