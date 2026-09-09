from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID as PyUUID

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.epic import Epic
    from app.models.user import User

from .base import Base, BaseEntity


class Application(Base, BaseEntity):
    __tablename__ = "applications"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    owner_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    owner: Mapped["User | None"] = relationship(lazy="raise_on_sql", back_populates="owned_applications")
    epics: Mapped[list["Epic"]] = relationship(
        lazy="raise_on_sql",
        back_populates="application",
        cascade="all, delete-orphan",
    )
