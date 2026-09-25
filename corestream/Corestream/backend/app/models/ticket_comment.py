from uuid import UUID as PyUUID

from sqlalchemy import ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, BaseEntity


class TicketComment(Base, BaseEntity):

    __tablename__ = "ticket_comments"

    ticket_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Ticket al que pertenece el comentario",
    )

    user_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        doc="Usuario que creó el comentario",
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Contenido del comentario",
    )

    ticket = relationship(
        "Ticket",
        back_populates="comments",
        foreign_keys=[ticket_id],
    )

    user = relationship(
        "User",
        back_populates="ticket_comments",
        foreign_keys=[user_id],
    )

    __table_args__ = (
        Index(
            "ix_ticket_comments_ticket_created",
            "ticket_id",
            "created_at",
        ),
    )